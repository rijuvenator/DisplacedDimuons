import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr

Patterns = {
    'HTo2XTo4Mu' : re.compile(r'(.*)_HTo2XTo4Mu_(\d{3,4})_(\d{2,3})_(\d{1,4})'),
    'HTo2XTo2Mu2J' : re.compile(r'(.*)_HTo2XTo2Mu2J_(\d{3,4})_(\d{2,3})_(\d{1,4})')
}

# get all histograms
HISTS = {}
f = R.TFile.Open('../analyzers/roots/SignalMiscPlots.root')
for hkey in [tkey.GetName() for tkey in f.GetListOfKeys()]:
    if 'HTo2X' in hkey:
        if '4Mu' in hkey:
            # hkey has the form KEY_HTo2XTo4Mu_mH_mX_cTau
            matches = Patterns['HTo2XTo4Mu'].match(hkey)
            fs = '4Mu'
        elif '2Mu2J' in hkey:
            # hkey has the form KEY_HTo2XTo2Mu2J_mH_mX_cTau
            matches = Patterns['HTo2XTo2Mu2J'].match(hkey)
            fs = '2Mu2J'
        key = matches.group(1)
        sp = tuple(map(int, matches.group(2, 3, 4)))
        if (fs, sp) not in HISTS:
            HISTS[(fs, sp)] = {}
        HISTS[(fs, sp)][key] = f.Get(hkey)

# end of plot function boilerplate
def Cleanup(canvas, filename):
    canvas.finishCanvas()
    canvas.save(filename)
    canvas.deleteCanvas()

# make DSA RSA overlaid per signal plots
def makeOverlayPerSignalPlots(fs):
    KEYS = (
        'd0Dif',
        'nMuon',
    )
    for sp in SIGNALPOINTS:
        for key in KEYS:
            h = {}
            h['DSA'] = HISTS[(fs, sp)]['DSA_'+key]
            h['RSA'] = HISTS[(fs, sp)]['RSA_'+key]
            p = {}
            for rtype in h:
                p[rtype] = Plotter.Plot(h[rtype], 'H#rightarrow2X#rightarrow4#mu MC ({})'.format(rtype), 'l', 'hist')
            fname = 'pdfs/SMP_{}_HTo2XTo{}_{}.pdf'.format(key, fs, SPStr(sp))

            canvas = Plotter.Canvas(lumi='({}, {}, {})'.format(*sp))
            canvas.addMainPlot(p['DSA'])
            canvas.addMainPlot(p['RSA'], addS=True)

            canvas.firstPlot.setTitles(X=canvas.firstPlot.GetXaxis().GetTitle().replace('DSA','Reco'))

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

            Cleanup(canvas, fname)

for fs in ('4Mu',):
    makeOverlayPerSignalPlots(fs)
