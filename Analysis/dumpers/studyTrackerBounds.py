# -*- coding: utf-8 -*-
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedDimuons

#### CLASS AND FUNCTION DEFINITIONS ####
# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
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
        dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, Dimuons, DSAmuons, vertex='BS')

        # print if exitcode 1, 2, 3: gen muons matched (or exists next best), but no dimuon found, and Lxy>340
        if exitcode in (1, 2, 3) and genMuonPair[0].Lxy() > 340.:
            dumpInfo(Event, genMuonPair, muonMatches, exitcode, DSAmuons, Dimuons, extramu, PARAMS)

# dump info
def dumpInfo(Event, genMuonPair, muonMatches, exitcode, DSAmuons, Dimuons, extramu, PARAMS):
    print '=== Run LS Event : {} {} {} ==='.format(Event.run, Event.lumi, Event.event)
    if exitcode == 1:
        muonMatchIndices = [muonMatches[0][0]['idx'], muonMatches[1][0]['idx']]
    elif exitcode == 2:
        muonMatchIndices = [muonMatches[0][0]['idx'], muonMatches[1][1]['idx']]
    elif exitcode == 3:
        muonMatchIndices = [muonMatches[0][1]['idx'], muonMatches[1][0]['idx']]
    for genMuon in genMuonPair:
        print 'Gen Muon Pair: {:7s} {:10.4f} {:12s} {:7.4f} {:7.4f} {:11.4f} {:9.4f}'.format(
                '',
                genMuon.pt,
                '',
                genMuon.eta,
                genMuon.phi,
                genMuon.z,
                genMuon.Lxy(),
        )
    for i, muon in enumerate(DSAmuons):
        fstring = '  Reco Muon:   {:7d} {:10.4f} {:1s}{:11.4f} {:7.4f} {:7.4f} {:11s} {:9s} {:10s} {:7.4f} {:7.4f} {:2d} {:2d} {:2d} {:2d} {:2d}'.format(
            i,
            muon.pt,
            '±',
            muon.ptError,
            muon.eta,
            muon.phi,
            '',
            '',
            '',
            muon.p4.DeltaR(genMuonPair[0].BS.p4),
            muon.p4.DeltaR(genMuonPair[1].BS.p4),
            muon.nDTStations,
            muon.nCSCStations,
            muon.nDTHits,
            muon.nCSCHits,
            muon.nMuonHits
        )
        if i in muonMatchIndices:
            if PARAMS.COLOR:
                fstring = '\033[31m' + fstring + '\033[m'
            else:
                fstring = '*' + fstring[1:]
        print fstring
    for dimuon in Dimuons:
        fstring = '  Dimuon:      {:2d} * {:2d} {:10s} {:12s} {:7s} {:7s} {:11s} {:9.4f} {:1s}{:9.4f}'.format(
            dimuon.idx1,
            dimuon.idx2,
            '',
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
                extraGen.pt,
                '',
                extraGen.eta,
                extraGen.phi,
        )
    print ''

#### RUN ANALYSIS ####
if __name__ == '__main__':
    Analyzer.PARSER.add_argument('--color', dest='COLOR', action='store_true', help='whether to print reco matches in color')
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('analyze',):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('EVENT', 'GEN', 'DSAMUON', 'DIMUON'),
        PARAMS      = ARGS
    )
