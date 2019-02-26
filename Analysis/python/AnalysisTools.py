import math
import ROOT as R
import DisplacedDimuons.Analysis.Primitives as Primitives

# defines a proximity match between two muons, in any order
# if deltaR < threshold, return deltaR; otherwise, return None
def proximityMatch(muon1, muon2, vertex=None, threshold=0.2):
    class1 = muon1.__class__.__name__
    class2 = muon2.__class__.__name__

    GM = Primitives.GenMuon.__name__

    # if vertex = 'BS', and we have gen muons, make any gen muons use the BS version of quantities
    # this will actually also work for two gen muons, in addition to gen + reco in any order
    if vertex == 'BS' and class1 == GM or class2 == GM:
        mu1 = muon1.BS if class1 == GM else muon1
        mu2 = muon2.BS if class2 == GM else muon2

        # deal with refitted gen tracks with 0 pT -- pretend deltaR is very large
        # gen 0 pT occurs only when the BS extrapolated gen track doesn't work properly
        # this happens when gen eta is very large, so they would probably be outside acceptance anyway
        # to prevent stderr warning lines, return None immediately
        if mu1.pt < 1.e-10 or mu2.pt < 1.e-10:
            return None

        mu1P4 = mu1.p4
        mu2P4 = mu2.p4

    # otherwise, just use the normal p4
    else:
        mu1P4 = muon1.p4
        mu2P4 = muon2.p4

    # compute deltaR
    deltaR = mu1P4.DeltaR(mu2P4)

    # define proximity match
    if deltaR < threshold:
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
def matchedMuons(baseMuon, muonList, vertex=None, threshold=0.2):
    matches = []
    if len(muonList) == 0:
        return matches
    for i,muon in enumerate(muonList):
        deltaR = proximityMatch(baseMuon, muon, vertex, threshold)
        if deltaR is not None:
            try:
                oidx = muon.idx
            except AttributeError:
                oidx = None # if muonList is genMuons, which don't have the idx attribute
            matches.append({'idx':i, 'deltaR':deltaR, 'oidx':oidx, 'muon':muon})
    return sorted(matches, key=lambda dic:dic['deltaR'])

# given a genMuonPair, a list of dimuons, and a list of recoMuons:
#   - use the matchedMuons function to find lists of matched muons to gen muons
#   - find all possible dimuons with those matched indices
#   - figure out which gen muons matched, and whether there's a second best
# given a genMuonPair, a list of dimuons, a list of recoMuons, and doDimuons=False:
#   - use the matchedMuons function to find lists of matched muons to gen muons
#   - figure out which gen muons matched, and whether there's a second best
# given a genMuonPair and a list of dimuons:
#   - find all dimuons whose constituent refitted muons proximity match gen muons
#
# return syntax: dimuonMatches, muonMatches, exitcode
# exitcode.dimuons  == True  means at least one dimuon exists in the event, False if not
# exitcode.matched  == True  means at least one dimuon was found for this genMuonPair, False if not
#
# exitcode.both     == True  means both gen muons matched reco muons
# exitcode.same     == True  means gen muons individually matched different reco muons, False if not
# exitcode.nextBest == True  means gen muons individually matched the same  reco muon + there is a next best
# exitcode.winner   == 0, 1  means gen muons individually matched the same  reco muon + g0, g1 is better (check nextBest)
#
# exitcode.both     == False means both gen muons did not match reco muons
# exitcode.which    == 0, 1  means both gen muons did not match reco muons + g0, g1 matched + g1, g0 did not
# exitcode.which    == -1    means both gen muons did not match + neither g0 nor g1 matched
#
# Note about DUMMY:
# much of this function depends on a) whether or not recoMuons was provided, and b) whether or not dimuons is empty
# if recoMuons is not provided, use the refitted muons embedded in dimuons to match to gen
# if recoMuons IS provided, use the given list of recoMuons instead to match to gen
# however, it turns out that the exitcode logic -- which uniquely partitions the possible states by which muons matched, etc.
# can be and is useful without the context of dimuons. You can always match a gen muon to a list of reco muons.
# But the way I have it, exitcode 0 is immediate when dimuons were found. So what if I want to provide recoMuons, and get
# the exitcode information too? I'll never get exitcode 1 if a dimuon was found. What I actually want in such a case is
# to not look for dimuons at all. But I can't pass an empty list, because that's exitcode 9 -- otherwise, yes, I would never
# match a dimuon. So my current solution is: pass dimuons = ('DUMMY',). This will not flag exitcode 9 because len() is not 0,
# and it won't flag exitcode 0 because you can't match to a string. dimuonMatches will be [], and the usual exitcode process
# will proceed. Of course, this only makes sense if recoMuons is not None! But that's when I would want to use it anyway.
# If dimuons = ('DUMMY',) is passed and recoMuons is None, the "else" condition triggers and you cleanly get exitcode 9.

