import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.Selections as Selections
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import HistogramGetter

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/nMinusOneEffPlots.root')
f = R.TFile.Open('../analyzers/roots/nMinusOneEffPlots.root')

# make per sample plots
def makePerSamplePlots():
    for ref in HISTS:
        for key in HISTS[ref]:
            if 'DenVS' in key: continue

            matches = re.match(r'(.*)EffVS(.*)', key)

            cut = matches.group(1)
            val = matches.group(2)

            if cut in Selections.CutLists['MuonCutList'] and val == 'Lxy': continue
            if cut in Selections.CutLists['DimuonCutList'] and val in ('pT', 'eta', 'd0'): continue

            if type(ref) == tuple:
                if ref[0] == '4Mu': name = 'HTo2XTo4Mu_'
                elif ref[0] == '2Mu2J' : name = 'HTo2XTo2Mu2J_'
                name += SPStr(ref[1])
                lumi = '{} ({}, {}, {})'.format(ref[0], *ref[1])
            else:
                name = ref
                lumi = ref

            h = HISTS[ref][key].Clone()
            g = R.TGraphAsymmErrors(h, HISTS[ref][key.replace('Eff', 'Den')], 'cp')
            g.SetNameTitle('g_'+key, ';'+h.GetXaxis().GetTitle()+';'+h.GetYaxis().GetTitle())
            p = Plotter.Plot(g, '', 'pe', 'pe')

            canvas = Plotter.Canvas(lumi=lumi)
            canvas.addMainPlot(p)
            p.SetLineColor(R.kBlue)
            p.SetMarkerColor(R.kBlue)
            canvas.firstPlot.SetMinimum(0.)
            canvas.firstPlot.SetMaximum(1.)

            fname = 'pdfs/NM1E_{}_{}.pdf'.format(key, name)
            canvas.cleanup(fname)

makePerSamplePlots()
