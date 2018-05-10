import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import RECOSIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr

Patterns = {
    'HTo2XTo4Mu' : re.compile(r'(.*)_HTo2XTo4Mu_(\d{3,4})_(\d{2,3})_(\d{1,4})')
}

# get all histograms
HISTS = {}
f = R.TFile.Open('../analyzers/roots/SignalMiscPlots.root')
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

# make DSA RSA overlaid per signal plots
def makeOverlayPerSignalPlots():
    KEYS = (
        'pTRes',
        'd0Dif',
        'nMuon',
    )
    for sp in RECOSIGNALPOINTS:
        for key in KEYS:
            DOFIT = key == 'pTRes'
            h = {}
            h['DSA'] = HISTS[sp]['DSA_'+key]
            h['RSA'] = HISTS[sp]['RSA_'+key]
            p = {}
            for rtype in h:
                p[rtype] = Plotter.Plot(h[rtype], 'H#rightarrow2X#rightarrow4#mu MC ({})'.format(rtype), 'l', 'hist')
            fname = 'pdfs/SMP_{}_HTo2XTo4Mu_{}.pdf'.format(key, SPStr(sp))

            if DOFIT:
                funcs = {}
                fplots = {}
                for rtype in h:
                    funcs[rtype] = R.TF1('f'+rtype, 'gaus', -0.5, 0.4)
                    h[rtype].Fit('f'+rtype)
                    fplots[rtype] = Plotter.Plot(funcs[rtype], 'Gaussian fit ({})'.format(rtype), 'l', '')

            canvas = Plotter.Canvas(lumi='({}, {}, {})'.format(*sp))
            canvas.addMainPlot(p['DSA'])
            canvas.addMainPlot(p['RSA'], addS=True)

            canvas.firstPlot.setTitles(X=canvas.firstPlot.GetXaxis().GetTitle().replace('DSA','Reco'))

            if DOFIT:
                canvas.addMainPlot(fplots['DSA'])
                canvas.addMainPlot(fplots['RSA'])

            canvas.makeLegend(lWidth=.25, pos='tr' if key == 'pTRes' else 'tl')
            canvas.legend.moveLegend(X=-.3 if key == 'pTRes' else 0.)
            canvas.legend.resizeHeight()

            p['DSA'].SetLineColor(R.kBlue)
            p['RSA'].SetLineColor(R.kRed)

            canvas.drawText('#color[4]{' + '#bar{{x}} = {:.4f}'   .format(h['DSA'].GetMean())   + '}', (.75, .8    ))
            canvas.drawText('#color[4]{' + 's = {:.4f}'           .format(h['DSA'].GetStdDev()) + '}', (.75, .8-.04))
            canvas.drawText('#color[2]{' + '#bar{{x}} = {:.4f}'   .format(h['RSA'].GetMean())   + '}', (.75, .8-.08))
            canvas.drawText('#color[2]{' + 's = {:.4f}'           .format(h['RSA'].GetStdDev()) + '}', (.75, .8-.12))

            if key == 'nMuon':
                canvas.firstPlot.SetMaximum(1.05 * max(p['DSA'].GetMaximum(), p['RSA'].GetMaximum()))

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
def makeColorPlot(key):
    for i, sp in enumerate(RECOSIGNALPOINTS):
        if i == 0:
            h = f.Get('{}_HTo2XTo4Mu_{}'.format(key, SPStr(sp)))
            h.SetDirectory(0)
        else:
            h.Add(f.Get('{}_HTo2XTo4Mu_{}'.format(key, SPStr(sp))))

    h.Rebin2D(10, 10)
    p = Plotter.Plot(h, '', '', 'colz')
    canvas = Plotter.Canvas()
    canvas.mainPad.SetLogz(True)
    canvas.addMainPlot(p)
    canvas.scaleMargins(1.75, edges='R')
    canvas.scaleMargins(0.8, edges='L')
    Cleanup(canvas, 'pdfs/SMP_{}_HTo2XTo4Mu_Global.pdf'.format(key))

makeOverlayPerSignalPlots()
makeColorPlot('DSA_pTResVSLxy')
makeColorPlot('DSA_pTResVSpT')
makeColorPlot('DSA_pTResVSdR')
makeColorPlot('DSA_pTVSpT')
