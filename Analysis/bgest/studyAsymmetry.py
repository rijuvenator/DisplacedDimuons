import numpy as np
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons
import DisplacedDimuons.Analysis.Selector as Selector

#### CLASS AND FUNCTION DEFINITIONS ####
# setup function for Analyzer class
def begin(self, PARAMS=None):
    pass

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    pass

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return

    Event = E.getPrimitives('EVENT')

    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')

    for attr in ('DSAmuons', 'PATmuons', 'Dimuons3'):
        setattr(self, attr, locals()[attr])

    def modifiedName(name):
        if 'DoubleMuon' in name:
            return 'Data'+name[17]
        if 'QCD' in name:
            return 'QCD'
        return name

    # no LxySig, no Dphi, and no blinding
    # LxySig < 1 applied below; iDphi and Dphi kept track of in dump
    CUTSTRING = '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_OS'

    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, CUTSTRING, Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is None: return

    for dim in selectedDimuons:
        if dim.composition == 'PAT' and dim.LxySig() < 1.:
            daddyMuons = self.getOriginalDSAMuons(dim)

            if sum([len(daddyMuons[idx]) for idx in daddyMuons]) < 2:
                print 'After original: Something is wrong: why did you not find 2 DSA muons leading to 2 PAT muons?'

            selectedDSAIndices = []
            for patIdx in daddyMuons:
                # dirty disambiguation
                if len(daddyMuons[patIdx]) == 0:
                    print 'In Loop: Something is wrong: why did you not find 2 DSA muons leading to 2 PAT muons?'
                elif len(daddyMuons[patIdx]) > 1:
                    thisDSAmuon = list(sorted(daddyMuons[patIdx], key=lambda mu: mu.pt, reverse=True))[0]
                    selectedDSAIndices.append(thisDSAmuon.idx)
                else:
                    thisDSAmuon = daddyMuons[patIdx][0]
                    selectedDSAIndices.append(thisDSAmuon.idx)

            parentDSADim = None
            if len(selectedDSAIndices) == 2:
                for DSADim in Dimuons3:
                    if DSADim.composition != 'DSA': continue
                    if selectedDSAIndices[0] in DSADim.ID and selectedDSAIndices[1] in DSADim.ID:
                        parentDSADim = DSADim
                        break

            if parentDSADim is None: continue

            print '{:9s} {:d} {:7d} {:10d} ::: PAT {:2d} {:2d} <-- DSA {:2d} {:2d} ::: {:9.4f} {:9.4f} ::: {:6.4f} {:6.4f}'.format(
                    modifiedName(self.NAME), Event.run, Event.lumi, Event.event,
                    dim         .ID[0], dim         .ID[1],
                    parentDSADim.ID[0], parentDSADim.ID[1],
                    dim.LxySig(), parentDSADim.LxySig(),
                    dim.deltaPhi, parentDSADim.deltaPhi,
            )

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    pass

def getOriginalDSAMuons(self, SelectedPATDimuon):
    selectedDSAmuons = [mu for mu in self.DSAmuons if Selections.MuonSelection(mu, cutList='DSAQualityCutList')]
    selectedOIndices = [mu.idx for mu in selectedDSAmuons]
    #selectedDimuons  = [dim for dim in self.Dimuons3 if set(dim.ID).issubset(selectedOIndices) or dim.composition != 'DSA']
    PATSelections = {muon.idx:Selections.MuonSelection(muon, cutList='PATQualityCutList') for muon in self.PATmuons}
    selectedPATmuons = self.PATmuons
    cutList = ['p_isGlobal', 'p_nTrkLays']

    # input to replaceDSAMuons is selectedDSAmuons, selectedPATmuons, selectedDimuons, PATSelections, cutList
    # what follows is the body of the replaceDSAmuons function, with **** EDIT **** for the pieces that needed
    # to be edited so as to actually get the daddy DSA muons out: basically, the dimuons were not necessary
    # so I just stop as soon as there would have been a replacement, and keep track of the muon

    inputPATs = {mu.idx:mu for mu in selectedPATmuons}

    # defines a SegMatch, returns a pair of indices (called candidate)
    # uses inputPATs, above
    def lookForSegMatch(DSAmuon):
        if DSAmuon.SegMatchPP.idx is None:
            return None

        # define what a segment match is
        # the tuples contain segment matches with 50% matched segments and above
        # fSeg sets the actual threshold to 2/3
        selectedSegMatches = [idx for idx, nSeg in zip(DSAmuon.SegMatchPP.idx, DSAmuon.SegMatchPP.nSeg) if float(nSeg)/DSAmuon.nSegments > 0.66]

        # only consider segMatches that are selectedPATmuons
        # don't do this anymore
        # segMatches = [idx for idx in DSAmuon.SegMatchPP.idx if idx in inputPATs]

        # ONLY if there are multiple segment matches,
        # filter the segment matches based on some selections
        # then go through the rest of the segment matching logic
        # ONLY if filtering results in 0 segment matches,
        # pretend that the cuts were not done at all, i.e.
        # if filtering gets down to 1, great -- it'll get taken
        # if it gets down to 2+, great -- prox will disambiguate
        # if it gets down to 0, the filtering would cause us to lose the match,
        # so pretend the filtering didn't happen
        if len(selectedSegMatches) > 1 and PATSelections is not None:
            segMatches = [idx for idx in selectedSegMatches if PATSelections[idx].allOf(*cutList)]
            if len(segMatches) == 0:
                segMatches = selectedSegMatches
        else:
            segMatches = selectedSegMatches

        # if 0, no matches
        # if 1, take the match
        # if 2+, disambiguate using ProxMatch OR take the first entry, if ProxMatch is not a SegMatch
        if len(segMatches) == 0:
            return None

        if len(segMatches) > 1:
            if DSAmuon.ProxMatchPP.idx in segMatches:
                candidate = DSAmuon.ProxMatchPP.idx
            else:
                # take first entry
                # which is the smallest index = largest pT
                candidate = segMatches[0]
        else:
            candidate = segMatches[0]

        return candidate

    # always do the last-resort DSA proximity match
    DSAProxMatch = True

    # as a last resort, use the proximity match in certain cases
    def lookForProximityMatch(DSAmuon):
        # only do this if there are NO segment matches

        # to do: this line used to read  if DSAmuon.SegMatchPP.idx is not None: return None
        # but now, it being None doesn't mean there ARE valid SegMatches
        #if DSAmuon.SegMatchPP.idx is not None: return None
        if DSAmuon.ProxMatchPP.idx is None: return None

        # option 2: proximity match is within deltaR of 0.1
        if DSAmuon.ProxMatchPP.deltaR < 0.1:
            return DSAmuon.ProxMatchPP.idx

        return None

    # ***** EDIT *****
    replacedDSAmuons = {idx:[] for idx in SelectedPATDimuon.ID}

    for mu in selectedDSAmuons:
        candidate = lookForSegMatch(mu)
        if candidate is None:
            if DSAProxMatch:
                candidate = lookForProximityMatch(mu)
        if candidate is not None:

            if candidate in replacedDSAmuons:
                replacedDSAmuons[candidate].append(mu)

    return replacedDSAmuons

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('begin', 'declareHistograms', 'analyze', 'end', 'getOriginalDSAMuons'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DIMUON', 'PATMUON', 'DSAMUON', 'TRIGGER', 'GEN', 'EVENT', 'FILTER'),
    )

    # write plots
    #analyzer.writeHistograms('roots/mcbg/AsymmetryPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
