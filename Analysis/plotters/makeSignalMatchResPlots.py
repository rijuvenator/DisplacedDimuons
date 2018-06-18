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

        canvas = Plotter.Canvas(lumi='{} ({}, {}, {})'.format(fs, *sp))
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

        canvas = Plotter.Canvas(lumi='{} ({}, {}, {})'.format(fs, *sp))
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
        fstring = '{M}_{Q}VS{Q}'.format(M=MUON, Q=quantity)
    else:
        fstring = '{M}_{Q}ResVS{Q2}'.format(M=MUON, Q=quantity, Q2=q2)

    for i, sp in enumerate(SIGNALPOINTS):
        if i == 0:
            h = HISTS[(fs, sp)][fstring].Clone()
            h.SetDirectory(0)
        else:
            h.Add(HISTS[(fs, sp)][fstring])

    h.Rebin2D(10, 10)
    p = Plotter.Plot(h, '', '', 'colz')
    canvas = Plotter.Canvas()
    canvas.mainPad.SetLogz(True)
    canvas.addMainPlot(p)
    canvas.scaleMargins(1.75, edges='R')
    canvas.scaleMargins(0.8, edges='L')
    canvas.cleanup('pdfs/SMR_'+fstring+'_HTo2XTo'+fs+'_Global.pdf')

# make res plot binned by other quantities
def makeBinnedResPlot(MUON, quantity, q2, fs, sp):
    h = HISTS[(fs, sp)]['{M}_{Q}ResVS{Q2}'.format(M=MUON, Q=quantity, Q2=q2)].Clone()

    PRETTY = {'pT' : 'p_{T}', 'Lxy': 'L_{xy}', 'd0' : 'd_{0}'}

    fname = 'pdfs/SMR_{}_{}_{}-Binned_HTo2XTo{}_{}.pdf'.format(MUON, quantity+'Res', q2, fs, SPStr(sp))

    # there are always 1000 bins
    binranges = ((0,199), (200,599), (600,1000))

    # figure out the edges
    values = {}
    for key in binranges:
        if q2 == 'pT' or q2 == 'Lxy':
            binwidth = 500./1000.
        elif q2 == 'd0':
            binwidth = 100./1000.
        values[key] = (key[0]*binwidth, (key[1]+1)*binwidth)

    colors = dict(zip(binranges, (R.kRed, R.kBlue, R.kGreen)))
    colors2 = dict(zip(binranges, (2, 4, 3)))

    projections = {key:h.ProjectionY('_'+str(i), key[0], key[1]) for i,key in enumerate(binranges)}
    plots       = {key:Plotter.Plot(projections[key], '{} in ({}, {})'.format(PRETTY[q2], values[key][0], values[key][1]), 'l', 'hist') for key in binranges}

    canvas = Plotter.Canvas(lumi='{} ({}, {}, {})'.format(fs, *sp))
    for key in binranges:
        canvas.addMainPlot(plots[key])

    if quantity in ('d0', 'Lxy'):
        for key in binranges:
            plots[key].GetXaxis().SetRangeUser(-.2, .2)

    canvas.makeLegend(lWidth=.25, pos='tr')
    canvas.legend.moveLegend(X=-.08)
    canvas.legend.resizeHeight()

    realMax = 0.
    for key in plots:
        p = plots[key]
        for ibin in xrange(p.GetNbinsX()):
            if p.GetBinContent(ibin) > realMax:
                realMax = p.GetBinContent(ibin)
    canvas.firstPlot.SetMaximum(realMax * 1.05)

    for i, key in enumerate(binranges):
        plots[key].SetLineColor(colors[key])
        plots[key].setTitles(X=plots[key].GetXaxis().GetTitle(), Y='Counts')
        canvas.drawText('#color[{}]{{'.format(colors2[key]) + '#sigma = {:.4f}'.format(plots[key].GetStdDev()) + '}',
                        (canvas.legend.GetX1NDC()+.01, canvas.legend.GetY1NDC()-(i*0.04)-.04)
        )

    canvas.cleanup(fname)

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
            #makeColorPlot(MUON, quantity, fs)

            # 2D resolution vs. gen quantity plots
            for q2 in ('pT', 'Lxy', 'd0'):
                #makeColorPlot(MUON, quantity, fs, q2)

            # 1D resolution binned by gen quantity
                for sp in ((1000, 350, 3500),):
                    makeBinnedResPlot(MUON, quantity, q2, fs, sp)