class ExitCode(object):
    def __init__(self):
        self.dimuons  = None
        self.matched  = None

        self.both     = None
        self.which    = None

        self.same     = None
        self.nextBest = None
        self.winner   = None

    def getBestGenMuonMatches(self, muonMatches):
        if self.both:
            if not self.same:
                return         muonMatches[0][0], muonMatches[1][0]
            else:
                if self.nextBest:
                    if self.winner == 0:
                        return muonMatches[0][0], muonMatches[1][1]
                    else:
                        return muonMatches[0][1], muonMatches[1][0]
                else:
                    if self.winner == 0:
                        return muonMatches[0][0], None
                    else:
                        return None             , muonMatches[1][0]
        else:
            if self.which == 0:
                return         muonMatches[0][0], None
            elif self.which == 1:
                return         None             , muonMatches[1][0]
            else:
                return         None             , None


def matchedDimuons(genMuonPair, dimuons, recoMuons=None, vertex=None, threshold=0.2, doDimuons=True):
    exitcode = ExitCode()
    # return matched based on refitted tracks
    if recoMuons is None:
        doDimuons = True
        dimuonMatches = []
        muonMatches = [[], []]
        for idx,dimuon in enumerate(dimuons):
            deltaR_Align = [proximityMatch(genMuonPair[0], dimuon.mu1, vertex=vertex, threshold=threshold), proximityMatch(genMuonPair[1], dimuon.mu2, vertex=vertex, threshold=threshold)]
            deltaR_Cross = [proximityMatch(genMuonPair[0], dimuon.mu2, vertex=vertex, threshold=threshold), proximityMatch(genMuonPair[1], dimuon.mu1, vertex=vertex, threshold=threshold)]

            # figure out which pairing resulted in both muons being matched
            alignMatched = deltaR_Align[0] is not None and deltaR_Align[1] is not None
            crossMatched = deltaR_Cross[0] is not None and deltaR_Cross[1] is not None

            # fill in either case
            # if BOTH cases matched, first check if there's an "obvious" answer: both Align < or both Cross <
            # if there is, pick that one.
            # if not, this is ambiguous. In this case, we will randomly keep (1, 2).
            # the "align" decision is (1, 2); the "cross" decision is (2, 1)
            if alignMatched or crossMatched:
                if alignMatched and crossMatched:
                    if deltaR_Align[0] < deltaR_Cross[0] and deltaR_Align[1] < deltaR_Cross[1]:
                        decisions = ((1, 2),)
                    elif deltaR_Align[0] > deltaR_Cross[0] and deltaR_Align[1] > deltaR_Cross[1]:
                        decisions = ((2, 1),)
                    else:
                        # this is ambiguous, but we will make a decision now
                        decisions = ((1, 2),)
                else:
                    if alignMatched:
                        decisions = ((1, 2),)
                    elif crossMatched:
                        decisions = ((2, 1),)

                for decision in decisions:
                    if decision == (1, 2):
                        deltaR_Vals = deltaR_Align
                    else:
                        deltaR_Vals = deltaR_Cross
                    dimuonMatches.append({'idx':idx, 'dim':dimuon})
                    for genIdx in (0, 1):
                        oIdx = getattr(dimuon, 'idx'+str(decision[genIdx]))
                        muon = getattr(dimuon, 'mu' +str(decision[genIdx]))
                        muonMatches[genIdx].append({'idx':None, 'deltaR':deltaR_Vals[genIdx], 'oidx':oIdx, 'didx':idx, 'muon':muon})

        # some exploitation of zip being its own inverse
        # first zip: put all the lists into a single table so each "row" can be sorted
        # then sort by genMuon0's deltaR, then genMuon1's deltaR
        # second zip: unpacks all entries (one per dimuon match) as lists, then zips them
        # this restores the original dimuonMatches, muonMatches[0], muonMatches[1] format
        # then just catch them
        if len(dimuonMatches) > 1:
            sortTable = zip(dimuonMatches, muonMatches[0], muonMatches[1])
            sortTable.sort(key=lambda row:row[1]['deltaR']**2.+row[2]['deltaR']**2.)
            dimuonMatches, muonMatches[0], muonMatches[1] = zip(*sortTable)

    # return matched based on original tracks
    elif recoMuons is not None:
        muonMatches = []
        for genMuon in genMuonPair:
            muonMatches.append(matchedMuons(genMuon, recoMuons, vertex=vertex))

        if doDimuons and len(dimuons) != 0:
            dimuonLookup = {dim.ID:(dim, didx) for didx,dim in enumerate(dimuons)}
            dimuonMatches = []
            for match1 in muonMatches[0]:
                for match2 in muonMatches[1]:
                    if match1['oidx'] == match2['oidx']: continue
                    try:
                        oIdx = (match1['oidx'], match2['oidx'])
                        dimuonMatches.append({'idx':dimuonLookup[oIdx][1], 'dim':dimuonLookup[oIdx][0], 'matches':(match1, match2)})
                    except:
                        try:
                            oIdx = (match2['oidx'], match1['oidx'])
                            dimuonMatches.append({'idx':dimuonLookup[oIdx][1], 'dim':dimuonLookup[oIdx][0], 'matches':(match1, match2)})
                        except:
                            pass
        else:
            dimuonMatches = []

    # always figure out if there were dimuons and dimuon matches
    # exitcode dimuons: whether there were dimuons in the event
    # exitcode matched: whether there was a dimuon match
    if len(dimuons) == 0:
        exitcode.dimuons = False
        exitcode.matched = False
    else:
        exitcode.dimuons = True
        exitcode.matched = (len(dimuonMatches) > 0)

    # for a given list of reco muons, figure out additional information about which ones matched and next best
    if recoMuons is not None:
        if len(muonMatches[0]) > 0 and len(muonMatches[1]) > 0:
            # exitcode both: True if both gen muons matched reco muons
            exitcode.both = True
            # exitcode same: False if each gen muon individually matched different reco muons
            if muonMatches[0][0]['oidx'] != muonMatches[1][0]['oidx']:
                same = False
            # exitcode nextBest, winner, loser: each gen muon individually matched the same reco muon, but
            # if we keep the gen muon that's closer, the "losing" gen muon has a second best option
            elif muonMatches[0][0]['oidx'] == muonMatches[1][0]['oidx']:
                exitcode.same = True
                # exitcode: muon 0 won, muon 1 lost; take muonMatches[0][0] and muonMatches[1][1]
                if muonMatches[0][0]['deltaR'] < muonMatches[1][0]['deltaR'] and len(muonMatches[1]) > 1:
                    exitcode.nextBest = True
                    exitcode.winner   = 0
                # exitcode: muon 1 won, muon 0 lost; take muonMatches[0][1] and muonMatches[1][0]
                elif muonMatches[0][0]['deltaR'] >= muonMatches[1][0]['deltaR'] and len(muonMatches[0]) > 1:
                    exitcode.nextBest = True
                    exitcode.winner   = 1
                # exitcode nextBest, winner, loser: each gen muon individually matched the same reco muon,
                # and the "losing" gen muon has no second best option
                else:
                    # exitcode: muon 0 won, muon 1 has no next best; take muonMatches[0][0] and None
                    if muonMatches[0][0]['deltaR'] < muonMatches[1][0]['deltaR']:
                        exitcode.nextBest = False
                        exitcode.winner   = 0
                    # exitcode: muon 1 won, muon 0 has no next best; take None and muonMatches[1][0]
                    elif muonMatches[0][0]['deltaR'] >= muonMatches[1][0]['deltaR']:
                        exitcode.nextBest = False
                        exitcode.winner   = 1
        # exitcode both: False if both gen muons didn't match reco muons
        # exitcode which: which ones did match, if any
        else:
            exitcode.both = False
            if len(muonMatches[0]) > 0 and len(muonMatches[1]) == 0:
                exitcode.which = 0
            elif len(muonMatches[1]) > 0 and len(muonMatches[0]) == 0:
                exitcode.which = 1
            else:
                exitcode.which = -1

    # final return
    return dimuonMatches, muonMatches, exitcode

