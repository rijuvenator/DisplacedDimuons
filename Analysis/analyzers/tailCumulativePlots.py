import math
import re
import ROOT as R
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Common.Utilities as Utilities

def getNM1Hists(ARGS):
    if ARGS.NAME.startswith('HTo2X'):
        SIGNALPOINT = Utilities.SignalPoint(ARGS.SIGNALPOINT)
        NAME = ARGS.NAME + '_' + SIGNALPOINT.SPStr()
    else:
        NAME = ARGS.NAME

    F_NM1 = R.TFile.Open('roots/nMinusOnePlots_{}.root'.format(NAME))

    NM1HISTS = {'Less' : {}, 'More' : {}}
    for KEY in CUTKEYS:
        for DeltaPhiRange in ('Less', 'More'):
            NM1HISTS[DeltaPhiRange][KEY] = F_NM1.Get(KEY+'_'+DeltaPhiRange+'_'+NAME)
            NM1HISTS[DeltaPhiRange][KEY].SetDirectory(0)
    return NM1HISTS

# set up a configuration dictionary with the same cut keys as in Selections
CUTKEYS = {
    'd0Sig'    : {},
    'LxySig'   : {},
}
for KEY in CUTKEYS:
    # the title is ;XTITLE;Counts
    CUTKEYS[KEY]['TITLE'] = ';' + Selections.PrettyTitles[KEY] + ';Counts'

# function for writing KEY_Less or KEY_More
def NAME(KEY, DeltaPhiRegion):
    return KEY + '_' +  DeltaPhiRegion

# declare histograms for Analyzer class
def declareHistograms(self, PARAMS=None):
    for DeltaPhiRegion in ('Less', 'More'):
        for KEY in CUTKEYS:
            h = NM1HISTS[DeltaPhiRegion][KEY].GetCumulative(False)
            h.SetNameTitle(NAME(KEY, DeltaPhiRegion) + '_TCUM_' + self.NAME, CUTKEYS[KEY]['TITLE'])
            h.SetDirectory(0)
            self.HISTS[NAME(KEY, DeltaPhiRegion)] = h

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)

    NM1HISTS = getNM1Hists(ARGS)

    for METHOD in ('declareHistograms',):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DSAMUON', 'DIMUON'),
        TREELOOP    = False
    )
    analyzer.writeHistograms('roots/TailCumulativePlots_{}.root')
