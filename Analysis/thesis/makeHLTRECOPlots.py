import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import DisplacedDimuons.Analysis.PlotterParser as PP
import DisplacedDimuons.Analysis.RootTools as RT
import itertools

PP.PARSER.add_argument('--square', dest='SQUARE', action='store_true')
PP.PARSER.add_argument('--tag'   , dest='TAG'   , default='DSAReqPlusPTPlusEta')
ARGS = PP.PARSER.parse_args()

FILES = {
    '2Mu2J' : R.TFile.Open('roots/HLTRECOPlots_Trig_{}_HTo2XTo2Mu2J.root'.format(ARGS.TAG))
}

def makeEffPlot(fs, sp, quantity, region):
    if sp is None:
        hDen = HG.getAddedSignalHistograms(FILES[fs], fs, '{}-Den-{}'.format(quantity,region))['{}-Den-{}'.format(quantity,region)]
        hNum = HG.getAddedSignalHistograms(FILES[fs], fs, '{}-Eff-{}'.format(quantity,region))['{}-Eff-{}'.format(quantity,region)]
        prettyFS = '2#mu' if '2Mu' in fs else '4#mu'
        lumi = 'H#rightarrow2X#rightarrow{}, all samples combined{}{}'.format(prettyFS, ' + trigger' if ARGS.TRIGGER else '', ' wrt acc.' if region=='Acc' else '')
    else:
        hDen = HG.getHistogram(FILES[fs], (fs, sp), '{}-Den-{}'.format(quantity,region)).Clone()
        hNum = HG.getHistogram(FILES[fs], (fs, sp), '{}-Eff-{}'.format(quantity,region)).Clone()
        prettyFS = '2#mu' if '2Mu' in fs else '4#mu'
        lumi = 'H#rightarrow2X#rightarrow{} ({} GeV, {} GeV, {} mm){}{}'.format(prettyFS, sp[0], sp[1], sp[2], ' + trigger' if ARGS.TRIGGER else '', ' wrt acc.' if region=='Acc' else '')

    spstr = '{:4d} {:3d} {:4d}'.format(*sp) if sp is not None else '{:4s} {:3s} {:4s}'.format('', '', '')
    hNumInt = hNum.Integral(0,hNum.GetNbinsX()+1)
    hDenInt = hDen.Integral(0,hDen.GetNbinsX()+1)
    print '\033[m{:19s} {:5s} {:3s} {:13s} {:6.0f} {:6.0f} {:6.2%}\033[m'.format(ARGS.TAG, quantity, region, spstr, hNumInt, hDenInt, hNumInt/hDenInt)

    #c = Plotter.Canvas(lumi=lumi, cWidth=600 if ARGS.SQUARE else 800)
    #hNum.Rebin(10)
    #hDen.Rebin(10)
    #g = R.TGraphAsymmErrors(hNum, hDen, 'cp')
    #p = Plotter.Plot(g, '', 'l', 'p')
    #c.addMainPlot(p)
    #p.setColor(R.kBlue, which='LM')

    #c.firstPlot.SetMinimum(0.)
    #c.firstPlot.SetMaximum(1.)
    #c.firstPlot.setTitles(X='', Y='', copy=hNum)
    #if ARGS.SQUARE:
    #    c.firstPlot.scaleTitleOffsets(1.1, 'X')

    #c.cleanup('pdfs/HLT-EFF_{}_{}_{}_{}_{}.pdf'.format(ARGS.TAG, quantity, region, fs, 'Global' if sp is None else SPStr(sp)), mode='LUMI')

for fs in FILES:
    for sp in itertools.chain(SIGNALPOINTS, [None]):
        #for quantity in ('Lxy', 'subPT'):
        for quantity in ('Lxy',):
            for region in ('Nom',):
            #for region in ('Nom', 'Acc'):
                makeEffPlot(fs, sp, quantity, region)
