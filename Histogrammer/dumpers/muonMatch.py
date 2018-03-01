import ROOT as R
import DisplacedDimuons.Histogrammer.Primitives as Primitives
from DisplacedDimuons.Histogrammer.Constants import DIR_DD, DIR_WS, SIGNALS

#f = R.TFile.Open(DIR_DD + 'Tupler/ntuples/simple_ntuple.root')
f = R.TFile.Open(DIR_WS + 'simple_ntuple_125_20_1300.root')
t = f.Get('SimpleNTupler/DDTree')

cTau = []
dX   = []

BRANCHKEYS = ('MUON', 'VERTEX', 'EVENT', 'GEN')
Primitives.SelectBranches(t, BRANCHKEYS)
for i, event in enumerate(t):
	if i == 10: break

	E = Primitives.ETree(t, BRANCHKEYS)
	muons = E.getPrimitives('MUON')
	vertices = E.getPrimitives('VERTEX')
	mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN')

	print 'Entry {}: REL {}:{}:{}, {} vertices, {} muons ({} slim)'.format(
		i,
		t.evt_run,
		t.evt_event,
		t.evt_lumi,
		len(vertices),
		len(muons),
		sum([1 for muon in muons if muon.isSlim]),
		len(t.gen_pdgID)
	)

	dX.append((X1.pos-mu11.pos).Mag())
	dX.append((X2.pos-mu21.pos).Mag())
	cTau.append(X1.mass/X1.p3.Mag()*mu11.pos.Dist(X1.pos))
	cTau.append(X2.mass/X2.p3.Mag()*mu21.pos.Dist(X2.pos))

	for muon in muons:
		if not muon.isSlim: continue
		print '  {muonPT:9.4f} {muonGenPT} {muonPos:9.4p}'.format(
			muonPT    = muon.pt,
			muonGenPT = '{:9.4f}'.format(muon.gen.pt) if muon.gen.pt != -999 else '{:9s}'.format('-'),
			muonPos   = muon.pos
		)
		for vertex in vertices:
			if muon.pos.Dist(vertex.pos) < 0.1:
				print '  {spaces:20s}{vertexPos:9.4p} {dist:6.4e}'.format(
					spaces = " ",
					vertexPos = vertex.pos,
					dist = muon.pos.Dist(vertex.pos)
				)

print 'avg. cTau = {:9.4f}, avg. dX = {:9.4f}'.format(sum(cTau)/len(cTau), sum(dX)/len(dX))
