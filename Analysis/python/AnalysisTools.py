# defines a match between a genMuon (Primitives.GenMuon) and a recoMuon (Primitives.RecoMuon)
# returns list of dictionaries sorted by deltaR of the index of the list, the deltaR gen-reco, and the reco pt
def matchedMuons(genMuon, recoMuons):
	matches = []
	for i,muon in enumerate(recoMuons):
		deltaR = muon.p4.DeltaR(genMuon.p4)
		#if deltaR < min(0.3,genMuon.deltaR) and Selections.CUTS['pt'].apply(muon) and muon.charge == genMuon.charge:
		if deltaR < min(0.3,genMuon.deltaR):
			matches.append({'idx':i, 'deltaR':deltaR, 'pt':muon.pt})
	return sorted(matches, key=lambda dic:dic['deltaR'])

# defines a match between a genMuonPair (Primitives.GenMuon) and a dimuon (Primitives.Dimuon)
# returns list of dictionaries sorted by deltaR of the index of the list, the deltaR gen-reco, and the reco pt
def matchedDimuons(genMuonPair, dimuons):
    matches = []
    genP4 = genMuonPair[0].p4 + genMuonPair[1].p4
    for i,dimuon in enumerate(dimuons):
        deltaR = dimuon.p4.DeltaR(genP4)
        if deltaR < min(0.3, genMuonPair[0].deltaR):
            matches.append({'idx':i, 'deltaR':deltaR, 'pt':dimuon.pt})
    return sorted(matches, key=lambda dic:dic['deltaR'])

# calculates pT resolution
def pTRes(recoMuon, genMuon):
	return (recoMuon.pt - genMuon.pt)/genMuon.pt


