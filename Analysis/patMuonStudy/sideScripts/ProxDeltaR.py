import sys
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT

# takes in event lines with
# - sample name as column 0
# - +/-1 weight as column 4 (because R, L, E are 1, 2, 3)
# ProxDeltaR1, ProxDeltaR2 as columns -2, -1, possibly inf

DOSQUARED = False

l = HG.BGORDER + ('data',)

hists = {}
for key in l:
    if DOSQUARED:
        hists[key] = R.TH1F('h'+key, ';#DeltaR^{2};Normalized Counts', 100, 0., .16)
    else:
        hists[key] = R.TH1F('h'+key, ';#DeltaR;Normalized Counts', 100, 0., .4)

with open(sys.argv[1]) as f:
    for line in f:
        cols = line.strip('\n').split()

        if cols[0] in l:
            weight = HG.PLOTCONFIG[cols[0]]['WEIGHT'] * int(cols[4]) * .100033
            key = cols[0]
        else: # data
            weight = 1.
            key = 'data'

        for val in (cols[-2], cols[-1]):
            if val == 'inf':
                hists[key].Fill(100., weight)
            else:
                hists[key].Fill(float(val)**(2. if DOSQUARED else 1.), weight)

stack = R.THStack('hstack', '')
p = {}
for key in l:
    RT.addFlows(hists[key])
    if key == 'data': continue
    stack.Add(hists[key])
    p[key] = Plotter.Plot(hists[key], HG.PLOTCONFIG[key]['LATEX'], 'f', 'hist')
    p[key].setColor(HG.PLOTCONFIG[key]['COLOR'], which='LF')

p['stack'] = Plotter.Plot(stack, '', '', 'hist')
p['data'] = Plotter.Plot(hists['data'], 'DoubleMuon2016', 'lp', 'pe')

c = Plotter.Canvas(logy=True)
c.addMainPlot(p['stack'])
c.addMainPlot(p['data'])
c.makeLegend(lWidth=.27, pos='tr', autoOrder=False, fontscale=0.8)
for ref in reversed(l):
    c.addLegendEntry(p[ref])
c.legend.resizeHeight()
c.firstPlot.setTitles(X='', Y='', copy=p['ttbar'])
c.setMaximum(recompute=True)
c.firstPlot.SetMinimum(1.e-3)

c.cleanup('DR{}.pdf'.format('' if not DOSQUARED else '2'))
