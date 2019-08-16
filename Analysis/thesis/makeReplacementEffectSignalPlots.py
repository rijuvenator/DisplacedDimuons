import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import DisplacedDimuons.Analysis.PlotterParser as PP

PP.PARSER.add_argument('--square', dest='SQUARE', action='store_true')
ARGS = PP.PARSER.parse_args()

FILES = {
    'Signal': R.TFile.Open('roots/RepEffectPlots_Signal.root'),
}

def makeRepEffectPlots(sp=None):

    lumi = 'H#rightarrow2X#rightarrow2#mu'
    if sp is None:
        lumi += ', all samples combined'
    else:
        lumi += ' ({} GeV, {} GeV, {} mm)'.format(*sp)

    hkeys = ('Lxy-before', 'Lxy-after')
    if sp is None:
        HISTS = HG.getAddedSignalHistograms(FILES['Signal'], '2Mu2J', hkeys)
    else:
        HISTS = {}
        for key in hkeys:
            HISTS[key] = HG.getHistogram(FILES['Signal'], ('2Mu2J', sp), key).Clone()

    nPass = HISTS['Lxy-after' ].Integral(HISTS['Lxy-after' ].GetXaxis().FindBin(65.), HISTS['Lxy-after' ].GetNbinsX()+1)
    nTot  = HISTS['Lxy-before'].Integral(HISTS['Lxy-before'].GetXaxis().FindBin(65.), HISTS['Lxy-before'].GetNbinsX()+1)
    print nPass/nTot

    for key in hkeys: HISTS[key].Rebin(2)
    g = R.TGraphAsymmErrors(HISTS['Lxy-after'], HISTS['Lxy-before'], 'cp')
    p = Plotter.Plot(g, '', '', 'p')

    canvas = Plotter.Canvas(lumi=lumi, cWidth=600 if ARGS.SQUARE else 800)
    canvas.addMainPlot(p)
    p.setColor(R.kBlue)

    canvas.firstPlot.setTitles(X='generated L_{xy} [cm]', Y='Dimuons after / before association')

    canvas.firstPlot.SetMaximum(1.)
    canvas.firstPlot.SetMinimum(0.)

    if ARGS.SQUARE:
        canvas.firstPlot.scaleTitleOffsets(1.1, 'X')
    canvas.cleanup('pdfs/REPEFF_Signal_{}.pdf'.format('Global' if sp is None else SPStr(sp)), mode='LUMI')

makeRepEffectPlots()
