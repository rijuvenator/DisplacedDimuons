import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr

Patterns = {
    'HTo2XTo4Mu' : re.compile(r'(.*)_HTo2XTo4Mu_(\d{3,4})_(\d{2,3})_(\d{1,4})')
}

# get all histograms
HISTS = {}
f = R.TFile.Open('../analyzers/roots/SignalMatchResPlots.root')
for hkey in [tkey.GetName() for tkey in f.GetListOfKeys()]:
    # hkey has the form KEY_HTo2XTo4Mu_mH_mX_cTau
    matches = Patterns['HTo2XTo4Mu'].match(hkey)
    key = matches.group(1)
    sp = tuple(map(int, matches.group(2, 3, 4)))
    if sp not in HISTS:
        HISTS[sp] = {}
    HISTS[sp][key] = f.Get(hkey)

# end of plot function boilerplate
def Cleanup(canvas, filename):
    canvas.finishCanvas()
    canvas.save(filename)
    canvas.deleteCanvas()

# DSA RSA overlaid, per signal
def makeResPlots(quantity):
    for sp in SIGNALPOINTS:
        DOFIT = quantity == 'pT'
        h = {
            'DSA' : HISTS[sp]['DSA_'+quantity+'Res'],
            'RSA' : HISTS[sp]['RSA_'+quantity+'Res']
        }
        p = {}
        for MUON in h:
            p[MUON] = Plotter.Plot(h[MUON], 'H#rightarrow2X#rightarrow4#mu MC ({})'.format(MUON), 'l', 'hist')
        fname = 'pdfs/SMR_{}_HTo2XTo4Mu_{}.pdf'.format(quantity+'Res', SPStr(sp))

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

        Cleanup(canvas, fname)

# make 3D color plots
def makeColorPlot(MUON, quantity, q2=None):
    if q2 is None:
        fstring = '{M}_{Q}VS{Q}_HTo2XTo4Mu_'.format(M=MUON, Q=quantity)
    else:
        fstring = '{M}_{Q}ResVS{Q2}_HTo2XTo4Mu_'.format(M=MUON, Q=quantity, Q2=q2)

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
    Cleanup(canvas, 'pdfs/SMR_'+fstring+'Global.pdf'.format(M=MUON, Q=quantity))

# make plots
for quantity in ('pT', 'eta', 'phi', 'Lxy'):
    makeResPlots(quantity)
    makeColorPlot('DSA', quantity)
    makeColorPlot('RSA', quantity)
    for q2 in ('pT', 'eta', 'phi', 'Lxy', 'dR'):
        makeColorPlot('DSA', quantity, q2)
        makeColorPlot('RSA', quantity, q2)