def matchedTrigger(HLTMuons, uncutDSAMuons, saveDeltaR=False, threshold=0.4, printAllMatches = False):

    # this selection should be here, instead of floating around
    DSAMuons = [mu for mu in uncutDSAMuons if mu.pt > 10. and abs(mu.eta) < 2.]

    HLTMuonMatches = {}
    # loop over unique pairs of HLT muons
    nHLT = len(HLTMuons)
    for i in xrange(nHLT):
        for j in xrange(i+1,nHLT):
            hltMuon1, hltMuon2 = HLTMuons[i], HLTMuons[j]

            # for a given pair of muons, re-calculate trigger variables and trigger decision
            hltDimuon = hltMuon1.p4 + hltMuon2.p4
            mass, angle = hltDimuon.M(), hltMuon1.p3.Angle(hltMuon2.p3)

            # found a pair of muons that fired; now look for closest DSA muons
            if mass > 9.99996 and angle < 2.5:
                HLTMuonMatches[(i, j)] = {}
                # find all the matching DSA muons, sort them by deltaR...
                matches = []
                for muon in DSAMuons:
                    for hltIdx, hltMuon in ((i, hltMuon1), (j, hltMuon2)):
                        if saveDeltaR:
                            dR = proximityMatch(hltMuon, muon, threshold=float('inf'))
                        else:
                            dR = proximityMatch(hltMuon, muon, threshold=threshold)
                        if dR is not None:
                            matches.append({'hlt_idx':hltIdx, 'rec_idx':muon.idx, 'deltaR':dR})
                matches = sorted(matches, key=lambda dic:dic['deltaR'])
                if printAllMatches: print matches

                # find the closest matches
                # walk through the list of matches. the first one (0) is the best one for
                # whatever match[0]['hlt_idx'] is. keep walking through until you hit another
                # hlt_idx. make sure its reco muon is not the same as the one you have, and
                # that's the other match. this accounts for multiple matches.
                bestMatches = []
                for match in matches:
                    if len(bestMatches) == 0:
                        bestMatches.append(match)
                    elif len(bestMatches) == 1:
                        if bestMatches[0]['hlt_idx'] != match['hlt_idx']:
                            if bestMatches[0]['rec_idx'] != match['rec_idx']:
                                bestMatches.append(match)
                                break

                HLTMuonMatches[(i,j)]['bestMatches'] = bestMatches

                # at this point, bestMatches is either 0, 1, or 2. "matchFound" is
                # only if both hltMuons matched different DSAmuons.
                # if saveDeltaR, that means proximityMatch calculated deltaR, but didn't
                # apply any cuts. so to actually decide if matchFound, check the threshold.
                if len(bestMatches) == 2:
                    if not saveDeltaR:
                        HLTMuonMatches[(i,j)]['matchFound'] = True
                    else:
                        if bestMatches[0]['deltaR'] < threshold and bestMatches[1]['deltaR'] < threshold:
                            HLTMuonMatches[(i,j)]['matchFound'] = True
                        else:
                            HLTMuonMatches[(i,j)]['matchFound'] = False
                else:
                    HLTMuonMatches[(i,j)]['matchFound'] = False

            # sanity check for the 2016 trigger: make sure that there
            # are no events with a single pair of HLT muons failing
            # angular or mass cuts
            else:
                if nHLT == 2:
                    print "+++ Warning in matchedTrigger: inconsistency in the trigger +++"
                    print "found single online dimuon with mass = ", mass, "and angle =", angle
                    print "hlt_idxs: ", i, j, "; list of HLT muons:"
                    for hltmuon in HLTMuons:
                        print(hltmuon)

    # return structure
    # if no triggering pair was found, this dictionary will be empty, otherwise keys are (i,j) indices of HLTMuons
    # HLTMuonMatches['matchFound'] is True if 2 DSA muons matched 2 HLTMuons below given threshold (default 0.4)
    # HLTMuonMatches['bestMatches'] is a list of 0-2 match dictionaries containing hlt_idx, rec_idx (a.k.a. oIdx), and deltaR
    # If saveDeltaR is True, this list may contain deltaR values > threshold; otherwise, it definitely won't
    # To get the two closest deltaR's regardless of threshold, e.g., do matchedTrigger(HLTMuons, DSAMuons, saveDeltaR=True)
    # Then do: for match in HLTMuonMatches['bestMatches']: dR = match['deltaR'] (can fill a histogram)
    # Of course, to check if there are any matches at all, simply do any([HLTMuonMatches[ij]['matchFound'] for ij in HLTMuonMatches])
    return HLTMuonMatches

