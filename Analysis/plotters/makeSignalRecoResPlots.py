import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import HistogramGetter
import sys

TRIGGER = False

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/Main/SignalRecoResPlots.root')
f = R.TFile.Open('../analyzers/roots/Main/SignalRecoResPlots.root')

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
            RT.addFlows(h[MUON])
            h[MUON].Rebin(10)
            p[MUON] = Plotter.Plot(h[MUON], 'Signal MC ({})'.format(MUON), 'l', 'hist')
        fname = 'pdfs/SRR_{}_{}HTo2XTo{}_{}.pdf'.format(quantity+'Res', 'Trig-' if TRIGGER else '', fs, SPStr(sp))

        if DOFIT:
            funcs = {}
            fplots = {}
            for MUON in h:
                funcs[MUON] = R.TF1('f'+MUON, 'gaus', -0.4, 0.3)
                h[MUON].Fit('f'+MUON, 'R')
                fplots[MUON] = Plotter.Plot(funcs[MUON], 'Gaussian fit ({})'.format(MUON), 'l', '')

        canvas = Plotter.Canvas(lumi=SPLumiStr(fs, *sp))
        canvas.addMainPlot(p['DSA'])
        canvas.addMainPlot(p['RSA'], addS=True)

        canvas.firstPlot.setTitles(X=canvas.firstPlot.GetXaxis().GetTitle().replace('DSA','Reco'))

        if DOFIT:
            canvas.addMainPlot(fplots['DSA'])
            canvas.addMainPlot(fplots['RSA'])

        canvas.makeLegend(lWidth=.25, pos='tl')
        canvas.legend.resizeHeight()

        p['DSA'].SetLineColor(R.kBlue)
        p['RSA'].SetLineColor(R.kRed)
        RT.addBinWidth(canvas.firstPlot)

        canvas.drawText('#color[4]{' + '#bar{{x}} = {:.4f}'   .format(h['DSA'].GetMean())   + '}', (.75, .85    ))
        canvas.drawText('#color[4]{' + 's = {:.4f}'           .format(h['DSA'].GetStdDev()) + '}', (.75, .85-.04))
        canvas.drawText('#color[2]{' + '#bar{{x}} = {:.4f}'   .format(h['RSA'].GetMean())   + '}', (.75, .85-.08))
        canvas.drawText('#color[2]{' + 's = {:.4f}'           .format(h['RSA'].GetStdDev()) + '}', (.75, .85-.12))

        if DOFIT:
            fplots['DSA'].SetLineColor(R.kBlue+1)
            fplots['RSA'].SetLineColor(R.kRed+1)

            canvas.setFitBoxStyle(h['DSA'], lWidth=0.275, pos='tr')
            canvas.setFitBoxStyle(h['RSA'], lWidth=0.275, pos='tr')

            p['DSA'].FindObject('stats').SetTextColor(R.kBlue+1)
            Plotter.MOVE_OBJECT(p['DSA'].FindObject('stats'), Y=-.15, NDC=True)

            p['RSA'].FindObject('stats').SetTextColor(R.kRed+1)
            Plotter.MOVE_OBJECT(p['RSA'].FindObject('stats'), Y=-.3, NDC=True)

        canvas.cleanup(fname)

# DSA plot or RSA plot only (used here for DSA Lxy)
def makeResPlotsSingle(quantity, fs, MUON):
    for sp in SIGNALPOINTS:
        h = HISTS[(fs, sp)][MUON+'_'+quantity+'Res'].Clone()
        RT.addFlows(h)
        h.Rebin(10)
        p = Plotter.Plot(h, 'Signal MC ({})'.format(MUON), 'l', 'hist')
        fname = 'pdfs/SRR_{}_{}_{}HTo2XTo{}_{}.pdf'.format(MUON, quantity+'Res', 'Trig-' if TRIGGER else '', fs, SPStr(sp))

        canvas = Plotter.Canvas(lumi=SPLumiStr(fs, *sp))
        canvas.addMainPlot(p)

        canvas.makeLegend(lWidth=.25, pos='tr' if quantity == 'pT' else 'tl')
        canvas.legend.moveLegend(X=-.3 if quantity == 'pT' else 0.)
        canvas.legend.resizeHeight()

        p.SetLineColor(R.kBlue)
        RT.addBinWidth(canvas.firstPlot)

        canvas.drawText('#color[4]{' + '#bar{{x}} = {:.4f}'   .format(h.GetMean())   + '}', (.75, .85    ))
        canvas.drawText('#color[4]{' + 's = {:.4f}'           .format(h.GetStdDev()) + '}', (.75, .85-.04))

        canvas.cleanup(fname)

