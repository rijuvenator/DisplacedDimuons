import ROOT as R
import os
import DisplacedDimuons.Histogrammer.Primitives as Primitives
from DisplacedDimuons.Histogrammer.Primitives import Point

DIR_DD = os.environ['CMSSW_BASE'] + '/src/DisplacedDimuons/'

f = R.TFile.Open(DIR_DD + 'Tupler/ntuples/simple_ntuple.root')
t = f.Get('SimpleNTupler/DDTree')

cTau = []
dX   = []

BRANCHKEYS = ('MUON', 'VERTEX', 'EVENT', 'GEN')
Primitives.SelectBranches(t, BRANCHKEYS)
for i, event in enumerate(t):
	#if i == 10: break

	E = Primitives.ETree(t, BRANCHKEYS)
	muons = E.getPrimitives('MUON')
	vertices = E.getPrimitives('VERTEX')
	mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN')

#	print 'Entry {}: REL {}:{}:{}, {} vertices, {} muons ({} slim)'.format(
#		i,
#		t.evt_run,
#		t.evt_event,
#		t.evt_lumi,
#		len(vertices),
#		len(muons),
#		sum([1 for muon in muons if muon.isSlim]),
#		len(t.gen_pdgID)
#	)

	dX.append(Point.dist(X1.pos, mu11.pos))
	dX.append(Point.dist(X2.pos, mu21.pos))
	cTau.append(X1.mass/X1.p3 * (mu11.pos - X1.pos))
	cTau.append(X2.mass/X2.p3 * (mu21.pos - X2.pos))

	#print 'CTau = {:9.4f}'.format(X1.mass/X1.p3 * (mu11.pos - X1.pos))
	#print 'CTau = {:9.4f}'.format(X2.mass/X2.p3 * (mu21.pos - X2.pos))
	#print 'CTau = {:9.4f}'.format(Point.dist(X1.pos, mu11.pos))
	#print 'CTau = {:9.4f}'.format(Point.dist(X2.pos, mu21.pos))

	#print '''Proton at {:9.4p} led to Higgs at {:9.4p}
    #led to X1 at {:9.4p}
    #    led to mu11 at {:9.4p}
    #    led to mu12 at {:9.4p}
    #led to X1 at {:9.4p}
    #    led to mu21 at {:9.4p}
    #    led to mu22 at {:9.4p}'''.format(P.pos, H.pos, X1.pos, mu11.pos, mu12.pos, X2.pos, mu21.pos, mu22.pos)

	#for muon in muons:
	#	if not muon.isSlim: continue
	#	print '  {muonPT:9.4f} {muonGenPT} {muonPos:9.4p}'.format(
	#		muonPT    = muon.pt,
	#		muonGenPT = '{:9.4f}'.format(muon.gen.pt) if muon.gen.pt != -999 else '{:9s}'.format('-'),
	#		muonPos   = muon.pos
	#	)
	#	for vertex in vertices:
	#		if Point.dist(muon.pos,vertex.pos) < 0.1:
	#			print '  {spaces:20s}{vertexPos:9.4p} {dist:6.4e}'.format(
	#				spaces = " ",
	#				vertexPos = vertex.pos,
	#				dist = Point.dist(muon.pos, vertex.pos)
	#			)
print 'avg. cTau = {:9.4f}, avg. dX = {:9.4f}'.format(sum(cTau)/len(cTau), sum(dX)/len(dX))
