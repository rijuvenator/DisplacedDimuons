import ROOT as R
import DisplacedDimuons.Analysis.STest as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer

# internal loop function for Analyzer class
def analyze(self, E, PARAMS=None):
    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3 = E.getPrimitives('DIMUON')
    Event    = E.getPrimitives('EVENT')

    cutkeys = ('b_LxyErr', 'b_mass', 'm_vtxChi2', 'm_d0Sig')
    funcs = (lambda d:d.LxyErr(), lambda d:d.mass, lambda d:d.normChi2, lambda d:[d.mu1.d0Sig(), d.mu2.d0Sig()])
    funcs = dict(zip(cutkeys, funcs))
    for dim in Dimuons3:
        valueString = ''
        for cutkey in cutkeys:
            result = Selections.CUTS[cutkey].apply(dim)

            if result:
                valueString += '\033[32m'
            else:
                valueString += '\033[31m'

            if 'd0' in cutkey:
                valueString += '{:6.2f} {:6.2f}'.format(*funcs[cutkey](dim))
            else:
                valueString += '{:6.2f} '.format(funcs[cutkey](dim))
            valueString += '\033[m'

        print '{:13s} {:d} {:7d} {:10d} ::: {:3s} {:2d} {:2d} ::: {:s}'.format(
            self.NAME, Event.run, Event.lumi, Event.event,
            dim.composition[:3], dim.idx1, dim.idx2,
            valueString
        )
    print ''

#### RUN ANALYSIS ####
if __name__ == '__main__':
    # get arguments
    ARGS = Analyzer.PARSER.parse_args()

    # set sample object based on arguments
    Analyzer.setSample(ARGS)

    # define Analyzer methods
    for METHOD in ('analyze',):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])

    # declare analyzer
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DIMUON', 'PATMUON', 'DSAMUON', 'TRIGGER', 'GEN', 'EVENT'),
    )
