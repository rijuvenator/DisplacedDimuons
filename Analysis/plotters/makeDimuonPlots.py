import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
from DisplacedDimuons.Common.Utilities import SPStr

Patterns = {
    'HTo2XTo4Mu' : re.compile(r'(.*)_HTo2XTo4Mu_(\d{3,4})_(\d{2,3})_(\d{1,4})')
}
for sample in ('DY100to200', 'DoubleMuonRun2016D-07Aug17'):
    Patterns[sample] = re.compile(r'(.*)_'+sample)

# get all histograms
HISTS = {}
f = R.TFile.Open('../analyzers/roots/DimuonPlots.root')
for hkey in [tkey.GetName() for tkey in f.GetListOfKeys()]:
    if 'HTo2XTo4Mu' in hkey:
        # hkey has the form KEY_HTo2XTo4Mu_mH_mX_cTau
        matches = Patterns['HTo2XTo4Mu'].match(hkey)
        key = matches.group(1)
        sp = tuple(map(int, matches.group(2, 3, 4)))
        if sp not in HISTS:
            HISTS[sp] = {}
        HISTS[sp][key] = f.Get(hkey)
    else:
        # hkey has the form KEY_SAMPLE
        for sample, pattern in Patterns.iteritems():
            matches = pattern.match(hkey)
            if matches:
                key = matches.group(1)
                if sample not in HISTS:
                    HISTS[sample] = {}
                HISTS[sample][key] = f.Get(hkey)

# end of plot function boilerplate
def Cleanup(canvas, filename):
    canvas.finishCanvas()
    canvas.save(filename)
    canvas.deleteCanvas()

# make plots that are per signal point
def makePerSignalPlots():
    for ref in HISTS:
        for key in HISTS[ref]:
            if type(ref) == tuple:
                name = 'HTo2XTo4Mu_' + SPStr(ref)
                lumi = '({}, {}, {})'.format(*ref)
            else:
                name = ref
                lumi = ref

            h = HISTS[ref][key]
            p = Plotter.Plot(h, 'H#rightarrow2X#rightarrow4#mu MC', 'l', 'hist')
            fname = 'pdfs/{}_{}.pdf'.format(key, name)

            canvas = Plotter.Canvas(lumi=lumi)
            canvas.addMainPlot(p)
            canvas.makeLegend(lWidth=.25, pos='tr')
            canvas.legend.moveLegend(Y=-.3)
            canvas.legend.resizeHeight()
            p.SetLineColor(R.kBlue)
            canvas.drawText('#color[4]{' + '#bar{{x}} = {:.4f}'   .format(h.GetMean())   + '}', (.7, .8    ))
            canvas.drawText('#color[4]{' + 's = {:.4f}'           .format(h.GetStdDev()) + '}', (.7, .8-.04))
            Cleanup(canvas, fname)

makePerSignalPlots()
