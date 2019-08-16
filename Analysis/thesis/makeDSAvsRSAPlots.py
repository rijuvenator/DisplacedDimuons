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
    '2Mu2J' : R.TFile.Open('roots/DSAVSRSAPlots{}_HTo2XTo2Mu2J.root'.format('_Trig' if ARGS.TRIGGER else ''))
}

MUONS = ['DSA', 'RSA']

#####################################
##### RECONSTRUCTION EFFICIENCY #####
#####################################

def makeEffPlot(fs, sp):
    if sp is None:
        hNum = HG.getAddedSignalHistograms(FILES[fs], fs, ['nRec'+MUON for MUON in MUONS])
        hDen = HG.getAddedSignalHistograms(FILES[fs], fs, ['nGen'+MUON for MUON in MUONS])
        prettyFS = '2#mu' if '2Mu' in fs else '4#mu'
        lumi = 'H#rightarrow2X#rightarrow{}, all samples combined{}'.format(prettyFS, ' + trigger' if ARGS.TRIGGER else '')
    else:
        hNum, hDen = {}, {}
        for MUON in MUONS:
            hNum['nRec'+MUON] = HG.getHistogram(FILES[fs], (fs, sp), 'nRec'+MUON).Clone()
            hDen['nGen'+MUON] = HG.getHistogram(FILES[fs], (fs, sp), 'nGen'+MUON).Clone()
        prettyFS = '2#mu' if '2Mu' in fs else '4#mu'
        lumi = 'H#rightarrow2X#rightarrow{} ({} GeV, {} GeV, {} mm){}'.format(prettyFS, sp[0], sp[1], sp[2], ' + trigger' if ARGS.TRIGGER else '')

    c = Plotter.Canvas(lumi=lumi, cWidth=600 if ARGS.SQUARE else 800)
    pretty = {'DSA':{'col':R.kBlue}, 'RSA':{'col':R.kRed}}
    g, p = {}, {}
    for MUON in MUONS:
        hNum['nRec'+MUON].Rebin(10)
        hDen['nGen'+MUON].Rebin(10)
        g[MUON] = R.TGraphAsymmErrors(hNum['nRec'+MUON], hDen['nGen'+MUON], 'cp')
        p[MUON] = Plotter.Plot(g[MUON], MUON, 'l', 'p')
        c.addMainPlot(p[MUON])
        p[MUON].setColor(pretty[MUON]['col'], which='LM')

    c.makeLegend(lWidth=0.125, pos='bl')
    c.legend.resizeHeight()

    c.firstPlot.SetMinimum(0.)
    c.firstPlot.SetMaximum(1.)
    c.firstPlot.setTitles(X='', Y='', copy=hNum['nRecDSA'])
    if ARGS.SQUARE:
        c.firstPlot.scaleTitleOffsets(1.1, 'X')

    c.cleanup('pdfs/REFF_Lxy{}_{}_{}.pdf'.format('_Trig' if ARGS.TRIGGER else '', fs, 'Global' if sp is None else SPStr(sp)), mode='LUMI')

#########################
##### PT RESOLUTION #####
#########################

def makeResPlot(fs, sp):
    if sp is None:
        h = HG.getAddedSignalHistograms(FILES[fs], fs, ['pTRes-'+MUON for MUON in MUONS])
        prettyFS = '2#mu' if '2Mu' in fs else '4#mu'
        lumi = 'H#rightarrow2X#rightarrow{}, all samples combined{}'.format(prettyFS, ' + trigger' if ARGS.TRIGGER else '')
    else:
        h = {}
        for MUON in MUONS:
            h['pTRes-'+MUON] = HG.getHistogram(FILES[fs], (fs, sp), 'pTRes-'+MUON).Clone()
        prettyFS = '2#mu' if '2Mu' in fs else '4#mu'
        lumi = 'H#rightarrow2X#rightarrow{} ({} GeV, {} GeV, {} mm){}'.format(prettyFS, sp[0], sp[1], sp[2], ' + trigger' if ARGS.TRIGGER else '')

    c = Plotter.Canvas(lumi=lumi, cWidth=600 if ARGS.SQUARE else 800)
    pretty = {'DSA':{'col':R.kBlue}, 'RSA':{'col':R.kRed}}
    p = {}
    for MUON in MUONS:
        h['pTRes-'+MUON].Scale(1./h['pTRes-'+MUON].Integral(0, h['pTRes-'+MUON].GetNbinsX()+1))
        #h['pTRes-'+MUON].Rebin(10)
        p[MUON] = Plotter.Plot(h['pTRes-'+MUON], MUON, 'l', 'hist')
        c.addMainPlot(p[MUON])
        p[MUON].setColor(pretty[MUON]['col'], which='LM')

    c.makeLegend(lWidth=0.125, pos='tr')
    c.legend.resizeHeight()

    c.setMaximum()
    c.firstPlot.setTitles(X='', Y='', copy=h['pTRes-DSA'])
    RT.addBinWidth(c.firstPlot)
    if ARGS.SQUARE:
        c.firstPlot.scaleTitleOffsets(1.1, 'X')
        c.firstPlot.scaleTitleOffsets(1.3, 'Y')

    c.cleanup('pdfs/PTRES{}_{}_{}.pdf'.format('_Trig' if ARGS.TRIGGER else '', fs, 'Global' if sp is None else SPStr(sp)), mode='LUMI')

for fs in FILES:
    for sp in [None]:
        makeEffPlot(fs, sp)
        makeResPlot(fs, sp)

    for sp in ((1000, 350, 350),):
        makeResPlot(fs, sp)
