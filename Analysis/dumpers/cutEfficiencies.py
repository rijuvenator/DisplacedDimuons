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
parser.add_argument('--fromfile'    , dest='FROMFILE'   , action='store_true', help='whether to rerun over trees'  )
args = parser.parse_args()

if not args.SIGNALPOINT:
	SIGNALPOINTS = [(125, 20, 13)]
else:
	SIGNALPOINTS = [tuple(args.SIGNALPOINT)]

for sp in SIGNALPOINTS:
	f = R.TFile.Open(DIR_WS + 'simple_ntuple_{}.root'.format(SPStr(sp)))
	t = f.Get('SimpleNTupler/DDTree')

	IndivEffDict = {key:0 for key in Selections.MuonCutListPlusAll}
	CumEffDict = {key:0 for key in Selections.MuonCutListPlusNone}
	Total = 0

	Primitives.SelectBranches(t, ('DSAMUON', 'GEN'))
	#Primitives.SelectBranches(t, ('DSAMUON', 'RSAMUON', 'GEN'))
	for i, event in enumerate(t):

		if args.DEVELOP:
			if i == 1000: break

		E = Primitives.ETree(t, ('DSAMUON', 'GEN'))
		#E = Primitives.ETree(t, ('DSAMUON', 'RSAMUON', 'GEN'))
		mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN')
		DSAmuons = E.getPrimitives('DSAMUON')
		#RSAmuons = E.getPrimitives('RSAMUON')

		def matchedMuons(genMuon, recoMuons):
			matches = []
			for i,muon in enumerate(recoMuons):
				deltaR = muon.p4.DeltaR(genMuon.p4)
				if deltaR < 0.3:
					matches.append((i,deltaR))
			return sorted(matches, key=lambda tup:tup[1])

		for genMuon in (mu11, mu12, mu21, mu22):
			# cut genMuons outside the detector acceptance
			genMuonSelection = Selections.MuonSelection(genMuon, cutList=Selections.MuonAcceptanceCutList)
			if not genMuonSelection: continue

			Total += 1

			PREFIX = 'DSA'
			for recoMuons in (DSAmuons,):
			#for recoMuons in (DSAmuons, RSAmuons):
				matches = matchedMuons(genMuon, recoMuons)
				if len(matches) != 0:
					closestRecoMuon = recoMuons[matches[0][0]]
					Selection = Selections.MuonSelection(closestRecoMuon)
					Selection.IndividualIncrement(IndivEffDict)
					Selection.SequentialIncrement(CumEffDict)

	del t
	f.Close()
	del f

	fstring = 'IND: {mH:<9d} {mX:<9d} {cTau:<9d} '
	fstring += ' '.join(['{'+key+':<9.3f}' for key in Selections.MuonCutListPlusAll])
	print fstring.format(mH=sp[0], mX=sp[1], cTau=sp[2], **{key:value/float(Total) for key, value in IndivEffDict.iteritems()})

	fstring = 'CUM: {mH:<9d} {mX:<9d} {cTau:<9d} '
	fstring += ' '.join(['{'+key+':<9.3f}' for key in Selections.MuonCutListPlusNone])
	print fstring.format(mH=sp[0], mX=sp[1], cTau=sp[2], **{key:value/float(Total) for key, value in CumEffDict.iteritems()})
