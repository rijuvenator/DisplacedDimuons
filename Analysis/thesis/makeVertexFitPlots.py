import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.PlotterParser as PP

PP.PARSER.add_argument('--square', dest='SQUARE', action='store_true')
ARGS = PP.PARSER.parse_args()

FILES = {
    '2Mu2J' : R.TFile.Open('roots/VertexFitPlots_HTo2XTo2Mu2J.root')
}

#################################
##### VERTEX FIT EFFICIENCY #####
#################################

def makeEffPlot(fs, sp):
    hNum = HG.getHistogram(FILES[fs], (fs, sp), 'LxyEff').Clone()
    hDen = HG.getHistogram(FILES[fs], (fs, sp), 'LxyDen').Clone()

    hNum.Rebin(10)
    hDen.Rebin(10)

    g = R.TGraphAsymmErrors(hNum, hDen, 'cp')

    p = Plotter.Plot(g, '', '', 'p')

    prettyFS = '2#mu' if '2Mu' in fs else '4#mu'
    c = Plotter.Canvas(lumi='H#rightarrow2X#rightarrow{} ({} GeV, {} GeV, {} mm)'.format(prettyFS, *sp), cWidth=600 if ARGS.SQUARE else 800)

    c.addMainPlot(p)
    p.setColor(R.kBlue, which='LM')

    c.firstPlot.SetMinimum(0.)
    c.firstPlot.SetMaximum(1.)
    c.firstPlot.setTitles(X='', Y='', copy=hNum)

    if ARGS.SQUARE:
        c.firstPlot.scaleTitleOffsets(1.1, 'X')
    c.cleanup('pdfs/VFE_Lxy_{}_{}_{}_{}.pdf'.format(fs, *sp), mode='LUMI')

for fs in FILES:
    for sp in ((1000, 350, 3500), (400, 150, 4000)):
        makeEffPlot(fs, sp)

#########################
##### LESS AND MORE #####
#########################

def makeLessMorePlot(fs, sp, quantity):
    h = {
        'Less' : HG.getHistogram(FILES[fs], (fs, sp), '{}-Less'.format(quantity)).Clone(),
        'More' : HG.getHistogram(FILES[fs], (fs, sp), '{}-More'.format(quantity)).Clone(),
    }

    for key in h:
        try:
            h[key].Scale(1./h[key].Integral())
        except:
            return

    pretty = {
        'Less':{'leg':'L_{xy} < 320 cm', 'col':R.kBlue},
        'More':{'leg':'L_{xy} > 320 cm', 'col':R.kRed },
    }

    p = {key:Plotter.Plot(h[key], pretty[key]['leg'], 'l', 'hist') for key in h}

    prettyFS = '2#mu' if '2Mu' in fs else '4#mu'
    c = Plotter.Canvas(lumi='H#rightarrow2X#rightarrow{} ({} GeV, {} GeV, {} mm)'.format(prettyFS, *sp), cWidth=600 if ARGS.SQUARE else 800)

    for key in p:
        c.addMainPlot(p[key])
        p[key].setColor(pretty[key]['col'], which='LM')

    RT.addBinWidth(c.firstPlot)
    c.makeLegend(lWidth=0.125, pos='tr')
    c.legend.resizeHeight()
    c.legend.moveLegend(X=-.4)
    c.setMaximum()
    
    if ARGS.SQUARE:
        c.firstPlot.scaleTitleOffsets(1.1, 'X')
    c.cleanup('pdfs/LESSMORE_{}_{}_{}_{}_{}.pdf'.format(quantity, fs, *sp), mode='LUMI')

for fs in FILES:
    for sp in ((1000, 350, 3500), (400, 150, 4000)):
    #for sp in SIGNALPOINTS:
        makeLessMorePlot(fs, sp, 'pTRes')
        makeLessMorePlot(fs, sp, 'LxyErr')