def matchedDimuonPairs(genMuonPairs, dimuons, recoMuons=None, vertex=None, threshold=0.2, doDimuons=True):
    # find matches for both pairs
    matchLists = {'dim':[], 'mu0':[], 'mu1':[]}
    for i, genMuonPair in enumerate(genMuonPairs):
        dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, dimuons, recoMuons=recoMuons, vertex=vertex, threshold=threshold, doDimuons=doDimuons)
        if len(dimuonMatches) > 0:
            for key, matchList in zip(['dim', 'mu0', 'mu1'], [dimuonMatches, muonMatches[0], muonMatches[1]]):
                for match in matchList:
                    match['pairIndex'] = i
                matchLists[key].extend(matchList)

    # sort everything by deltaR^2
    # remember: matches is [matches_pair0 ... matches_pair1], and matches_pair0, e.g. is a list of dimuonMatches
    # so a "column" of the table is matches_pair0 + matches_pair1. When they get sorted, the best ones
    # will float to the top, and the "pairIndex" will help remember which pair they came from
    if len(matchLists['dim']) > 0: # zip doesn't behave for zero length
        sortTable = zip(matchLists['dim'], matchLists['mu0'], matchLists['mu1'])
        sortTable.sort(key=lambda row:row[1]['deltaR']**2.+row[2]['deltaR']**2.)
        dimuonMatches, muon0Matches, muon1Matches = zip(*sortTable)
    else:
        sortTable = []
        dimuonMatches, muon0Matches, muon1Matches = [], [], []

    # find the best two dimuon matches with non-overlapping muons
    realMatches = {}
    for dimMatch, mu0Match, mu1Match in sortTable:
        # remember which pair
        pairIndex = dimMatch['pairIndex']
        # if there's nothing in realMatches, take this match
        if len(realMatches) == 0:
            realMatches[pairIndex] = dimMatch
        # there's already something in realMatches
        # if it's the same pair, keep going
        # okay, it's the other pair. Great. But make sure the other pair
        # has no muons in common with the pair that exists already (alreadyFound, alreadyIndices)
        # if it does, keep going
        # otherwise, bingo! we've found the other match. fill it and break.
        else:
            if pairIndex in realMatches: continue
            alreadyFound = realMatches[realMatches.keys()[0]]['dim']
            alreadyIndices = (alreadyFound.idx1, alreadyFound.idx2)
            if dimMatch['dim'].idx1 in alreadyIndices or dimMatch['dim'].idx2 in alreadyIndices: continue
            realMatches[pairIndex] = dimMatch

    return realMatches, dimuonMatches, muon0Matches, muon1Matches

