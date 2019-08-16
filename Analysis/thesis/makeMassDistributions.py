import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import DisplacedDimuons.Analysis.PlotterParser as PP
import DisplacedDimuons.Analysis.RootTools as RT

PP.PARSER.add_argument('--square', dest='SQUARE', action='store_true')
ARGS = PP.PARSER.parse_args()

FILES = {
    '2Mu2J' : R.TFile.Open('roots/MassDistributions_Trig_HTo2XTo2Mu2J.root')
}

WINDOWS = {
    20  : {'INT' : (0.  ,  40.), 'REBIN':None},
    50  : {'INT' : (0.  , 100.), 'REBIN':2   },
    150 : {'INT' : (0.  , 300.), 'REBIN':5   },
    350 : {'INT' : (0.  , 700.), 'REBIN':10  },
}

##############################
##### MASS DISTRIBUTIONS #####
##############################

def makeMassPlot(spList):
    mX = spList[0][1]

    h = HG.getHistogram(FILES['2Mu2J'], ('2Mu2J', spList[0]), 'mass')
    for sp in spList[1:]:
        h.Add(HG.getHistogram(FILES['2Mu2J'], ('2Mu2J', sp), 'mass'))

    p = Plotter.Plot(h, '', '', 'hist')

    if WINDOWS[mX]['REBIN'] is not None: p.Rebin(WINDOWS[mX]['REBIN'])
    p.GetXaxis().SetRangeUser(WINDOWS[mX]['INT'][0], WINDOWS[mX]['INT'][1])

    RT.addBinWidth(p)

    f = R.TF1('f', 'gaus', WINDOWS[mX]['INT'][0], WINDOWS[mX]['INT'][1])
    h.Fit('f', 'R')

    c = Plotter.Canvas(lumi='m_{{X}} = {} GeV'.format(mX), cWidth=600)
    c.addMainPlot(p)
    f.Draw('same')
    f.SetLineColor(R.kRed)
    sbox = c.setFitBoxStyle(p.plot)
    Plotter.MOVE_OBJECT(sbox, X=.4, NDC=True)
    sbox.SetTextColor(R.kRed)
    c.firstPlot.setColor(R.kBlue)
    c.firstPlot.scaleTitleOffsets(1.1, 'Y')
    c.cleanup('pdfs/MASS_2Mu2J_{}.pdf'.format(mX), mode='LUMI')

spLists = {}
for sp in SIGNALPOINTS:
    mX = sp[1]
    if mX not in spLists:
        spLists[mX] = []
    spLists[mX].append(sp)

for mX in spLists:
    makeMassPlot(spLists[mX])
