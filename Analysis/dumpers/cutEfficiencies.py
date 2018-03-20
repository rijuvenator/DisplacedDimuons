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
	SIGNALPOINTS = [args.SIGNALPOINT]

for sp in SIGNALPOINTS:
	f = R.TFile.Open(DIR_WS + 'simple_ntuple_{}.root'.format(SPStr(sp)))
	t = f.Get('SimpleNTupler/DDTree')

	EffDict = {cutkey:0 for cutkey in Selections.MuonCutList}
	EffDict['all'] = 0
	Total = 0

	Primitives.SelectBranches(t, ('DSAMUON',))
	for i, event in enumerate(t):
		if args.DEVELOP:
			if i == 1000: break

		E = Primitives.ETree(t, ('DSAMUON',))
		DSAmuons = E.getPrimitives('DSAMUON')
		Total += len(DSAmuons)
		for muon in DSAmuons:
			Selection = Selections.MuonSelection(muon)
			for key in EffDict:
				if Selection[key]:
					EffDict[key] += 1
	
	del t
	f.Close()
	del f
	
	print SPStr(sp).replace('_', ' ')
	for key in EffDict:
		print '  {:9s} {:6d} {:6d} {:.3f}'.format(key, EffDict[key], Total, EffDict[key]/float(Total))
	print ''
