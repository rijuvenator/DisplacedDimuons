import ROOT as R
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Analysis.Selections as Selections
from DisplacedDimuons.Analysis.Constants import DIR_DD, DIR_WS, SIGNALS
from DisplacedDimuons.Analysis.Utilities import SPStr
import argparse

R.PyConfig.IgnoreCommandLineOptions = True

parser = argparse.ArgumentParser()
parser.add_argument('--signalpoints', dest='SIGNALPOINT', type=int, nargs=3  , help='the mH mX cTau tuple'         )
parser.add_argument('--develop'     , dest='DEVELOP'    , action='store_true', help='run test mode for 1000 events')
args = parser.parse_args()

if not args.SIGNALPOINT:
	SIGNALPOINTS = [(125, 20, 13)]
else:
	SIGNALPOINTS = [tuple(args.SIGNALPOINT)]

for sp in SIGNALPOINTS:
	f = R.TFile.Open(DIR_WS + 'simple_ntuple_{}.root'.format(SPStr(sp)))
	t = f.Get('SimpleNTupler/DDTree')

	Counters = {'Muon':{'IND':{}, 'CUM':{}, 'TOTAL':0}, 'Dimuon':{'IND':{}, 'CUM':{}, 'TOTAL':0}}
	for PREFIX in ('Muon', 'Dimuon'):
		for DTYPE, SUFFIX in zip(('IND', 'CUM'),('All', 'None')):
			Counters[PREFIX][DTYPE] = {key:0 for key in Selections.CutLists[PREFIX+'CutListPlus'+SUFFIX]}

	Primitives.SelectBranches(t, ('DSAMUON', 'GEN', 'DIMUON'))
	#Primitives.SelectBranches(t, ('DSAMUON', 'RSAMUON', 'GEN'))
	for i, event in enumerate(t):

		if args.DEVELOP:
			if i == 1000: break

		E = Primitives.ETree(t, ('DSAMUON', 'GEN', 'DIMUON'))
		#E = Primitives.ETree(t, ('DSAMUON', 'RSAMUON', 'GEN'))
		mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN')
		DSAmuons = E.getPrimitives('DSAMUON')
		#RSAmuons = E.getPrimitives('RSAMUON')
		Dimuons = E.getPrimitives('DIMUON')

		def matchedMuons(genMuon, recoMuons):
			matches = []
			for i,muon in enumerate(recoMuons):
				deltaR = muon.p4.DeltaR(genMuon.p4)
				if deltaR < 0.3:
					matches.append((i,deltaR))
			return sorted(matches, key=lambda tup:tup[1])

		for genMuon in (mu11, mu12, mu21, mu22):
			# cut genMuons outside the detector acceptance
			genMuonSelection = Selections.MuonSelection(genMuon, cutList='MuonAcceptanceCutList')
			if not genMuonSelection: continue

			Counters['Muon']['TOTAL'] += 1

			PREFIX = 'DSA'
			for recoMuons in (DSAmuons,):
			#for recoMuons in (DSAmuons, RSAmuons):
				matches = matchedMuons(genMuon, recoMuons)
				if len(matches) != 0:
					closestRecoMuon = recoMuons[matches[0][0]]
					Selection = Selections.MuonSelection(closestRecoMuon)
					Selection.IndividualIncrement(Counters['Muon']['IND'])
					Selection.SequentialIncrement(Counters['Muon']['CUM'])

		for dimuon in Dimuons:
			Muon1Selection = Selections.MuonSelection(DSAmuons[dimuon.idx1])
			Muon2Selection = Selections.MuonSelection(DSAmuons[dimuon.idx2])
			if Muon1Selection.allExcept('d0Sig') and Muon2Selection.allExcept('d0Sig'):
				Counters['Dimuon']['TOTAL'] += 1
			else:
				continue
			dimuonSelection = Selections.DimuonSelection(dimuon)
			dimuonSelection.IndividualIncrement(Counters['Dimuon']['IND'])
			dimuonSelection.SequentialIncrement(Counters['Dimuon']['CUM'])

	del t
	f.Close()
	del f

	for PREFIX,SHORT in zip(('Muon', 'Dimuon'),('MUO','DIM')):
		for DTYPE,SUFFIX in zip(('IND', 'CUM'),('All', 'None')):
			fstring = SHORT+' '+DTYPE+': {mH:<9s} {mX:<9s} {cTau:<9s} '
			fstring += ' '.join(['{'+key+':<9s}' for key in Selections.CutLists[PREFIX+'CutListPlus'+SUFFIX]])
			print fstring.format(mH='mH', mX='mX', cTau='cTau', **{key:key for key in Selections.CutLists[PREFIX+'CutListPlus'+SUFFIX]})

			fstring = SHORT+' '+DTYPE+': {mH:<9d} {mX:<9d} {cTau:<9d} '
			fstring += ' '.join(['{'+key+':<9.3f}' for key in Selections.CutLists[PREFIX+'CutListPlus'+SUFFIX]])
			print fstring.format(mH=sp[0], mX=sp[1], cTau=sp[2], **{key:value/float(Counters[PREFIX]['TOTAL']) for key, value in Counters[PREFIX][DTYPE].iteritems()})
