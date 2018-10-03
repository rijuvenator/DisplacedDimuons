import math
import ROOT as R
import DisplacedDimuons.Analysis.Primitives as Primitives

# defines a proximity match between a genMuon and a recoMuon (Primitives.GenMuon and Primitives.RecoMuon), in either order
def proximityMatch(muon1, muon2, vertex='BS'):
    # make sure that genMuons and recoMuons are assigned correctly
    class1 = muon1.__class__.__name__
    class2 = muon2.__class__.__name__
    if class1 == Primitives.GenMuon.__name__ and class2 == Primitives.RecoMuon.__name__:
        genMuon = muon1
        recoMuon = muon2
    elif class2 == Primitives.GenMuon.__name__ and class1 == Primitives.RecoMuon.__name__:
        genMuon = muon2
        recoMuon = muon1
    else:
        raise Exception('[ANALYSISTOOLS ERROR]: Proximity match requires one gen muon and one reco muon')

    # compute deltaR, using the correct 4-vector
    if vertex != 'BS':
        deltaR = recoMuon.p4.DeltaR(genMuon.p4)
    else:
        deltaR = recoMuon.p4.DeltaR(genMuon.BS.p4)

    # define proximity match
    if deltaR < 0.2:
        return deltaR
    else:
        return None

# given a baseMuon and a list of muons to which to compare,
# return list of dictionaries (sorted by deltaR) of the list index and the deltaR
# idx is the 'real' idx of the LIST of muonList
# oidx is the 'original' idx of the ORIGINAL list of muons (the idx that is stored by RecoMuons)
# dimuon.mu.idx MUST compare with oidx only, if appropriate
# but getting the muon with muonList[matches[0]['idx']] can only be done with LIST idx
# Note: this function was originally designed with baseMuon = genMuon and muonList = list(recoMuons)
# but it is sometimes useful to have baseMuon = recoMuon and muonList = list(genMuons)
# so the functions are treated symmetrically
def matchedMuons(baseMuon, muonList, vertex='BS'):
    matches = []
    if len(muonList) == 0:
        return matches
    for i,muon in enumerate(muonList):
        deltaR = proximityMatch(baseMuon, muon, vertex)
        if deltaR is not None:
            try:
                oidx = muon.idx
            except AttributeError:
                oidx = None # if muonList is genMuons, which don't have the idx attribute
            matches.append({'idx':i, 'deltaR':deltaR, 'oidx':oidx})
    return sorted(matches, key=lambda dic:dic['deltaR'])

# given a genMuonPair, a list of dimuons, and a list of recoMuons:
# - use the matchedMuons function to find lists of matched muons to gen muons
# - find all possible dimuons with those matched indices
# given a genMuonPair and a list of dimuons:
# - find all dimuons whose constituent refitted muons proximity match gen muons
# return syntax: dimuonMatches, muonMatches, exitcode
# len(dimuonMatches) > 0 means a dimuon was found for this genMuonPair
# exitcode 0 means dimuons were found
# exitcode 1 means both gen muons did not match
# exitcode 2 means both gen muons matched, but a suitable dimuon was not found -- this can only happen if recoMuons is provided
# exitcode 3 means the dimuon list was empty and nothing was matched
def matchedDimuons(genMuonPair, dimuons, recoMuons=None, vertex='BS'):
    if len(dimuons) == 0:
        return [], [[], []], 3

    if recoMuons is None:
        dimuonMatches = []
        muonMatches = [[], []]
        for idx,dimuon in enumerate(dimuons):
            deltaR_Align = [proximityMatch(genMuonPair[0], dimuon.mu1, vertex=vertex), proximityMatch(genMuonPair[1], dimuon.mu2, vertex=vertex)]
            deltaR_Cross = [proximityMatch(genMuonPair[0], dimuon.mu2, vertex=vertex), proximityMatch(genMuonPair[1], dimuon.mu1, vertex=vertex)]
            if (deltaR_Align[0] is not None and deltaR_Align[1] is not None) or (deltaR_Cross[0] is not None and deltaR_Cross[1]):
                dimuonMatches.append({'idx':idx, 'dim':dimuon})
            if deltaR_Align[0] is not None and deltaR_Align[1] is not None:
                muonMatches[0].append({'idx':dimuon.idx1, 'deltaR':deltaR_Align[0], 'oidx':dimuon.idx1, 'didx':idx})
                muonMatches[1].append({'idx':dimuon.idx2, 'deltaR':deltaR_Align[1], 'oidx':dimuon.idx2, 'didx':idx})
            if deltaR_Cross[0] is not None and deltaR_Cross[1] is not None:
                muonMatches[0].append({'idx':dimuon.idx2, 'deltaR':deltaR_Cross[0], 'oidx':dimuon.idx2, 'didx':idx})
                muonMatches[1].append({'idx':dimuon.idx1, 'deltaR':deltaR_Cross[1], 'oidx':dimuon.idx1, 'didx':idx})

        # some exploitation of zip being its own inverse
        # first zip: put all the lists into a single table so each "row" can be sorted
        # then sort by genMuon0's deltaR, then genMuon1's deltaR
        # second zip: unpacks all entries (one per dimuon match) as lists, then zips them
        # this restores the original dimuonMatches, muonMatches[0], muonMatches[1] format
        # then just catch them
        if len(dimuonMatches) > 1:
            sortTable = zip(dimuonMatches, muonMatches[0], muonMatches[1])
            sortTable.sort(key=lambda row:(row[1]['deltaR'],row[2]['deltaR']))
            dimuonMatches, muonMatches[0], muonMatches[1] = zip(*sortTable)
    else:
        muonMatches = []
        for genMuon in genMuonPair:
            muonMatches.append(matchedMuons(genMuon, recoMuons, vertex=vertex))

        dimuonLookup = {(dim.idx1, dim.idx2):(dim, didx) for didx,dim in enumerate(dimuons)}
        dimuonMatches = []
        for match1 in muonMatches[0]:
            for match2 in muonMatches[1]:
                if match1['oidx'] == match2['oidx']: continue
                try:
                    oIdx = (match1['oidx'], match2['oidx'])
                    dimuonMatches.append({'idx':dimuonLookup[oIdx][1], 'dim':dimuonLookup[oIdx][0]})
                except:
                    try:
                        oIdx = (match2['oidx'], match1['oidx'])
                        dimuonMatches.append({'idx':dimuonLookup[oIdx][1], 'dim':dimuonLookup[oIdx][0]})
                    except:
                        pass

    # NOT FINISHED YET
    if len(dimuonMatches) > 0:
        return dimuonMatches, muonMatches, 0
    elif len(muonMatches[0]) > 0 and len(muonMatches[1]) > 0:
        return dimuonMatches, muonMatches, 2
    else:
        return dimuonMatches, muonMatches, 1

# function for computing ZBi given nOn, nOff, and tau
def ZBi(nOn, nOff, tau):
    PBi = R.TMath.BetaIncomplete(1./(1.+tau),nOn,nOff+1)
    return R.TMath.Sqrt(2.)*R.TMath.ErfInverse(1. - 2.*PBi)