# apply the pairing criteria recipe developed in the pairing criteria study
# returns a list of 0, 1, or 2 dimuons, based on how many muons there are and the result of applying the recipe
def applyPairingCriteria(muons, dimuons, doAMD=False):
    # get the list of relevant dimuons
    selectedOIndices = [mu.idx for mu in muons]
    selectedDimuons  = [dim for dim in dimuons if dim.idx1 in selectedOIndices and dim.idx2 in selectedOIndices]

    # if there are any dimuons at all, there had to be >= 2 muons
    # if there's 2, just return the one dimuon that was made
    # if there's 3, return the dimuon with the lowest vertex chi^2/dof
    # if there's 4, find all pairs of dimuons, sort the pairs by chi^2/dof sum, and return the lowest one (2 dimuons)
    # with optional doAMD mode, return the lowest pair by mass difference instead if both dimuons have Lxy < 30 cm
    # if there were no pairings with 4 muons, treat it like a 3 muon case
    if len(selectedDimuons) > 0:
        if   len(muons) == 2:
            return selectedDimuons[0:1]
        elif len(muons) == 3:
            return sorted(selectedDimuons, key=lambda dim: dim.normChi2)[0:1]
        elif len(muons) >= 4:
            highestPTMuons = sorted(muons, key=lambda mu: mu.pt, reverse=True)[:4]
            highestIndices = [mu.idx for mu in highestPTMuons]
            HPDs = [d for d in selectedDimuons if d.idx1 in highestIndices and d.idx2 in highestIndices]

            # find all unique non-overlapping pairs of dimuons
            pairings = []
            for dim1 in HPDs:
                for dim2 in HPDs:
                    if dim1.ID == dim2.ID: continue
                    muonIDs = set(dim1.ID+dim2.ID)
                    if len(muonIDs) == 4:
                        pairings.append((dim1, dim2))

            def C2S(pairing): return pairing[0].normChi2+pairing[1].normChi2
            def AMD(pairing): return abs(pairing[0].mass-pairing[1].mass)

            funcs = {'C2S':C2S, 'AMD':AMD}

            # sort the pairings by a pairing criteria
            if len(pairings) > 0:
                candidateBestDimuons = {fkey:{} for fkey in funcs}
                sortedPairings = {}
                for fkey in funcs:
                    sortedPairings[fkey] = sorted(pairings, key=funcs[fkey])
                    for d in sortedPairings[fkey][0]:
                        candidateBestDimuons[fkey][d.ID] = d

                # try to use AMD for low Lxy
                if doAMD:
                    dims = candidateBestDimuons['AMD'].values()
                    if dims[0].Lxy() < 30. and dims[1].Lxy() < 30.:
                        bestDimuons = candidateBestDimuons['AMD']
                    else:
                        bestDimuons = candidateBestDimuons['C2S']
                else:
                    bestDimuons = candidateBestDimuons['C2S']
                return bestDimuons.values()

            # if there were NO pairings, there had to have been <=3 dimuons
            # because any 4 dimuons can always make at least 1 pair
            # this means 1 of the 4 muons formed no dimuons at all
            # so treat this case like the 3 mu case
            else:
                return sorted(selectedDimuons, key=lambda dim: dim.normChi2)[0:1]

    # there weren't any dimuons so return an empty list
    else:
        return []

