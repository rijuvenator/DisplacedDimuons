import ROOT as R
import DisplacedDimuons.Histogrammer.Primitives as Primitives
from DisplacedDimuons.Histogrammer.Constants import DIR_DD, DIR_WS, SIGNALS

#f = R.TFile.Open(DIR_DD + 'Tupler/ntuples/simple_ntuple.root')
f = R.TFile.Open(DIR_WS + 'simple_ntuple_125_20_1300.root')
t = f.Get('SimpleNTupler/DDTree')

#cTau = []
#dX   = []

BRANCHKEYS = ('MUON', 'VERTEX', 'EVENT', 'GEN', 'DSAMUON')
Primitives.SelectBranches(t, BRANCHKEYS)
for i, event in enumerate(t):
	if i == 10: break

	E = Primitives.ETree(t, BRANCHKEYS)
	muons = E.getPrimitives('MUON')
	vertices = E.getPrimitives('VERTEX')
	mu11, mu12, mu21, mu22, X1, X2, H, P = E.getPrimitives('GEN')
	DSAmuons = E.getPrimitives('DSAMUON')

	print 'Entry {}: REL {}:{}:{}, {} vertices, {} muons ({} slim), {} DSA muons'.format(
		i,
		t.evt_run,
		t.evt_event,
		t.evt_lumi,
		len(vertices),
		len(muons),
		sum([1 for muon in muons if muon.isSlim]),
		len(DSAmuons),
	)

	def findClosestMuon(muon, muons):
		if len(muons) == 0:
			return None
		closestDeltaR = float('inf')
		closestMuon = None
		for mu in muons:
			if muon.p4.DeltaR(mu.p4) < closestDeltaR:
				closestDeltaR = muon.p4.DeltaR(mu.p4)
				closestMuon = mu
		return closestMuon

	for muon in (mu11, mu12, mu21, mu22):
		closestRecMuon = findClosestMuon(muon, muons)
		closestDSAMuon = findClosestMuon(muon, DSAmuons)
		print '  {genMuonPT:10.4f} {recMuonPT:10.4f} {recDeltaR:10.4f} {DSAMuonPT:10.4f} {DSADeltaR:10.4f}'.format(
			genMuonPT = muon.pt,
			recMuonPT = float('inf') if closestRecMuon is None else closestRecMuon.pt,
			recDeltaR = float('inf') if closestRecMuon is None else muon.p4.DeltaR(closestRecMuon.p4),
			DSAMuonPT = float('inf') if closestDSAMuon is None else closestDSAMuon.pt,
			DSADeltaR = float('inf') if closestDSAMuon is None else muon.p4.DeltaR(closestDSAMuon.p4),
		)

	#dX.append((X1.pos-mu11.pos).Mag())
	#dX.append((X2.pos-mu21.pos).Mag())
	#cTau.append(X1.mass/X1.p3.Mag()*mu11.pos.Dist(X1.pos))
	#cTau.append(X2.mass/X2.p3.Mag()*mu21.pos.Dist(X2.pos))

	#def findClosestVertex(muon, vertices):
	#	closestDistance = float('inf')
	#	closestVertex = None
	#	for vertex in vertices:
	#		if muon.pos.Dist(vertex.pos) < closestDistance:
	#			closestDistance = muon.pos.Dist(vertex.pos)
	#			closestVertex = vertex
	#	return closestVertex

	#for muon in muons:
	#	if not muon.isSlim: continue
	#	vertex = findClosestVertex(muon, vertices)
	#	#print '  {muonPT:10.4f} {muonGenPT} {muonPos:10.4p}'.format(
	#	print '  {muonPT:10.4f} {muonGenPT} {muonPos:10.4p} {dist:6.4e}'.format(
	#		muonPT    = muon.pt,
	#		muonGenPT = '{:10.4f}'.format(muon.gen.pt) if muon.gen.pt != -999 else '{:10s}'.format('-'),
	#		muonPos   = muon.pos,
	#		dist = muon.pos.Dist(vertex.pos)
	#	)
	#	#print '  {spaces:20s}{vertexPos:10.4p} {dist:6.4e}'.format(
	#	#	spaces = " ",
	#	#	vertexPos = vertex.pos,
	#	#	dist = muon.pos.Dist(vertex.pos)
	#	#)
	#print
	#for muon in (mu11, mu12, mu21, mu22):
	#	vertex = findClosestVertex(muon, vertices)
	#	print '  {muonPT:10.4f} {muonGenPT} {muonPos:10.4p} {dist:6.4e}'.format(
	#		muonPT    = muon.pt,
	#		muonGenPT = '{:10s}'.format('-'),
	#		muonPos   = muon.pos,
	#		dist = muon.pos.Dist(vertex.pos)
	#	)
	#print
	#for muon in DSAmuons:
	#	vertex = findClosestVertex(muon, vertices)
	#	print '  {muonPT:10.4f} {muonGenPT} {muonPos:10.4p} {dist:6.4e}'.format(
	#		muonPT    = muon.pt,
	#		muonGenPT = '{:10s}'.format('-'),
	#		muonPos   = muon.pos,
	#		dist = muon.pos.Dist(vertex.pos)
	#	)

#print 'avg. cTau = {:10.4f}, avg. dX = {:10.4f}'.format(sum(cTau)/len(cTau), sum(dX)/len(dX))
