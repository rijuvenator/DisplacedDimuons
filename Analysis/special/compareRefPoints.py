import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities
from DisplacedDimuons.Analysis.AnalysisTools import matchedMuons, matchedDimuons

# note the explicit abs around the gen d0. in the old version of the nTuples, the sign was dropped; in the new version, it is kept.
CONFIG = {
    'Lxy': ('L_{xy}', (100,-100.,100.), lambda dim, extrap: dim.Lxy()             , lambda gmu, extrap: gmu.Lxy()                 , lambda rq, gq: rq-gq),
    'd0G': ('d_{0}' , (100, -50., 50.), lambda rmu, extrap: rmu.d0(extrap=extrap) , lambda gmu, extrap: abs(gmu.d0(extrap=extrap)), lambda rq, gq: rq-gq),
}

#### CLASS AND FUNCTION DEFINITIONS ####
# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for QUANTITY in ('Lxy', 'd0G'):
        PRETTY, AXES, RFUNC, GFUNC, RESFUNC = CONFIG[QUANTITY]
        self.HistInit(QUANTITY+'ResZZ', ';'+PRETTY+' Res;Counts', *AXES)
        self.HistInit(QUANTITY+'ResBS', ';'+PRETTY+' Res;Counts', *AXES)

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    if self.SP is None:
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    if self.TRIGGER:
        if not Selections.passedTrigger(E): return
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
        genMuonPairs = ((mu1, mu2),)
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    TAG = 'ZZ' if self.ARGS.OLD else 'BS'

    # In order for this to work on the "old" nTuples, i.e. previous to the changes to gen muons with BS quantities,
    # the following changes need to be made to Primitives.GenMuon in order to make it backwards-compatible:
    # - wrap the .BS declaration in a try-except: we do not use it here, so the old nTuples will still work
    # - wrap the d0 and dz declarations in a try-except: these only fail for the "extra" gen muons; in the old nTuples,
    #   extra gen muons did not fill the d0 and dz quantities

    for genMuonPair in genMuonPairs:
        dimuonMatches, muonMatches, exitcode = matchedDimuons(genMuonPair, Dimuons, DSAmuons, vertex=None)
        if len(dimuonMatches) > 0:
            dimuon = Dimuons[dimuonMatches[0]['idx']]
            recoMuons = dimuon.mu1, dimuon.mu2
            for QUANTITY in ('Lxy',):
                PRETTY, AXES, RFUNC, GFUNC, RESFUNC = CONFIG[QUANTITY]
                if True:
                    self.HISTS[QUANTITY+'Res{}'.format(TAG)].Fill(RESFUNC(RFUNC(dimuon, 'LIN'), GFUNC(genMuonPair[0], 'LIN')))
            for QUANTITY in ('d0G',):
                PRETTY, AXES, RFUNC, GFUNC, RESFUNC = CONFIG[QUANTITY]
                for recoMuon, genMuon in zip(recoMuons, genMuonPair):
                    self.HISTS[QUANTITY+'Res{}'.format(TAG)].Fill(RESFUNC(RFUNC(recoMuon, 'LIN'), GFUNC(genMuon, 'LIN')))

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    Analyzer.PARSER.add_argument('--old', dest='OLD', action='store_true')
    ARGS = Analyzer.PARSER.parse_args()

    if ARGS.OLD:
        fs = '4Mu' if '4Mu' in ARGS.NAME else '2Mu2J'
        sp = '_'.join(map(str, ARGS.SIGNALPOINT))
        FILES = '/eos/cms/store/user/adasgupt/DisplacedDimuons/NTuples/PreBS/ntuple_HTo2XTo{}_{}.root'.format(fs, sp)
    else:
        FILES = None

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('declareHistograms', 'analyze',):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DSAMUON', 'GEN', 'DIMUON'),
        FILES       = FILES
    )

    # write plots
    analyzer.writeHistograms('roots/RefPointTest{}{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else '', '_Old' if ARGS.OLD else '_New'))
