# defines a match between a genMuon (Primitives.Muon with source=GEN) and a recoMuon (Primitives.Muon with source=DSA or RSA)
# retuns list of dictionaries sorted by deltaR of the index of the list, the deltaR gen-reco, and the reco pt
def matchedMuons(genMuon, recoMuons):
	matches = []
	for i,muon in enumerate(recoMuons):
		deltaR = muon.p4.DeltaR(genMuon.p4)
		#if deltaR < min(0.3,genMuon.pairDeltaR) and Selections.MuonCuts['pt'].apply(muon) and muon.charge == genMuon.charge:
		if deltaR < min(0.3,genMuon.pairDeltaR):
			matches.append({'idx':i, 'deltaR':deltaR, 'pt':muon.pt})
	return sorted(matches, key=lambda dic:dic['deltaR'])

# calculates pT resolution
def pTRes(recoMuon, genMuon):
	return (recoMuon.pt - genMuon.pt)/genMuon.pt


