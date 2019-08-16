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
    '2Mu2J' : R.TFile.Open('roots/NM1Distributions_Trig_HTo2XTo2Mu2J.root'),
    'Data'  : R.TFile.Open('roots/NM1Distributions_IDPHI_DATA.root')
}

CUTS = {
    'deltaPhi' : {'val':R.TMath.Pi()/4., 'logy':True, 'lumi':'|#Delta#Phi| < #pi/4'},
    'pT'       : {'val':10., 'logy':True, 'lumi':'p_{T} > 10 GeV'            },
    'DCA'      : {'val':50., 'logy':True, 'lumi':'D.C.A. < 50 cm'            },
    'vtxChi2'  : {'val':20., 'logy':True, 'lumi':'vtx. #chi^{2} < 20'        },
    'cosAlpha' : {'val':-.8, 'logy':True, 'lumi':'cos(#alpha) > #minus0.8'   },
    'Npp'      : {'val':6. , 'logy':True, 'lumi':'N(parallel pairs) < 6'     },
    'trkChi2'  : {'val':2.5, 'logy':True, 'lumi':'trk. #chi^{2}/dof < 2.5'   },
    'nDTHits'  : {'val':18., 'logy':True, 'lumi':'barrel N(DT Hits) > 18'    },
    'LxySig'   : {'val':6. , 'logy':True, 'lumi':'L_{xy}/#sigma_{L_{xy}} > 6'},
}

def getEff(p, key):
    nBins = p.GetNbinsX()
    den = p.Integral(0, nBins+1)
    if key == 'Npp':
        num = p.Integral(0, 5)
    elif '<' in CUTS[key]['lumi']:
        num = p.Integral(0, p.FindBin(CUTS[key]['val']))
    else:
        num = p.Integral(p.FindBin(CUTS[key]['val']), nBins+1)

    try:
        return num/den
    except:
        return 0.

################################
##### SIGNAL DISTRIBUTIONS #####
################################

def makeSignalPlot(key):
    h = HG.getAddedSignalHistograms(FILES['2Mu2J'], '2Mu2J', key)
    h = h[key]

    p = Plotter.Plot(h, '', '', 'hist')

    RT.addBinWidth(p)

    c = Plotter.Canvas(lumi='H#rightarrow2X#rightarrow2#mu, {}'.format(CUTS[key]['lumi']), cWidth=600 if key != 'deltaPhi' else 800, logy=CUTS[key]['logy'])
    c.addMainPlot(p)
    c.firstPlot.setColor(R.kBlue)
    c.firstPlot.scaleTitleOffsets(1.1, 'Y')

    if key == 'deltaPhi':
        axis = c.firstPlot.GetXaxis()
        labeldict = {1:'0', 25:'#pi/4', 50:'#pi/2', 75:'3#pi/4', 100:'#pi'}
        for i in xrange(1, 101):
            val = labeldict.get(i)
            if val is None: val = ''
            axis.SetBinLabel(i, val)
        axis.SetNdivisions(216, False)
        axis.SetLabelSize(.06)
        axis.SetTickLength(0.03)
        axis.SetTickSize(0.03)
        axis.LabelsOption('h')

        c.mainPad.Update()
        ymin = c.mainPad.GetUymin()
        ymax = c.mainPad.GetUymax()
        if c.logy:
            ymax = 10.**ymax

        xB = R.TGaxis(0., ymin, R.TMath.Pi()-.07, ymin, 0., R.TMath.Pi(), 216, "+B", .03)
        xB.SetLabelSize(0)
        xB.Draw('same')

        xT = R.TGaxis(0., ymax, R.TMath.Pi()-.07, ymax, 0., R.TMath.Pi(), 216, "-B", .03)
        xT.SetLabelSize(0)
        xT.Draw('same')

    if key == 'pT':
        c.firstPlot.GetXaxis().SetRangeUser(0., 600.)


    eff = getEff(p, key)
    c.drawText('{:.1%} efficient'.format(eff), align='tr', pos=(1.-c.margins['r']-.03, 1.-c.margins['t']-.03))

    c.mainPad.Update()
    ymax = c.mainPad.GetUymax()
    line = R.TLine(CUTS[key]['val'], 0., CUTS[key]['val'], ymax if not c.logy else 10.**ymax)
    line.SetLineStyle(2)
    line.Draw()

    if key == 'trkChi2': c.firstPlot.GetXaxis().SetTitle('trk. #chi^{2}/dof')

    c.cleanup('pdfs/NM1_2Mu2J_{}.pdf'.format(key), mode='LUMI')

for key in CUTS:
    makeSignalPlot(key)

##############################
##### DATA DISTRIBUTIONS #####
##############################

def makeDataPlot(key):
    h, pconfig = HG.getDataHistograms(FILES['Data'], key)
    h = h[key]['data']

    p = Plotter.Plot(h, '', '', 'pe')

    RT.addBinWidth(p)

    c = Plotter.Canvas(lumi='Data 2016, 36.3 fb^{{-1}} (13 TeV), {}'.format(CUTS[key]['lumi']), cWidth=600 if key != 'deltaPhi' else 800, logy=CUTS[key]['logy'])
    c.addMainPlot(p)
    c.firstPlot.setColor(R.kBlack)
    c.firstPlot.scaleTitleOffsets(1.1, 'Y')

    if key == 'deltaPhi':
        axis = c.firstPlot.GetXaxis()
        labeldict = {1:'0', 25:'#pi/4', 50:'#pi/2', 75:'3#pi/4', 100:'#pi'}
        for i in xrange(1, 101):
            val = labeldict.get(i)
            if val is None: val = ''
            axis.SetBinLabel(i, val)
        axis.SetNdivisions(216, False)
        axis.SetLabelSize(.06)
        axis.SetTickLength(0.03)
        axis.SetTickSize(0.03)
        axis.LabelsOption('h')

        c.mainPad.Update()
        ymin = c.mainPad.GetUymin()
        ymax = c.mainPad.GetUymax()
        if c.logy:
            ymax = 10.**ymax

        xB = R.TGaxis(0., ymin, R.TMath.Pi()-.07, ymin, 0., R.TMath.Pi(), 216, "+B", .03)
        xB.SetLabelSize(0)
        xB.Draw('same')

        xT = R.TGaxis(0., ymax, R.TMath.Pi()-.07, ymax, 0., R.TMath.Pi(), 216, "-B", .03)
        xT.SetLabelSize(0)
        xT.Draw('same')

    if key == 'pT':
        c.firstPlot.GetXaxis().SetRangeUser(0., 600.)

    eff = getEff(p, key)
    c.drawText('{:.1%} efficient'.format(eff), align='tr', pos=(1.-c.margins['r']-.03, 1.-c.margins['t']-.03))

    c.mainPad.Update()
    ymax = c.mainPad.GetUymax()
    line = R.TLine(CUTS[key]['val'], 0., CUTS[key]['val'], ymax if not c.logy else 10.**ymax)
    line.SetLineStyle(2)
    line.Draw()

    if key == 'trkChi2': c.firstPlot.GetXaxis().SetTitle('trk. #chi^{2}/dof')

    c.cleanup('pdfs/NM1_Data_{}.pdf'.format(key), mode='LUMI')

for key in CUTS:
    makeDataPlot(key)