# copy of above, with overlay (for 14 September talk), two specific signal points
def makeResPlotsSingleOverlaid():
    quantity = 'Lxy'
    MUON     = 'DSA'
    fs       = '2Mu2J'
    SPLIST   = ((1000, 350, 3500), (1000, 20, 200))

    h = {
        SPLIST[0] : HISTS[(fs, SPLIST[0])][MUON+'_'+quantity+'Res'].Clone(),
        SPLIST[1] : HISTS[(fs, SPLIST[1])][MUON+'_'+quantity+'Res'].Clone()
    }
    p = {}
    for TAG in h:
        NB = h[TAG].GetNbinsX()
        print h[TAG].GetEntries(), h[TAG].Integral(0, NB+1)
        if h[TAG].Integral(0, NB+1) != 0:
            h[TAG].Scale(1./h[TAG].Integral(0, NB+1))
        RT.addFlows(h[TAG])
        h[TAG].Rebin(10)
        p[TAG] = Plotter.Plot(h[TAG], '{}, {}, {}, {}'.format(fs, *TAG), 'l', 'hist')
    fname = 'SRR_{}_{}_{}HTo2XTo{}_Overlaid.pdf'.format(MUON, quantity+'Res', 'Trig-' if TRIGGER else '', fs)

    funcs = {}
    fplots = {}
    for TAG in h:
        funcs[TAG] = R.TF1('f'+str(TAG), 'gaus', -15., 15.)
        h[TAG].Fit('f'+str(TAG), 'R')
        fplots[TAG] = Plotter.Plot(funcs[TAG], 'Gaussian fit ({}, {}, {}, {})'.format(fs, *TAG), 'l', '')

    canvas = Plotter.Canvas()
    canvas.addMainPlot(p[SPLIST[0]])
    canvas.addMainPlot(p[SPLIST[1]], addS=True)

    canvas.firstPlot.setTitles(X=                canvas.firstPlot.GetXaxis().GetTitle() + ' [cm]')
    canvas.firstPlot.setTitles(Y='Normalized ' + canvas.firstPlot.GetYaxis().GetTitle()          )

    canvas.addMainPlot(fplots[SPLIST[0]])
    canvas.addMainPlot(fplots[SPLIST[1]])

    canvas.makeLegend(lWidth=.25, pos='tl')
    canvas.legend.resizeHeight()

    p[SPLIST[0]].SetLineColor(R.kBlue)
    p[SPLIST[1]].SetLineColor(R.kRed)
    RT.addBinWidth(canvas.firstPlot)

    canvas.drawText('#color[4]{' + '#bar{{x}} = {:.4f}'   .format(h[SPLIST[0]].GetMean())   + '}', (.75, .85    ))
    canvas.drawText('#color[4]{' + 's = {:.4f}'           .format(h[SPLIST[0]].GetStdDev()) + '}', (.75, .85-.04))
    canvas.drawText('#color[2]{' + '#bar{{x}} = {:.4f}'   .format(h[SPLIST[1]].GetMean())   + '}', (.75, .85-.08))
    canvas.drawText('#color[2]{' + 's = {:.4f}'           .format(h[SPLIST[1]].GetStdDev()) + '}', (.75, .85-.12))

    fplots[SPLIST[0]].SetLineColor(R.kBlue+1)
    fplots[SPLIST[1]].SetLineColor(R.kRed+1)

    canvas.setFitBoxStyle(h[SPLIST[0]], lWidth=0.275, pos='tr')
    canvas.setFitBoxStyle(h[SPLIST[1]], lWidth=0.275, pos='tr')

    p[SPLIST[0]].FindObject('stats').SetTextColor(R.kBlue+1)
    Plotter.MOVE_OBJECT(p[SPLIST[0]].FindObject('stats'), Y=-.15, NDC=True)

    p[SPLIST[1]].FindObject('stats').SetTextColor(R.kRed+1)
    Plotter.MOVE_OBJECT(p[SPLIST[1]].FindObject('stats'), Y=-.3, NDC=True)

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
    canvas.cleanup('pdfs/SRR_{}_{}HTo2XTo{}_Global.pdf'.format(fstring, 'Trig-' if TRIGGER else '', fs))

