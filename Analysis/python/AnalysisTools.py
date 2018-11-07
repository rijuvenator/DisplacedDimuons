import math
import ROOT as R
import DisplacedDimuons.Analysis.Primitives as Primitives

# defines a proximity match between a genMuon and a recoMuon (Primitives.GenMuon and Primitives.RecoMuon/Primitives.TriggerMuon), in either order
# if deltaR < 0.2, return deltaR; otherwise, return None
def proximityMatch(muon1, muon2, vertex=None):
    # make sure that genMuons and recoMuons are assigned correctly
    class1 = muon1.__class__.__name__
    class2 = muon2.__class__.__name__
    if class1 == Primitives.GenMuon.__name__ and (class2 == Primitives.RecoMuon.__name__ or class2 == Primitives.TriggerMuon.__name__):
        genMuon = muon1
        recoMuon = muon2
    elif class2 == Primitives.GenMuon.__name__ and (class1 == Primitives.RecoMuon.__name__ or class1 == Primitives.TriggerMuon.__name__):
        genMuon = muon2
        recoMuon = muon1
    else:
        raise Exception('[ANALYSISTOOLS ERROR]: Proximity match requires one gen muon and one reco muon')

    # compute deltaR, using the correct 4-vector
    if vertex != 'BS':
        deltaR = recoMuon.p4.DeltaR(genMuon.p4)
    else:
        # deal with refitted tracks with 0 pT -- pretend deltaR is very large
        # gen 0 pT occurs only when the BS extrapolated gen track doesn't work properly
        # this happens when gen eta is very large, so they would probably be outside acceptance anyway
        # to prevent stderr warning lines, return None immediately
        if genMuon.BS.pt < 1.e-10:
            return None
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
def matchedMuons(baseMuon, muonList, vertex=None):
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


def matchedDimuons(genMuonPair, dimuons, recoMuons=None, vertex=None, doDimuons=True):
    exitcode = ExitCode()
    # return matched based on refitted tracks
    if recoMuons is None:
        doDimuons = True
        dimuonMatches = []
        muonMatches = [[], []]
        for idx,dimuon in enumerate(dimuons):
            deltaR_Align = [proximityMatch(genMuonPair[0], dimuon.mu1, vertex=vertex), proximityMatch(genMuonPair[1], dimuon.mu2, vertex=vertex)]
            deltaR_Cross = [proximityMatch(genMuonPair[0], dimuon.mu2, vertex=vertex), proximityMatch(genMuonPair[1], dimuon.mu1, vertex=vertex)]

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
            dimuonLookup = {(dim.idx1, dim.idx2):(dim, didx) for didx,dim in enumerate(dimuons)}
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

# function for computing ZBi given nOn, nOff, and tau
def ZBi(nOn, nOff, tau):
    PBi = R.TMath.BetaIncomplete(1./(1.+tau),nOn,nOff+1)
    return R.TMath.Sqrt(2.)*R.TMath.ErfInverse(1. - 2.*PBi)
