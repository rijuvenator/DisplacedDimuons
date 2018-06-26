# -*- coding: utf-8 -*-
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

    Event    = E.getPrimitives('EVENT'  )
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    for genMuonPair in genMuonPairs:
        # require genMuonPair to be within acceptance
        genMuonSelection = Selections.AcceptanceSelection(genMuonPair)
        if not genMuonSelection: continue

        # check if any DSA muons match a genMuon
        muonMatches = [None, None]
        for i, genMuon in enumerate(genMuonPair):
            matches = matchedMuons(genMuon, DSAmuons)
            if len(matches) > 0:
                muonMatches[i] = matches[0]['idx']

        # if both genMuons matched, check if there is a dimuon with exactly those recoMuons
        if muonMatches[0] is not None and muonMatches[1] is not None and muonMatches[0] != muonMatches[1]:
            for dimuon in Dimuons:
                if dimuon.idx1 in muonMatches and dimuon.idx2 in muonMatches:
                    break
            else:
                if genMuonPair[0].Lxy() > 340.:
                    dumpInfo(Event, genMuonPair, muonMatches, DSAmuons, Dimuons, extramu)

# dump info
def dumpInfo(Event, genMuonPair, muonMatches, DSAmuons, Dimuons, extramu):
    print '=== Run LS Event : {} {} {} ==='.format(Event.run, Event.lumi, Event.event)
    for genMuon in genMuonPair:
        print 'Gen Muon Pair: {:7s} {:10.4f} {:12s} {:7.4f} {:7.4f} {:9.4f}'.format(
                '',
                genMuon.pt,
                '',
                genMuon.eta,
                genMuon.phi,
                genMuon.Lxy(),
        )
    for i, muon in enumerate(DSAmuons):
        fstring = '  Reco Muon:   {:7d} {:10.4f} {:1s}{:11.4f} {:7.4f} {:7.4f} {:9s} {:10s} {:7.4f} {:7.4f}'.format(
            i,
            muon.pt,
            '±',
            muon.ptError,
            muon.eta,
            muon.phi,
            '',
            '',
            muon.p4.DeltaR(genMuonPair[0].p4),
            muon.p4.DeltaR(genMuonPair[1].p4),
        )
        if i in muonMatches:
            if COLOR:
                fstring = '\033[31m' + fstring + '\033[m'
            else:
                fstring = '*' + fstring[1:]
        print fstring
    for dimuon in Dimuons:
        fstring = '  Dimuon:      {:2d} * {:2d} {:10s} {:12s} {:7s} {:7s} {:9.4f} {:1s}{:9.4f}'.format(
            dimuon.idx1,
            dimuon.idx2,
            '',
            '',
            '',
            '',
            dimuon.Lxy(),
            '±',
            dimuon.Lxy()/dimuon.LxySig()
        )
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
        BRANCHKEYS  = ('EVENT', 'GEN', 'DSAMUON', 'DIMUON'),
    )
