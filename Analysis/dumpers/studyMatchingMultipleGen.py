# -*- coding: utf-8 -*-
import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

#### CLASS AND FUNCTION DEFINITIONS ####
def begin(self, PARAMS=None):
    self.COUNTERS = {
        'nGenMuons' : 0,
        'nMatches'  : 0,
        'nMultiple' : 0,
    }

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

    # loop over genMuons and count various matching criteria
    for genMuonPair in genMuonPairs:
        alreadySelected = []
        MATCHES = []
        for genMuon in genMuonPair:
            self.COUNTERS['nGenMuons'] += 1
            matches = matchedMuons(genMuon, selectedDSAmuons)
            MATCHES.append(matches)
            if len(matches) != 0:
                self.COUNTERS['nMatches'] += 1
                if matches[0]['idx'] not in alreadySelected:
                    alreadySelected.append(matches[0]['idx'])
                else:
                    self.COUNTERS['nMultiple'] += 2
                    alreadySelected.append(matches[0]['idx'])
                    if PARAMS.DUMP:
                        dumpInfo(Event, genMuonPair, selectedDSAmuons, MATCHES, extramu, PARAMS)

# dump info
def dumpInfo(Event, genMuonPair, DSAmuons, MATCHES, extramu, PARAMS):
    print '=== Run LS Event : {} {} {} ==='.format(Event.run, Event.lumi, Event.event)
    for genMuon, matches in zip(genMuonPair, MATCHES):
        print 'Gen Muon:      {:10.4f} {:12s} {:7.4f} {:7.4f} {:9.4f} {:2d}'.format(
                genMuon.pt,
                '',
                genMuon.eta,
                genMuon.phi,
                genMuon.Lxy(),
                len(matches)
        )
    for muon in DSAmuons:
        fstring = '  Reco Muon:   {:10.4f} {:1s}{:11.4f} {:7.4f} {:7.4f} {:9s} {:2s} {:7.4f} {:7.4f} {:2d} {:2d} {:2d} {:2d} {:2d}'.format(
            muon.pt,
            '±',
            muon.ptError,
            muon.eta,
            muon.phi,
            '',
            '',
            muon.p4.DeltaR(genMuonPair[0].p4),
            muon.p4.DeltaR(genMuonPair[1].p4),
            muon.nDTStations,
            muon.nCSCStations,
            muon.nDTHits,
            muon.nCSCHits,
            muon.nMuonHits
        )
        if muon.p4.DeltaR(genMuonPair[1].p4) < 0.3 and muon.p4.DeltaR(genMuonPair[0].p4) < 0.3:
            if PARAMS.COLOR:
                fstring = '\033[35m' + fstring + '\033[m'
            else:
                fstring = '**' + fstring[2:]
        elif muon.p4.DeltaR(genMuonPair[1].p4) < 0.3:
            if PARAMS.COLOR:
                fstring = '\033[31m' + fstring + '\033[m'
            else:
                fstring = ' *' + fstring[2:]
        elif muon.p4.DeltaR(genMuonPair[0].p4) < 0.3:
            if PARAMS.COLOR:
                fstring = '\033[32m' + fstring + '\033[m'
            else:
                fstring = '*' + fstring[1:]

        print fstring
    for extraGen in extramu:
        print 'Extra GenMuon: {:10.4f} {:12s} {:7.4f} {:7.4f}'.format(
                extraGen.pt,
                '',
                extraGen.eta,
                extraGen.phi,
        )
    print ''

# dump info
def end(self, PARAMS=None):
    fstring = 'DATA: {:4d} {:3d} {:4d} {:5s} {:6d} {:6d} {:6d} '
    print fstring.format(
        self.SP.mH,
        self.SP.mX,
        self.SP.cTau,
        '4Mu' if '4Mu' in self.NAME else '2Mu2J',
        self.COUNTERS['nGenMuons'],
        self.COUNTERS['nMatches' ],
        self.COUNTERS['nMultiple'],
    )

#### RUN ANALYSIS ####
if __name__ == '__main__':
    Analyzer.PARSER.add_argument('--color', dest='COLOR', action='store_true', help='whether to print reco matches in color'              )
    Analyzer.PARSER.add_argument('--dump' , dest='DUMP' , action='store_true', help='whether to dump detailed information about the event')
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('begin', 'analyze', 'end'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('EVENT', 'GEN', 'DSAMUON'),
        PARAMS      = ARGS,
    )
