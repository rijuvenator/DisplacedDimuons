import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import HistogramGetter
import sys

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/SignalMatchResPlots.root')
f = R.TFile.Open('../analyzers/roots/SignalMatchResPlots.root')

# DSA RSA overlaid, per signal
def makeResPlots(quantity, fs):
    for sp in SIGNALPOINTS:
        DOFIT = quantity == 'pT'
        h = {
            'DSA' : HISTS[(fs, sp)]['DSA_'+quantity+'Res'],
            'RSA' : HISTS[(fs, sp)]['RSA_'+quantity+'Res']
        }
        p = {}
        for MUON in h:
            p[MUON] = Plotter.Plot(h[MUON], 'H#rightarrow2X#rightarrow4#mu MC ({})'.format(MUON), 'l', 'hist')
        fname = 'pdfs/SMR_{}_HTo2XTo{}_{}.pdf'.format(quantity+'Res', fs, SPStr(sp))

        if DOFIT:
            funcs = {}
            fplots = {}
            for MUON in h:
                funcs[MUON] = R.TF1('f'+MUON, 'gaus', -0.5, 0.4)
                h[MUON].Fit('f'+MUON)
                fplots[MUON] = Plotter.Plot(funcs[MUON], 'Gaussian fit ({})'.format(MUON), 'l', '')

        canvas = Plotter.Canvas(lumi='({}, {}, {})'.format(*sp))
        canvas.addMainPlot(p['DSA'])
        canvas.addMainPlot(p['RSA'], addS=True)

        canvas.firstPlot.setTitles(X=canvas.firstPlot.GetXaxis().GetTitle().replace('DSA','Reco'))

        if DOFIT:
            canvas.addMainPlot(fplots['DSA'])
            canvas.addMainPlot(fplots['RSA'])

        canvas.makeLegend(lWidth=.25, pos='tr' if quantity == 'pT' else 'tl')
        canvas.legend.moveLegend(X=-.3 if quantity == 'pT' else 0.)
        canvas.legend.resizeHeight()

        p['DSA'].SetLineColor(R.kBlue)
        p['RSA'].SetLineColor(R.kRed)

        canvas.drawText('#color[4]{' + '#bar{{x}} = {:.4f}'   .format(h['DSA'].GetMean())   + '}', (.75, .8    ))
        canvas.drawText('#color[4]{' + 's = {:.4f}'           .format(h['DSA'].GetStdDev()) + '}', (.75, .8-.04))
        canvas.drawText('#color[2]{' + '#bar{{x}} = {:.4f}'   .format(h['RSA'].GetMean())   + '}', (.75, .8-.08))
        canvas.drawText('#color[2]{' + 's = {:.4f}'           .format(h['RSA'].GetStdDev()) + '}', (.75, .8-.12))

        if DOFIT:
            fplots['DSA'].SetLineColor(R.kBlack)
            fplots['RSA'].SetLineColor(R.kGreen+1)

            canvas.setFitBoxStyle(h['DSA'], lWidth=0.35, pos='tr')
            canvas.setFitBoxStyle(h['RSA'], lWidth=0.35, pos='tr')

            p['DSA'].FindObject('stats').SetTextColor(R.kBlack)
            Plotter.MOVE_OBJECT(p['DSA'].FindObject('stats'), Y=-.25, NDC=True)

            p['RSA'].FindObject('stats').SetTextColor(R.kGreen+1)
            Plotter.MOVE_OBJECT(p['RSA'].FindObject('stats'), Y=-.5, NDC=True)

        canvas.cleanup(fname)

# DSA plot or RSA plot only (used here for DSA Lxy)
def makeResPlotsSingle(quantity, fs, MUON):
    for sp in SIGNALPOINTS:
        h = HISTS[(fs, sp)][MUON+'_'+quantity+'Res']
        p = Plotter.Plot(h, 'H#rightarrow2X#rightarrow4#mu MC ({})'.format(MUON), 'l', 'hist')
        fname = 'pdfs/SMR_{}_{}_HTo2XTo{}_{}.pdf'.format(MUON, quantity+'Res', fs, SPStr(sp))

        canvas = Plotter.Canvas(lumi='({}, {}, {})'.format(*sp))
        canvas.addMainPlot(p)

        canvas.makeLegend(lWidth=.25, pos='tr' if quantity == 'pT' else 'tl')
        canvas.legend.moveLegend(X=-.3 if quantity == 'pT' else 0.)
        canvas.legend.resizeHeight()

        p.SetLineColor(R.kBlue)

        canvas.drawText('#color[4]{' + '#bar{{x}} = {:.4f}'   .format(h.GetMean())   + '}', (.75, .8    ))
        canvas.drawText('#color[4]{' + 's = {:.4f}'           .format(h.GetStdDev()) + '}', (.75, .8-.04))

        canvas.cleanup(fname)

# make 3D color plots
def makeColorPlot(MUON, quantity, fs='4Mu', q2=None):
    if q2 is None:
        fstring = '{M}_{Q}VS{Q}_HTo2XTo{FS}_'.format(M=MUON, Q=quantity, FS=fs)
    else:
        fstring = '{M}_{Q}ResVS{Q2}_HTo2XTo{FS}_'.format(M=MUON, Q=quantity, FS=fs, Q2=q2)

    for i, sp in enumerate(SIGNALPOINTS):
        if i == 0:
            h = f.Get(fstring+'{SP}'.format(SP=SPStr(sp)))
            h.SetDirectory(0)
        else:
            h.Add(f.Get(fstring+'{SP}'.format(SP=SPStr(sp))))

    h.Rebin2D(10, 10)
    p = Plotter.Plot(h, '', '', 'colz')
    canvas = Plotter.Canvas()
    canvas.mainPad.SetLogz(True)
    canvas.addMainPlot(p)
    canvas.scaleMargins(1.75, edges='R')
    canvas.scaleMargins(0.8, edges='L')
    canvas.cleanup('pdfs/SMR_'+fstring+'Global.pdf'.format(M=MUON, Q=quantity))

# make plots
if len(sys.argv) == 1: FS = '4Mu'
else: FS = sys.argv[1]
for fs in (FS,):
    for quantity in ('pT', 'Lxy', 'd0'):
        # 1D resolution plots
        if quantity == 'Lxy':
            makeResPlotsSingle(quantity, fs, 'DSA')
        else:
            makeResPlots(quantity, fs)

        for MUON in ('DSA', 'RSA'):
            if quantity == 'Lxy' and MUON == 'RSA': continue

            # 2D reco quantity vs. gen quantity plots
            makeColorPlot(MUON, quantity, fs)

            # 2D reco quantity vs. resolution plots
            for q2 in ('pT', 'Lxy', 'd0'):
                makeColorPlot(MUON, quantity, fs, q2)
