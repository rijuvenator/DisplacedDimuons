import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Analysis.Selector as Selector


#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    self.HistInit('pTRes_hits_less', ';(p_{T}^{reco} #minus p_{T}^{gen})/p_{T}^{gen}', 50, -1., 1.)
    self.HistInit('pTRes_hits_more', ';(p_{T}^{reco} #minus p_{T}^{gen})/p_{T}^{gen}', 50, -1., 1.)
    self.HistInit('pTRes_fpte_less', ';(p_{T}^{reco} #minus p_{T}^{gen})/p_{T}^{gen}', 50, -1., 1.)
    self.HistInit('pTRes_fpte_more', ';(p_{T}^{reco} #minus p_{T}^{gen})/p_{T}^{gen}', 50, -1., 1.)

    self.HistInit('qdiff_hits_less', ';q^{reco} #minus q^{gen}', 5, -2.5, 2.5)
    self.HistInit('qdiff_hits_more', ';q^{reco} #minus q^{gen}', 5, -2.5, 2.5)
    self.HistInit('qdiff_fpte_less', ';q^{reco} #minus q^{gen}', 5, -2.5, 2.5)
    self.HistInit('qdiff_fpte_more', ';q^{reco} #minus q^{gen}', 5, -2.5, 2.5)


# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.TRIGGER and self.SP is not None:
        if not Selections.passedTrigger(E): return

    DSAmuons = E.getPrimitives('DSAMUON')

    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)


    f = {}
    f['pTRes'] = lambda reco, gen : (reco.pt - gen.BS.pt) / (gen.BS.pt if gen.BS.pt > 1.e-10 else 1.e-10)
    f['qdiff'] = lambda reco, gen : reco.charge - gen.charge

    for muon in DSAmuons:
        matches = AT.matchedMuons(muon, genMuons, vertex='BS')
        if len(matches) > 0:
            gen = matches[0]['muon']

            nHits, fpte = muon.nCSCHits+muon.nDTHits, muon.ptError/muon.pt
            whichHits = 'hits' + ('_less' if nHits <= 12 else '_more')
            whichFPTE = 'fpte' + ('_less' if fpte  <= 1. else '_more')

            self.HISTS['pTRes_'+whichHits].Fill(f['pTRes'](muon, gen))
            self.HISTS['qdiff_'+whichHits].Fill(f['qdiff'](muon, gen))
            self.HISTS['pTRes_'+whichFPTE].Fill(f['pTRes'](muon, gen))
            self.HISTS['qdiff_'+whichFPTE].Fill(f['qdiff'](muon, gen))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DSAMUON', 'TRIGGER', 'GEN'),
    )

    # write plots
    analyzer.writeHistograms('roots/mcbg/ResolutionPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
