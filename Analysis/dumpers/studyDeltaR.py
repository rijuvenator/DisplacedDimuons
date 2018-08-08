# -*- coding: utf-8 -*-
import math
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    pass
    #self.HistInit('pT_Gen', '', 100, 0., 500.)
    #self.HistInit('pT_Reco', '', 100, 0., 500.)

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

    SelectMuons = False
    # require reco muons to pass all selections
    if SelectMuons:
        DSASelections = [Selections.MuonSelection(muon) for muon in DSAmuons]
        selectedDSAmuons = [mu for idx,mu in enumerate(DSAmuons) if DSASelections[idx]]

    # don't require reco muons to pass all selections
    else:
        selectedDSAmuons = DSAmuons
    
    # fill histograms only for matched reco muons
    for genMuon in genMuons:
        # cut genMuons outside the detector acceptance
        # don't do it for now
        #genMuonSelection = Selections.AcceptanceSelection(genMuon)

        for MUON, recoMuons in (('DSA', selectedDSAmuons),):
            matches = matchedMuons(genMuon, recoMuons)
            if len(matches) > 0:
                closestMuon = recoMuons[matches[0]['idx']]
                #self.HISTS['pT_Reco'].Fill(closestMuon.pt)
                #self.HISTS['pT_Gen'].Fill(genMuon.pt)
                MODE = 1
                # print genMuons with closest matches > 0.2
                if MODE == 1:
                    if genMuon.p4.DeltaR(closestMuon.p4) > 0.2:
                        dumpInfo(Event, genMuon, genMuons, selectedDSAmuons, len(matches), extramu, PARAMS)
                # print genMuons with closest matches > 0.2 passing the pT cut
                elif MODE == 2:
                    if genMuon.p4.DeltaR(closestMuon.p4) > 0.2 and closestMuon.pt > 30.:
                        dumpInfo(Event, genMuon, genMuons, selectedDSAmuons, len(matches), extramu, PARAMS)
                # print genMuons with closest matches > 0.2 not passing the pT cut,
                # but which have another recoMuon with higher pT and nearby deltaPhi
                elif MODE == 3:
                    if genMuon.p4.DeltaR(closestMuon.p4) > 0.2 and closestMuon.pt < 30.:
                        betterMuonsExist = False
                        for recoMuon in recoMuons:
                            if recoMuon.idx == matches[0]['idx']: continue
                            if recoMuon.pt > 30. and abs(recoMuon.p4.DeltaPhi(genMuon.p4)) < 0.1:
                                betterMuonsExist = True
                        if betterMuonsExist:
                            dumpInfo(Event, genMuon, genMuons, selectedDSAmuons, len(matches), extramu, PARAMS)

# dump info
def dumpInfo(Event, selectedGenMuon, genMuons, DSAmuons, nMatches, extramu, PARAMS):
    print '=== Run LS Event : {} {} {} ==='.format(Event.run, Event.lumi, Event.event)

    print 'Gen Muon:      {:10.4f} {:12s} {:7.4f} {:7.4f} {:9.4f} {:2d}'.format(
            selectedGenMuon.pt,
            '',
            selectedGenMuon.eta,
            selectedGenMuon.phi,
            selectedGenMuon.Lxy(),
            nMatches
    )
    for genMuon in genMuons:
        if genMuon.pdgID == selectedGenMuon.pdgID: continue
        print 'Gen Muon:      {:10.4f} {:12s} {:7.4f} {:7.4f} {:9.4f} {:2d}'.format(
                genMuon.pt,
                '',
                genMuon.eta,
                genMuon.phi,
                genMuon.Lxy(),
                nMatches
        )
    for muon in DSAmuons:
        fstring = '  Reco Muon:   {:10.4f} {:1s}{:11.4f} {:7.4f} {:7.4f} {:9s} {:2s} {:7.4f} {:2d} {:2d} {:2d} {:2d} {:2d}'.format(
            muon.pt,
            '±',
            muon.ptError,
            muon.eta,
            muon.phi,
            '',
            '',
            muon.p4.DeltaR(selectedGenMuon.p4),
            muon.nDTStations,
            muon.nCSCStations,
            muon.nDTHits,
            muon.nCSCHits,
            muon.nMuonHits
        )
        if muon.p4.DeltaR(selectedGenMuon.p4) < 0.3:
            if PARAMS.COLOR:
                fstring = '\033[31m' + fstring + '\033[m'
            else:
                fstring = '*' + fstring[1:]
        elif muon.pt > 30. and abs(muon.p4.DeltaPhi(selectedGenMuon.p4)) < 0.1:
            if PARAMS.COLOR:
                fstring = '\033[32m' + fstring + '\033[m'
            else:
                fstring = '+' + fstring[1:]
        print fstring
    for extraGen in extramu:
        print 'Extra GenMuon: {:10.4f} {:12s} {:7.4f} {:7.4f}'.format(
                extraGen.pt,
                '',
                extraGen.eta,
                extraGen.phi,
        )
    print ''

#### RUN ANALYSIS ####
if __name__ == '__main__':
    Analyzer.PARSER.add_argument('--color', dest='COLOR', action='store_true', help='whether to print reco matches in color'              )
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('analyze', 'declareHistograms'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('EVENT', 'DSAMUON', 'GEN'),
        PARAMS      = ARGS,
    )
    #analyzer.writeHistograms('deltaRTest_{}.root')
