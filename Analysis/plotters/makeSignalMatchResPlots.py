import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
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
            'DSA' : HISTS[(fs, sp)]['DSA_'+quantity+'Res'].Clone(),
            'RSA' : HISTS[(fs, sp)]['RSA_'+quantity+'Res'].Clone()
        }
        p = {}
        for MUON in h:
            h[MUON].Rebin(10)
            p[MUON] = Plotter.Plot(h[MUON], 'Signal MC ({})'.format(MUON), 'l', 'hist')
        fname = 'pdfs/SMR_{}_HTo2XTo{}_{}.pdf'.format(quantity+'Res', fs, SPStr(sp))

        if DOFIT:
            funcs = {}
            fplots = {}
            for MUON in h:
                funcs[MUON] = R.TF1('f'+MUON, 'gaus', -0.5, 0.4)
                h[MUON].Fit('f'+MUON, 'R')
                fplots[MUON] = Plotter.Plot(funcs[MUON], 'Gaussian fit ({})'.format(MUON), 'l', '')

        canvas = Plotter.Canvas(lumi='{} ({} GeV, {} GeV, {} mm)'.format(fs, *sp))
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
        RT.addBinWidth(canvas.firstPlot)

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
        h = HISTS[(fs, sp)][MUON+'_'+quantity+'Res'].Clone()
        h.Rebin(10)
        p = Plotter.Plot(h, 'Signal MC ({})'.format(MUON), 'l', 'hist')
        fname = 'pdfs/SMR_{}_{}_HTo2XTo{}_{}.pdf'.format(MUON, quantity+'Res', fs, SPStr(sp))

        canvas = Plotter.Canvas(lumi='{} ({} GeV, {} GeV, {} mm)'.format(fs, *sp))
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

    PRETTY = {'pT' : 'p_{T}', 'Lxy': 'L_{xy}', 'd0' : 'd_{0}', 'qm' : 'charge matched'}

    fname = 'pdfs/SMR_{}_{}_{}-Binned_HTo2XTo{}_{}.pdf'.format(MUON, quantity+'Res', q2, fs, SPStr(sp))

    if q2 == 'pT':
        binranges = ((0,199), (200,599), (600,1000))
        binwidth  = 500./1000.
        values    = {key:(key[0]*binwidth, (key[1]+1)*binwidth) for key in binranges}
        colors    = dict(zip(binranges, (R.kRed, R.kBlue, R.kGreen)))
        colors2   = dict(zip(binranges, (2     , 4      , 3       )))
        legName   = '{V1} #leq {Q2} #leq {V2}'
    elif q2 == 'Lxy':
        binranges = ((0,199), (200,599), (600,1000))
        binwidth  = 800./1000.
        values    = {key:(key[0]*binwidth, (key[1]+1)*binwidth) for key in binranges}
        colors    = dict(zip(binranges, (R.kRed, R.kBlue, R.kGreen)))
        colors2   = dict(zip(binranges, (2     , 4      , 3       )))
        legName   = '{V1} #leq {Q2} #leq {V2}'
    elif q2 == 'd0':
        binranges = ((0,199), (200,599), (600,1000))
        binwidth  = 200./1000.
        values    = {key:(key[0]*binwidth, (key[1]+1)*binwidth) for key in binranges}
        colors    = dict(zip(binranges, (R.kRed, R.kBlue, R.kGreen)))
        colors2   = dict(zip(binranges, (2     , 4      , 3       )))
        legName   = '{V1} #leq {Q2} #leq {V2}'
    elif q2 == 'qm':
        binranges = ((1, 1), (2, 2))
        values    = {(1, 1):(False, False),(2, 2):(True, True)}
        colors    = dict(zip(binranges, (R.kRed, R.kBlue)))
        colors2   = dict(zip(binranges, (2     , 4      )))
        legName   = '{Q2} : {V1}'

    projections = {key:h.ProjectionY('_'+str(i), key[0], key[1]) for i,key in enumerate(binranges)}
    plots       = {key:Plotter.Plot(projections[key], legName.format(Q2=PRETTY[q2], V1=values[key][0], V2=values[key][1]), 'l', 'hist') for key in binranges}

    canvas = Plotter.Canvas(lumi='{} ({} GeV, {} GeV, {} mm)'.format(fs, *sp))
    for key in binranges:
        plots[key].Rebin(10)
        if plots[key].Integral() != 0:
            plots[key].Scale(1./plots[key].Integral())
        canvas.addMainPlot(plots[key])

    canvas.makeLegend(lWidth=.25, pos='tr')
    canvas.legend.moveLegend(X=-.08)
    canvas.legend.resizeHeight()
    canvas.setMaximum(recompute=True)

    for i, key in enumerate(binranges):
        plots[key].SetLineColor(colors[key])
        plots[key].setTitles(X=plots[key].GetXaxis().GetTitle(), Y='Normalized Counts')
        canvas.drawText('#color[{}]{{'.format(colors2[key]) + '#sigma = {:.4f}'.format(plots[key].GetStdDev()) + '}',
                        (canvas.legend.GetX1NDC()+.01, canvas.legend.GetY1NDC()-(i*0.04)-.04)
        )

    canvas.cleanup(fname)

