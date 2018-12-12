import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.Selections as Selections
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter

TRIGGER = False

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/Main/nMinusOneEffPlots.root')
f = R.TFile.Open('../analyzers/roots/Main/nMinusOneEffPlots.root')

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
                if TRIGGER:
                    name = 'Trig-'+name
                lumi = SPLumiStr(ref[0], *ref[1])
                legName = HistogramGetter.PLOTCONFIG['HTo2XTo'+ref[0]]['LATEX']
            else:
                name = ref
                lumi = HistogramGetter.PLOTCONFIG[ref]['LATEX']
                legName = HistogramGetter.PLOTCONFIG[ref]['LATEX']

            h = HISTS[ref][key].Clone()
            RT.addFlows(h)
            d = HISTS[ref][key.replace('Eff', 'Den')].Clone()
            RT.addFlows(d)
            g = R.TGraphAsymmErrors(h, d, 'cp')
            g.SetNameTitle('g_'+key, ';'+h.GetXaxis().GetTitle()+';'+h.GetYaxis().GetTitle())
            p = Plotter.Plot(g, '', 'pe', 'pe')

            canvas = Plotter.Canvas(lumi=lumi)
            canvas.addMainPlot(p)
            p.setColor(R.kBlue)
            canvas.firstPlot.SetMinimum(0.)
            canvas.firstPlot.SetMaximum(1.)

            fname = 'pdfs/NM1E_{}_{}.pdf'.format(key, name)
            canvas.cleanup(fname)

# make stack plots
def makeStackPlots(DataMC=False, logy=False):
    BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'DY10to50', 'DY50toInf')
    for hkey in HISTS['DY50toInf']:
        if 'DenVS' in hkey: continue

        matches = re.match(r'(.*)EffVS(.*)', hkey)

        cut = matches.group(1)
        val = matches.group(2)

        if cut in Selections.CutLists['MuonCutList'] and val == 'Lxy': continue
        if cut in Selections.CutLists['DimuonCutList'] and val in ('pT', 'eta', 'd0'): continue

        h = {
#           'Data'       : HISTS['DoubleMuonRun2016D-07Aug17'][hkey].Clone(),
#           'Signal'     : HISTS[('4Mu', (125, 20, 13))      ][hkey].Clone(),
            'BG'         : R.THStack('hBG', '')
        }

        dkey = hkey.replace('EffVS', 'DenVS')
        d = {
#           'Data'       : HISTS['DoubleMuonRun2016D-07Aug17'][dkey].Clone(),
#           'Signal'     : HISTS[('4Mu', (125, 20, 13))      ][dkey].Clone(),
            'BG'         : R.THStack('hBGD', '')
        }

        PConfig = {
#           'Data'       : ('DoubleMuon2016D'              , 'pe', 'pe'  ),
#           'Signal'     : ('H#rightarrow2X#rightarrow4#mu', 'l' , 'hist'),
            'BG'         : (''                             , ''  , 'hist'),
        }

        PC = HistogramGetter.PLOTCONFIG

        for key in BGORDER:
            PConfig[key] = (PC[key]['LATEX'], 'f', 'hist')
            for DICT, KEY in ((h, hkey), (d, dkey)):
                DICT[key] = HISTS[key][KEY].Clone()
                RT.addFlows(DICT[key])
                if DICT[key].GetNbinsX() > 100: DICT[key].Rebin(10)
                DICT[key].Scale(PC[key]['WEIGHT'])
                DICT['BG'].Add(DICT[key])


        g = R.TGraphAsymmErrors(h['BG'].GetStack().Last(), d['BG'].GetStack().Last(), 'cp')
        g.SetNameTitle('g_'+hkey, ';'+h['DY50toInf'].GetXaxis().GetTitle()+';'+h['DY50toInf'].GetYaxis().GetTitle())
        p = Plotter.Plot(g, '', 'pe', 'pe')

        fname = 'pdfs/NM1E_{}_Stack{}.pdf'.format(hkey, '-Log' if logy else '')

        canvas = Plotter.Canvas(ratioFactor=0. if not DataMC else 1./3., cHeight=600 if not DataMC else 800, logy=logy)
        canvas.addMainPlot(p)
#       canvas.addMainPlot(p['Data'])
#       canvas.addMainPlot(p['Signal'])

        p.setColor(R.kBlue)
        canvas.firstPlot.SetMinimum(0.)
        canvas.firstPlot.SetMaximum(1.)
        #canvas.firstPlot.SetMaximum(1.e-4)

#       if DataMC:
#           canvas.makeRatioPlot(p['Data'].plot, p['BG'].plot.GetStack().Last())

#       p['Signal'    ].SetLineStyle(2)
#       p['Signal'    ].SetLineColor(R.kRed)

        canvas.cleanup(fname)

makePerSamplePlots()
makeStackPlots()