# function for replacing DSA Dimuons with PAT Dimuons or Hybrid Dimuons
# The input Dimuons list should be the bare Primitives list, consisting of 3 embedded lists in order:
# the DSA-DSA dimuons, the PAT-PAT dimuons, and the hybrid DSA-PAT dimuons
# mode should be None, 'PAT', or 'HYBRID', corresponding to no replacement, PAT-PAT only, or PAT-PAT + DSA-PAT replacement
# match should be 'PROX' or 'SEG', indicating whether to use the proximity match or the segment match as criteria
# loose is either True or False, indicating, given match = SEG (PROX), whether to use PROX (SEG), if possible
def replaceDSADimuons(Dimuons3, DSAmuons, mode=None, match='SEG', loose=False):
    if mode is None:
        return Dimuons3

    if mode not in ('PAT', 'HYBRID'):
        raise ValueError("[ANALYSISTOOLS ERROR]: replaceDSADimuons mode should be None, 'PAT', or 'HYBRID'")
    if match not in ('SEG', 'PROX'):
        raise ValueError("[ANALYSISTOOLS ERROR]: replaceDSADimuons match should be 'SEG' or 'PROX'")

    # splits Dimuons3 into 3 pieces
    DSADimuons = [dim for dim in Dimuons3 if dim.composition == 'DSA'   ]
    PATDimuons = [dim for dim in Dimuons3 if dim.composition == 'PAT'   ]
    HYBDimuons = [dim for dim in Dimuons3 if dim.composition == 'HYBRID']

    # defines a SegMatch, returns a pair of indices (called candidate)
    def lookForSegMatch(mu1, mu2):
        candidate = []
        for mu in mu1, mu2:
            if mu.idx_SegMatch is None:
                candidate.append(None)
            elif len(mu.idx_SegMatch) > 1:
                if mu.idx_ProxMatch in mu.idx_SegMatch:
                    candidate.append(mu.idx_ProxMatch)
                else:
                    # take first entry
                    # which is the smallest index = largest pT
                    candidate.append(mu.idx_SegMatch[0])
            else:
                candidate.append(mu.idx_SegMatch[0])
        return candidate

    # defines a ProxMatch, returns a pair of indices (called candidate)
    def lookForProxMatch(mu1, mu2):
        return [mu1.idx_ProxMatch, mu2.idx_ProxMatch]

    # if using the backup option (loose), defines when a dimuon match was not found
    def matchNotFound(mode, candidate):
        if mode == 'PAT'    : return None in candidate
        if mode == 'HYBRID' : return candidate.count(None) == 2

    # if using the backup option (loose), defines when the backup option is preferable
    def backupCandidateIsBetter(mode, candidate):
        if mode == 'PAT'    : return None not in candidate
        if mode == 'HYBRID' : return candidate.count(None) < 2

    # code for figuring out the best candidate
    # note: this candidate is not guaranteed to be a dimuon
    # perhaps if it is not found, we might want to double back somehow
    def CandidateIndices(mode, match, dim, DSAmuons):
        # define the first and backup match criteria
        if match == 'SEG':
            firstLook  = lookForSegMatch
            backupLook = lookForProxMatch
        elif match == 'PROX':
            firstLook  = lookForProxMatch
            backupLook = lookForSegMatch

        # get the candidate
        mu1, mu2 = DSAmuons[dim.idx1], DSAmuons[dim.idx2]
        candidate = firstLook(mu1, mu2)

        # replace with backup, if appropriate
        if loose and matchNotFound(mode, candidate):
            backupCandidate = backupLook(mu1, mu2)
            if backupCandidateIsBetter(mode, backupCandidate):
                candidate = backupCandidate

        return candidate

    # for adding None to a number which is an index
    def IntWrapper(candIndex):
        if candIndex is None:
            return -2000
        return candIndex

    # the replacement logic is very similar for PAT and HYBRID
    # the only difference is the input list ("sourceList") and whether one requires both ID ("and"/"all") or just one ("or"/"any")
    # repList and wasReplaced are modified;
    # repType specifies PAT or HYBRID (maps to "all" or "any"), defDim is the original DSA dimuon which won't be replaced
    def ReplaceAdd(repList, boolList, sourceList, repType, defDim, candidate):
        if sourceList is None:
            repList.append(defDim)
            boolList.append(False)
        else:
            if repType == 'PAT':
                comboFunc = all
            elif repType == 'HYBRID':
                comboFunc = any
            for dimuon in sourceList:
                # WARNING: deal with this for HYBRID
                if comboFunc([IntWrapper(candidate[0]) in dimuon.ID, IntWrapper(candidate[1]) in dimuon.ID]):
                    repList.append(dimuon)
                    boolList.append(True)
                    break
            else:
                repList.append(defDim)
                boolList.append(False)


    replacedDimuons = []
    wasReplaced = []

    for dim in DSADimuons:

        # get candidate indices
        candidate = CandidateIndices(mode, match, dim, DSAmuons)

        # logic:
        # if mode is PAT, and both muons did not match, use DSA
        # else, look for the dimuon made of both PAT muons, replace if found, use DSA if not
        # if mode is HYBRID, and no muons matched, use DSA
        # if both muons matched, proceed as PAT above
        # if only one muon matched, look for a dimuon made of one DSA and one PAT muons, replace if found, use DSA if not
        if mode == 'PAT':
            if None in candidate:
                ReplaceAdd(replacedDimuons, wasReplaced, None, 'DEFAULT', dim, candidate)
            elif None not in candidate:
                ReplaceAdd(replacedDimuons, wasReplaced, PATDimuons, 'PAT', dim, candidate)

        elif mode == 'HYBRID':
            NoneMatches = candidate.count(None)
            if NoneMatches == 2:
                ReplaceAdd(replacedDimuons, wasReplaced, None, 'DEFAULT', dim, candidate)
            elif NoneMatches == 0:
                ReplaceAdd(replacedDimuons, wasReplaced, PATDimuons, 'PAT', dim, candidate)
            elif NoneMatches == 1:
                ReplaceAdd(replacedDimuons, wasReplaced, HYBDimuons, 'HYBRID', dim, candidate)

    return replacedDimuons, wasReplaced

