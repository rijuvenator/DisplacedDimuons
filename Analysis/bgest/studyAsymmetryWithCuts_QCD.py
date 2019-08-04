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
    if 'QCD' in self.NAME:
        self.COUNTS = {'rep':0, 'norep':0}

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

    eventWeight = 1.
    try:
        eventWeight = 1. if Event.weight > 0. else -1.
    except:
        pass

    for attr in ('DSAmuons', 'PATmuons', 'Dimuons3'):
        setattr(self, attr, locals()[attr])

    def modifiedName(name):
        if 'DoubleMuon' in name:
            return 'Data'+name[17]
        if 'QCD' in name:
            return 'QCD'
        return name

    # no replacement, LxySig, no Dphi, and no blinding
    # LxySig < 1 applied to the REPLACED PAT muons below; iDphi and Dphi kept track of in dump
    CUTSTRING = '_Combined_NS_NH_FPTE_HLT_PT_TRK_NDT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP'

    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, CUTSTRING, Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is None: return

    for dim in selectedDimuons:
        # select same sign / opposite sign
        if dim.mu1.charge + dim.mu2.charge != 0: continue

        patDimuon = self.getPATDimuon(dim)
        if patDimuon is None:
            if 'QCD' in self.NAME:
                if dim.LxySig() > 9.:
                    self.COUNTS['norep'] += 1
            continue

        if 'QCD' in self.NAME:
            if dim.LxySig() > 9.:
                self.COUNTS['rep'] += 1

        #if patDimuon.LxySig() < 1.:

        mu1, mu2 = PATmuons[patDimuon.mu1.idx], PATmuons[patDimuon.mu2.idx]
        if patDimuon.LxySig() < 115. and patDimuon.LxySig() > 60. and mu1.trackIso/mu1.pt > 0.5 and mu2.trackIso/mu2.pt > 0.5:
            print '{:9s} {:d} {:7d} {:10d} {:2d} ::: PAT {:2d} {:2d} <-- DSA {:2d} {:2d} ::: {:9.4f} {:9.4f} ::: {:6.4f} {:6.4f} ::: {:.5e} {:.5e} ::: {:.5e} {:.5e} {:.5e} ::: {:.4e} {:6.4f}'.format(
                    modifiedName(self.NAME), Event.run, Event.lumi, Event.event, int(eventWeight),
                    patDimuon   .ID[0], patDimuon   .ID[1],
                    dim         .ID[0], dim         .ID[1],
                    patDimuon.LxySig(), dim.LxySig(),
                    patDimuon.deltaPhi, dim.deltaPhi,
                    dim.Lxy(), dim.LxyErr(),
                    dim.mu1.pt, dim.mu2.pt, dim.pt,
                    dim.mass, dim.deltaR
            )

# cleanup function for Analyzer class
def end(self, PARAMS=None):
    if 'QCD' in self.NAME:
        print self.COUNTS

def getPATDimuon(self, SelectedDSADimuon):
    selectedDSAmuons = [mu for mu in self.DSAmuons if mu.idx in SelectedDSADimuon.ID]

    selectedPATmuons = self.PATmuons
    PATSelections = {muon.idx:Selections.MuonSelection(muon, cutList='PATQualityCutList') for muon in self.PATmuons}
    cutList = ['p_isGlobal', 'p_nTrkLays']

    selectedDimuons = self.Dimuons3

    # input to replaceDSAMuons is selectedDSAmuons, selectedPATmuons, selectedDimuons, PATSelections, cutList
    # what follows is the body of the replaceDSAmuons function, with some pieces edited
    # the replacement functions are the same; the actual calls are a bit simplified
    # and the only dimuons needed are the PAT dimuons

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

        # option 2: if it's a global muon, we don't have segments,
        # but check if the number of hits is the same, and if they
        # are, and the deltaR is < 0.2, take it as a match
        # NEW: removing the deltaR cut, so now it's 0.4
        PATmuon = inputPATs[DSAmuon.ProxMatchPP.idx]
        if PATmuon.isGlobal and (not PATmuon.isTracker):
            if     PATmuon.nDTHits      == DSAmuon.nDTHits      \
               and PATmuon.nCSCHits     == DSAmuon.nCSCHits     \
               and PATmuon.nDTStations  == DSAmuon.nDTStations  \
               and PATmuon.nCSCStations == DSAmuon.nCSCStations:
               return DSAmuon.ProxMatchPP.idx

        return None

    matchingPATMuons = {}

    for mu in selectedDSAmuons:
        candidate = lookForSegMatch(mu)
        if candidate is None:
            candidate = lookForProximityMatch(mu)
        if candidate is not None:
            matchingPATMuons[candidate] = self.PATmuons[candidate]

    patDimuon = None
    if len(matchingPATMuons) == 2:
        patIndices = matchingPATMuons.keys()
        for dim in self.Dimuons3:
            if dim.composition != 'PAT': continue
            if set(dim.ID).issubset(patIndices):
                patDimuon = dim
                break

    return patDimuon

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('begin', 'declareHistograms', 'analyze', 'end', 'getPATDimuon'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DIMUON', 'PATMUON', 'DSAMUON', 'TRIGGER', 'GEN', 'EVENT', 'FILTER'),
    )

    # write plots
    #analyzer.writeHistograms('roots/mcbg/AsymmetryPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