def getBinningValues(q2):
    if q2 == 'pT':
        pretty    = 'p_{T}'
        binranges = ((0,199), (200,599), (600,1000))
        binwidth  = 500./1000.
        values    = {key:(key[0]*binwidth, (key[1]+1)*binwidth) for key in binranges}
        colors    = dict(zip(binranges, (R.kRed, R.kBlue, R.kGreen)))
        colors2   = dict(zip(binranges, (2     , 4      , 3       )))
        legName   = '{V1} #leq {Q2} #leq {V2} GeV'
    elif q2 == 'Lxy':
        pretty    = 'L_{xy}'
        binranges = ((0,214), (215,424), (425,1000))
        binwidth  = 800./1000.
        values    = {key:(key[0]*binwidth, (key[1]+1)*binwidth) for key in binranges}
        colors    = dict(zip(binranges, (R.kRed, R.kBlue, R.kGreen)))
        colors2   = dict(zip(binranges, (2     , 4      , 3       )))
        legName   = '{V1} #leq {Q2} #leq {V2} cm'
    elif q2 == 'd0':
        pretty    = 'd_{0}'
        binranges = ((0,199), (200,599), (600,1000))
        binwidth  = 200./1000.
        values    = {key:(key[0]*binwidth, (key[1]+1)*binwidth) for key in binranges}
        colors    = dict(zip(binranges, (R.kRed, R.kBlue, R.kGreen)))
        colors2   = dict(zip(binranges, (2     , 4      , 3       )))
        legName   = '{V1} #leq {Q2} #leq {V2} cm'
    elif q2 == 'qm':
        pretty    = 'charge matched'
        binranges = ((1, 1), (2, 2))
        values    = {(1, 1):(False, False),(2, 2):(True, True)}
        colors    = dict(zip(binranges, (R.kRed, R.kBlue)))
        colors2   = dict(zip(binranges, (2     , 4      )))
        legName   = '{Q2} : {V1}'

    return pretty, binranges, values, colors, colors2, legName

# make res plot binned by other quantities
def makeBinnedResPlot(MUON, quantity, q2, fs, sp):
    h = HISTS[(fs, sp)]['{M}_{Q}ResVS{Q2}'.format(M=MUON, Q=quantity, Q2=q2)].Clone()

    fname = 'pdfs/SRR_{}_{}_{}-Binned_{}HTo2XTo{}_{}.pdf'.format(MUON, quantity+'Res', q2, 'Trig-' if TRIGGER else '', fs, SPStr(sp))

    pretty, binranges, values, colors, colors2, legName = getBinningValues(q2)

    projections = {key:h.ProjectionY('_'+str(i), key[0], key[1]) for i,key in enumerate(binranges)}
    plots       = {key:Plotter.Plot(projections[key], legName.format(Q2=pretty, V1=values[key][0], V2=values[key][1]), 'l', 'hist') for key in binranges}

    canvas = Plotter.Canvas(lumi=SPLumiStr(fs, *sp))
    for key in binranges:
        RT.addFlows(plots[key])
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

    RT.addBinWidth(canvas.firstPlot)
    canvas.cleanup(fname)

