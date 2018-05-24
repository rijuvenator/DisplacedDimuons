import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.Selections as Selections
from DisplacedDimuons.Common.Constants import RECOSIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr

Patterns = {
    'HTo2XTo4Mu' : re.compile(r'(.*)_HTo2XTo4Mu_(\d{3,4})_(\d{2,3})_(\d{1,4})')
}
for sample in ('DY100to200', 'DoubleMuonRun2016D-07Aug17'):
    Patterns[sample] = re.compile(r'(.*)_'+sample)

# get all histograms
HISTS = {}
f = R.TFile.Open('../analyzers/roots/nMinusOne.root')
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

# make per signal plots
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
            fname = 'pdfs/NM1_{}_{}.pdf'.format(key, name)
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

# make stack plots
def makeStackPlots(DataMC=False):
    #for hkey in HISTS[(125, 20, 13)]:
    for hkey in ('deltaR_Less',):
        h = {
            'DY100to200' : HISTS['DY100to200'                ][hkey],
            'Data'       : HISTS['DoubleMuonRun2016D-07Aug17'][hkey],
            'Signal'     : HISTS[(125, 20, 13)               ][hkey],
            'BG'         : R.THStack('hBG', '')
        }

        PConfig = {
            'DY100to200' : ('Drell-Yan 100-200 GeV'        , 'f' , 'hist'),
            'Data'       : ('DoubleMuon2016D'              , 'pe', 'pe'  ),
            'Signal'     : ('H#rightarrow2X#rightarrow4#mu', 'l' , 'hist'),
            'BG'         : (''                             , ''  , 'hist'),
        }

        h['BG'].Add(h['DY100to200'])

        p = {}
        for key in h:
            p[key] = Plotter.Plot(h[key], *PConfig[key])

        fname = 'NM1_Stack_{}.pdf'.format(hkey)

        p['DY100to200'].SetLineColor(R.kOrange)
        p['DY100to200'].SetFillColor(R.kOrange)

        canvas = Plotter.Canvas(ratioFactor=0. if not DataMC else 1./3., cHeight=600 if not DataMC else 800)
        canvas.addMainPlot(p['BG'])
        canvas.addMainPlot(p['Data'])
        canvas.addMainPlot(p['Signal'])

        canvas.makeLegend(lWidth=.25, pos='tl', autoOrder=False)
        canvas.addLegendEntry(p['Data'      ])
        canvas.addLegendEntry(p['DY100to200'])
        canvas.addLegendEntry(p['Signal'    ])
        canvas.legend.resizeHeight()

        if DataMC:
            canvas.makeRatioPlot(p['Data'].plot, p['BG'].plot.GetStack().Last())

        p['Signal'    ].SetLineStyle(2)
        p['Signal'    ].SetLineColor(R.kRed)

        Cleanup(canvas, fname)

makePerSignalPlots()
#makeStackPlots(True)
