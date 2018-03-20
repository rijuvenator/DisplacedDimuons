import ROOT as R
import DisplacedDimuons.Histogrammer.Primitives as Primitives
import DisplacedDimuons.Histogrammer.Selections as Selections
from DisplacedDimuons.Histogrammer.Constants import DIR_DD, DIR_WS, SIGNALS
from DisplacedDimuons.Histogrammer.Utilities import SPStr

signalpoints = [
#	(1000, 350,   35),
#	(1000, 350,  350),
#	(1000, 350, 3500),
#	(1000, 150,   10),
#	(1000, 150,  100),
#	(1000, 150, 1000),
#	(1000,  50,    4),
#	(1000,  50,   40),
#	(1000,  50,  400),
	(1000,  20,    2),
	(1000,  20,   20),
	(1000,  20,  200),
	( 400, 150,   40),
	( 400, 150,  400),
	( 400, 150, 4000),
#	( 400,  50,    8),
#	( 400,  50,   80),
#	( 400,  50,  800),
	( 400,  20,    4),
	( 400,  20,   40),
	( 400,  20,  400),
#	( 200,  50,   20),
#	( 200,  50,  200),
#	( 200,  50, 2000),
#	( 200,  20,    7),
#	( 200,  20,   70),
#	( 200,  20,  700),
	( 125,  50,   50),
	( 125,  50,  500),
	( 125,  50, 5000),
	( 125,  20,   13),
	( 125,  20,  130),
	( 125,  20, 1300),
]

for sp in [(125, 20, 13)]:
	f = R.TFile.Open(DIR_WS + 'simple_ntuple_{}.root'.format(SPStr(sp)))
	t = f.Get('SimpleNTupler/DDTree')

	EffDict = {cut.name:0 for cut in Selections.MuonCutList}
	EffDict['all'] = 0
	Total = 0

	Primitives.SelectBranches(t, ('DSAMUON',))
	for i, event in enumerate(t):
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
