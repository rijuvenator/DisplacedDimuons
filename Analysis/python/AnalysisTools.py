# defines a match between a genMuon (Primitives.GenMuon) and a recoMuon (Primitives.RecoMuon)
# returns list of dictionaries sorted by deltaR of the index of the list, the deltaR gen-reco, and the reco pt
def matchedMuons(genMuon, recoMuons):
	matches = []
	for i,muon in enumerate(recoMuons):
		deltaR = muon.p4.DeltaR(genMuon.p4)
		#if deltaR < min(0.3,genMuon.deltaR) and Selections.CUTS['pT'].apply(muon) and muon.charge == genMuon.charge:
		if deltaR < 0.3:
			matches.append({'idx':i, 'deltaR':deltaR, 'pt':muon.pt})
	return sorted(matches, key=lambda dic:dic['deltaR'])

# defines a match between a genMuonPair (Primitives.GenMuon) and a dimuon (Primitives.Dimuon)
# returns list of dictionaries sorted by deltaR of the index of the list, the deltaR gen-reco, and the reco pt
def matchedDimuons(genMuonPair, dimuons):
    matches = []
    genP4 = genMuonPair[0].p4 + genMuonPair[1].p4
    for i,dimuon in enumerate(dimuons):
        deltaR = dimuon.p4.DeltaR(genP4)
        if deltaR < 0.3:
            matches.append({'idx':i, 'deltaR':deltaR, 'pt':dimuon.pt})
    return sorted(matches, key=lambda dic:dic['deltaR'])

# finds the dimuon constructed from the reco muons matching the given genMuonPair, if any
# returns a tuple: (dimuon, exitcode, muonMatches).
# dimuon is None if no such dimuon exists
# exitcode 0 means dimuon was found (redundant with dimuon is not None)
# exitcode 1 means both gen muons did not match
# exitcode 2 means both gen muons matched, but a suitable dimuon was not found
# muonMatches are the indices of the matching reco muons
def findDimuon(genMuonPair, recoMuons, dimuons):
    muonMatches = [None, None]
    for i, genMuon in enumerate(genMuonPair):
        matches = matchedMuons(genMuon, recoMuons)
        if len(matches) > 0:
            muonMatches[i] = matches[0]['idx']

    if muonMatches[0] is not None and muonMatches[1] is not None and muonMatches[0] != muonMatches[1]:
        for dimuon in dimuons:
            if dimuon.idx1 in muonMatches and dimuon.idx2 in muonMatches:
                return dimuon, 0, muonMatches
        else:
            return None, 2, muonMatches
    else:
        return None, 1, muonMatches