# this function does the above, but earlier, on a muon basis, in prep for doing other selections
# for time's sake I will default a few of the options: mode is PAT, match is SEG, loose is False
def replaceDSAMuons(selectedDSAmuons, PATmuons, selectedDimuons):

    # defines a SegMatch, returns a pair of indices (called candidate)
    def lookForSegMatch(DSAmuon):
        candidate = None
        if DSAmuon.idx_SegMatch is None:
            pass
        elif len(DSAmuon.idx_SegMatch) > 1:
            if DSAmuon.idx_ProxMatch in DSAmuon.idx_SegMatch:
                candidate = DSAmuon.idx_ProxMatch
            else:
                # take first entry
                # which is the smallest index = largest pT
                candidate = DSAmuon.idx_SegMatch[0]
        else:
            candidate = DSAmuon.idx_SegMatch[0]
        return candidate

    # filter DSA muons based on whether there was a PAT match
    # after this, there are two lists: PAT muons which replaced a DSA muon, and
    # DSA muons which matched no PAT muon
    selectedPATmuons = []
    filteredDSAmuons = []
    DSAIndices = []
    PATIndices = []
    for mu in selectedDSAmuons:
        candidate = lookForSegMatch(mu)
        if candidate is not None:
            if candidate in PATIndices: continue
            selectedPATmuons.append(PATmuons[candidate]) # be careful. PATmuons is the full list, here.
            PATIndices.append(candidate)
        else:
            filteredDSAmuons.append(mu)
            DSAIndices.append(mu.idx)

    # possible indices for dimuons. Consider only DSA-DSA and PAT-PAT dimuons; skip HYBRID
    # call the new list "filteredDimuons"
    selectedIndices = {
        'DSA':DSAIndices,
        'PAT':PATIndices,
    }

    filteredDimuons = []
    for dim in selectedDimuons:
        if dim.composition == 'HYBRID': continue
        if dim.idx1 in selectedIndices[dim.composition] and dim.idx2 in selectedIndices[dim.composition]:
            filteredDimuons.append(dim)

    # final return
    # suitable for the following call:
    # selectedDSAmuons, selectedPATmuons, selectedDimuons = replaceDSAmuons(selectedDSAmuons, PATmuons, selectedDimuons)
    # where selectedDimuons is a Dimuons3 type list
    return filteredDSAmuons, selectedPATmuons, filteredDimuons

# function for computing ZBi given nOn, nOff, and tau
def ZBi(nOn, nOff, tau):
    PBi = R.TMath.BetaIncomplete(1./(1.+tau),nOn,nOff+1)
    return R.TMath.Sqrt(2.)*R.TMath.ErfInverse(1. - 2.*PBi)
