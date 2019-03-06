import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter

FILES = {'_PATOnly':0, '_NoRep':0, '':0}
HISTS = {}
for key in FILES:
    FILES[key] = R.TFile.Open('roots/ZephyrPlots_Trig_Combined_BS9{}_2Mu2J.root'.format(key))
    HISTS[key] = HG.getAddedSignalHistograms(FILES[key], '2Mu2J', ('GEN-Lxy', 'GEN-Lxy-PAT', 'GEN-Lxy-HYB', 'GEN-Lxy-DSA'))

# relative signal match eff
h = {}
h['PAT'] = HISTS['_PATOnly']['GEN-Lxy'].Clone()
h['HYB'] = HISTS[''        ]['GEN-Lxy'].Clone()
h['DSA'] = HISTS['_NoRep'  ]['GEN-Lxy'].Clone()
for key in h:
    h[key].Rebin(5)

h['PAT'].Divide(h['DSA'])
h['HYB'].Divide(h['DSA'])

h.pop('DSA')

p = {}
config = {'PAT' : ('DSA-DSA or PAT-PAT only', R.kRed), 'HYB' : ('DSA-DSA, PAT-PAT, or DSA-PAT', R.kBlue)}
for key in h:
    p[key] = Plotter.Plot(h[key], config[key][0], 'lp', 'p')

canvas = Plotter.Canvas(lumi='2Mu2J')
for key in ('PAT', 'HYB'):
    canvas.addMainPlot(p[key])
    p[key].setColor(config[key][1], which='LM')

canvas.makeLegend(pos='br', lWidth=.5)
canvas.legend.resizeHeight()
canvas.legend.moveLegend(Y=.2)
canvas.legend.SetMargin(0.15)

canvas.firstPlot.setTitles(Y='Gen matches with / without DSA replacement')
canvas.firstPlot.SetMinimum(0.)
canvas.firstPlot.SetMaximum(1.1)
canvas.firstPlot.GetXaxis().SetRangeUser(0., 400.)

canvas.cleanup('pdfs/ZEP_relSigMatchEff.pdf')

# breakdown
plotKeys = {'_PATOnly':('SUM', 'PAT', 'DSA'), '':('SUM', 'PAT', 'DSA', 'HYB')}
for fkey in plotKeys:
    h = {}
    h['PAT'] = HISTS[fkey    ]['GEN-Lxy-PAT'].Clone()
    h['DSA'] = HISTS[fkey    ]['GEN-Lxy-DSA'].Clone()
    h['HYB'] = HISTS[fkey    ]['GEN-Lxy-HYB'].Clone()
    h['SUM'] = HISTS[fkey    ]['GEN-Lxy'    ].Clone()
    h['DEN'] = HISTS['_NoRep']['GEN-Lxy'    ].Clone()
    for key in h:
        h[key].Rebin(5)

    h['PAT'].Divide(h['DEN'])
    h['HYB'].Divide(h['DEN'])
    h['DSA'].Divide(h['DEN'])
    h['SUM'].Divide(h['DEN'])

    p = {}
    config = {'PAT' : ('PAT-PAT', R.kRed), 'HYB' : ('DSA-PAT', R.kBlue), 'DSA' : ('DSA-DSA', R.kGreen), 'SUM' : ('Sum', R.kBlack)}
    for key in plotKeys[fkey]:
        p[key] = Plotter.Plot(h[key], config[key][0], 'lp', 'p')

    canvas = Plotter.Canvas(lumi='2Mu2J')
    for key in plotKeys[fkey]:
        canvas.addMainPlot(p[key])
        p[key].setColor(config[key][1], which='LM')

    canvas.makeLegend(pos='br', lWidth=.5)
    canvas.legend.resizeHeight()
    canvas.legend.moveLegend(Y=.2-(0. if fkey == '_PATOnly' else .04))
    canvas.legend.SetMargin(0.15)

    canvas.firstPlot.setTitles(Y='Fraction of gen matches with DSA-DSA only')
    canvas.firstPlot.SetMinimum(0.)
    canvas.firstPlot.SetMaximum(1.1)
    canvas.firstPlot.GetXaxis().SetRangeUser(0., 400.)

    canvas.cleanup('pdfs/ZEP_relSigMatchEff_breakdown{}.pdf'.format(fkey))