def makeRefittedResPlot(fs):
    DOFIT = True
    for sp in SIGNALPOINTS:
        h = {}
        p = {}
        funcs = {}
        fplots = {}
        canvas = Plotter.Canvas(lumi='{} ({} GeV, {} GeV, {} mm)'.format(fs, *sp))
        for TAG in ('Before', 'After'):
            h[TAG] = HISTS[(fs, sp)]['Refit'+TAG+'_pTRes'].Clone()
            h[TAG].Rebin(10)

            p[TAG] = Plotter.Plot(h[TAG], TAG + ' fit', 'l', 'hist')
            canvas.addMainPlot(p[TAG], addS=True)

            if DOFIT:
                MODE = h[TAG].GetXaxis().GetBinLowEdge(h[TAG].GetMaximumBin())
                funcs[TAG] = R.TF1('f'+TAG, 'gaus', MODE-0.3, MODE+0.3)
                h[TAG].Fit('f'+TAG, 'R')
                fplots[TAG] = Plotter.Plot(funcs[TAG], 'Gaussian fit ({})'.format(TAG), 'l', '')
                canvas.addMainPlot(fplots[TAG])


        canvas.makeLegend(lWidth=.3, pos='tr')
        canvas.legend.resizeHeight()

        p['Before'].SetLineColor(R.kRed )
        p['After' ].SetLineColor(R.kBlue)
        canvas.setMaximum()

        # top left edge = bottom left corner of legend shifted a tiny bit
        tle = {'x':canvas.legend.GetX1NDC()+0.02, 'y':canvas.legend.GetY1NDC()-0.025}

        canvas.drawText('#color[{:d}]{{#bar{{x}} = {:.4f}'   .format(R.kRed , h['Before'].GetMean())   + '}', (tle['x'], tle['y']    ))
        canvas.drawText('#color[{:d}]{{s = {:.4f}'           .format(R.kRed , h['Before'].GetStdDev()) + '}', (tle['x'], tle['y']-.04))
        canvas.drawText('#color[{:d}]{{#bar{{x}} = {:.4f}'   .format(R.kBlue, h['After' ].GetMean())   + '}', (tle['x'], tle['y']-.08))
        canvas.drawText('#color[{:d}]{{s = {:.4f}'           .format(R.kBlue, h['After' ].GetStdDev()) + '}', (tle['x'], tle['y']-.12))

        if DOFIT:
            fplots['Before'].SetLineColor(R.kRed+1)
            fplots['After' ].SetLineColor(R.kBlue+1)

            canvas.setFitBoxStyle(h['Before'], lWidth=0.25, pos='tl', fontscale=0.6)
            canvas.setFitBoxStyle(h['After' ], lWidth=0.25, pos='tl', fontscale=0.6)

            sboxes = {
                'Before': p['Before'].FindObject('stats'),
                'After' : p['After' ].FindObject('stats')
            }

            sboxes['Before'].SetTextColor(R.kRed+1)
            sboxes['After' ].SetTextColor(R.kBlue+1)

            firstHeight = sboxes['Before'].GetY2NDC() - sboxes['Before'].GetY1NDC()

            Plotter.MOVE_OBJECT(sboxes['After'], Y=-firstHeight-.01, NDC=True)


        fname = 'pdfs/SMR_RefitBA_pTRes_HTo2XTo{}_{}.pdf'.format(fs, SPStr(sp))
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
            for q2 in ('pT', 'Lxy', 'd0', 'qm'):
                if quantity == 'Lxy' and q2 == 'qm': continue
                #makeColorPlot(MUON, quantity, fs, q2)

            # 1D resolution binned by gen quantity
                for sp in SIGNALPOINTS:
                    makeBinnedResPlot(MUON, quantity, q2, fs, sp)

    makeRefittedResPlot(fs)
    for sp in SIGNALPOINTS:
        makeBinnedResPlot('RefitBefore', 'pT', 'Lxy', fs, sp)
        makeBinnedResPlot('RefitAfter' , 'pT', 'Lxy', fs, sp)
