# -*- coding: utf-8 -*-
import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

#### CLASS AND FUNCTION DEFINITIONS ####
# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN', 'HTo2XTo4Mu')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN', 'HTo2XTo2Mu2J')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)
    Event    = E.getPrimitives('EVENT')
    DSAmuons = E.getPrimitives('DSAMUON')

    SelectMuons   = False
    # require muons to pass all selections
    if SelectMuons:
        DSASelections    = [Selections.MuonSelection  (muon)   for muon   in DSAmuons]

        selectedDSAmuons = [mu  for idx,mu  in enumerate(DSAmuons) if DSASelections   [idx]]

    # don't require muons to pass all selections
    else:
        selectedDSAmuons = DSAmuons

    # loop over genMuons and print if pTRes is poor
    for genMuon in genMuons:

        matches = matchedMuons(genMuon, selectedDSAmuons)
        if len(matches) != 0:
            closestRecoMuon = selectedDSAmuons[matches[0]['idx']]

            if (closestRecoMuon.pt-genMuon.pt)/genMuon.pt < -0.8:
                dumpInfo(Event, genMuon, selectedDSAmuons, len(matches), extramu)

# dump info
def dumpInfo(Event, genMuon, DSAmuons, nMatches, extramu):
    print '=== Run LS Event : {} {} {} ==='.format(Event.run, Event.lumi, Event.event)
    print 'Gen Muon:    {:10.4f} {:12s} {:7.4f} {:7.4f} {:9.4f} {:2d}'.format(
            genMuon.pt,
            '',
            genMuon.eta,
            genMuon.phi,
            genMuon.Lxy(),
            nMatches
    )
    for muon in DSAmuons:
        fstring = '  Reco Muon: {:10.4f} {:1s}{:11.4f} {:7.4f} {:7.4f} {:9s} {:2s} {:7.4f} {:2d} {:2d} {:2d} {:2d} {:2d}'.format(
            muon.pt,
            '±',
            muon.ptError,
            muon.eta,
            muon.phi,
            '',
            '',
            muon.p4.DeltaR(genMuon.p4),
            muon.nDTStations,
            muon.nCSCStations,
            muon.nDTHits,
            muon.nCSCHits,
            muon.nMuonHits
        )
        if muon.p4.DeltaR(genMuon.p4) < 0.3:
            if COLOR:
                fstring = '\033[31m' + fstring + '\033[m'
            else:
                fstring = '*' + fstring[1:]
        print fstring
    for extraGen in extramu:
        print 'Extra GenMuon: {:7s} {:10.4f} {:12s} {:7.4f} {:7.4f}'.format(
                '',
                genMuon.pt,
                '',
                genMuon.eta,
                genMuon.phi,
        )
    print ''

#### RUN ANALYSIS ####
if __name__ == '__main__':
    COLOR = False
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('analyze',):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('EVENT', 'GEN', 'DSAMUON'),
    )
