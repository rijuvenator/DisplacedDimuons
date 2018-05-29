import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.Selections as Selections
from DisplacedDimuons.Common.Utilities import SPStr

Patterns = {
    'HTo2XTo4Mu'   : re.compile(r'(.*)_TCUM_HTo2XTo4Mu_(\d{3,4})_(\d{2,3})_(\d{1,4})'),
    'HTo2XTo2Mu2J' : re.compile(r'(.*)_TCUM_HTo2XTo2Mu2J_(\d{3,4})_(\d{2,3})_(\d{1,4})')
}
for sample in ('DY100to200', 'DoubleMuonRun2016D-07Aug17'):
    Patterns[sample] = re.compile(r'(.*)_TCUM_'+sample)

# get all histograms
HISTS = {}
f = R.TFile.Open('../analyzers/roots/TailCumulativePlots.root')
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

# make per signal plots
def makePerSignalPlots():
    for ref in HISTS:
        for key in HISTS[ref]:
            if type(ref) == tuple:
                if ref[0] == '4Mu': name = 'HTo2XTo4Mu_'
                elif ref[0] == '2Mu2J' : name = 'HTo2XTo2Mu2J_'
                name += SPStr(ref[1])
                lumi = '{} ({}, {}, {})'.format(ref[0], *ref[1])
            else:
                name = ref
                lumi = ref

            h = HISTS[ref][key]
            p = Plotter.Plot(h, 'H#rightarrow2X#rightarrow4#mu MC', 'l', 'hist')
            fname = 'pdfs/TCUM_{}_{}.pdf'.format(key, name)
            canvas = Plotter.Canvas(lumi=lumi)
            canvas.lumi += ' : |#Delta#Phi| ' + ('<' if '_Less' in key else '>') + ' #pi/2'
            canvas.addMainPlot(p)
            canvas.makeLegend(lWidth=.25, pos='tr')
            canvas.legend.moveLegend(Y=-.3)
            canvas.legend.resizeHeight()
            p.SetLineColor(R.kBlue)

            cutKey = key.replace('_Less','').replace('_More','')
            cutVal = Selections.CUTS[cutKey].val

            l = R.TLine(cutVal, p.GetMinimum(), cutVal, p.GetMaximum()*1.05)
            l.SetLineStyle(2)
            l.SetLineWidth(2)
            l.Draw()

            Cleanup(canvas, fname)

makePerSignalPlots()