# make resolution plots of the tracks before and after the refit
def makeRefittedResPlot(fs):
    DOFIT = True
    for sp in SIGNALPOINTS:
        h = {}
        p = {}
        funcs = {}
        fplots = {}
        canvas = Plotter.Canvas(lumi=SPLumiStr(fs, *sp))
        for TAG in ('Before', 'After'):
            h[TAG] = HISTS[(fs, sp)]['Refit'+TAG+'_pTRes'].Clone()
            RT.addFlows(h[TAG])
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
        RT.addBinWidth(canvas.firstPlot)
        canvas.setMaximum(recompute=True)

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


        fname = 'pdfs/SRR_RefitBA_pTRes_{}HTo2XTo{}_{}.pdf'.format('Trig-' if TRIGGER else '', fs, SPStr(sp))
        canvas.cleanup(fname)

# make res plot binned by other quantities, separated by bin
# necessarily, this must account for multiple plot types -- we are splitting bins across plots,
# so it must be because we're plotting two different plots of the same bin
# therefore TAGS should be a list, even if of one element, e.g. ('DSA', 'RSA') or ('RefitBefore', 'RefitAfter')
# outputTag should be whatever the resulting file name should be
def makeBinnedResPlotsBinwise(TAGS, outputTag, quantity, q2, fs, sp):
    defaultColorOrder = (R.kRed, R.kBlue, R.kGreen)
    h = {}
    for tag in TAGS:
        h[tag] = HISTS[(fs, sp)]['{T}_{Q}ResVS{Q2}'.format(T=tag, Q=quantity, Q2=q2)].Clone()

    # leaving space for the bin number
    fname = 'pdfs/SRR_{}_{}_{}-Binned-Bin-{{}}_{}HTo2XTo{}_{}.pdf'.format(outputTag, quantity+'Res', q2, 'Trig-' if TRIGGER else '', fs, SPStr(sp))

    pretty, binranges, values, colors, colors2, legName = getBinningValues(q2)

    for i, key in enumerate(binranges):
        canvas = Plotter.Canvas(lumi=SPLumiStr(fs, *sp))
        projections, plots = {}, {}
        for j, tag in enumerate(TAGS):
            projections[tag] = h[tag].ProjectionY('_'+str(i)+'_'+str(j), key[0], key[1])
            plots[tag]       = Plotter.Plot(projections[tag], tag, 'l', 'hist')
            RT.addFlows(plots[tag])
            plots[tag].Rebin(10)
            if plots[tag].Integral() != 0:
                plots[tag].Scale(1./plots[tag].Integral())
            plots[tag].SetLineColor(defaultColorOrder[j])

            canvas.addMainPlot(plots[tag])

        canvas.makeLegend(lWidth=.25, pos='tr')
        canvas.legend.resizeHeight()
        canvas.setMaximum(recompute=True)

        canvas.drawText(legName.format(Q2=pretty, V1=values[key][0], V2=values[key][1]), (canvas.legend.GetX1NDC()+.01, canvas.legend.GetY1NDC()-.04))

        for j, tag in enumerate(TAGS):
            plots[tag].SetLineColor(defaultColorOrder[j])
            plots[tag].setTitles(X=plots[tag].GetXaxis().GetTitle(), Y='Normalized Counts')
            canvas.drawText('#color[{}]{{'.format(defaultColorOrder[j]) + '#sigma = {:.4f}'.format(plots[tag].GetStdDev()) + '}',
                (canvas.legend.GetX1NDC()+.01, canvas.legend.GetY1NDC()-(j*0.04)-.08)
            )

        RT.addBinWidth(canvas.firstPlot)
        canvas.cleanup(fname.format(i+1))

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
        makeBinnedResPlotsBinwise(('RefitBefore', 'RefitAfter'), 'RefitBA', 'pT', 'Lxy', fs, sp)

# special purpose overlaid plot
#makeResPlotsSingleOverlaid()
