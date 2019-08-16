import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter

# the input histogram here is just two histograms with LxySig < 6 and DeltaPhi < pi/4 and > 3pi/4 separately
# the script to make it is validateBackground which is in oldscripts now
# this script makes a little less sense now, also it is superseded by smallLxySigConsistency,
# but I'm leaving it here in case you want to see how to to the KS probability

f = R.TFile.Open('roots/ValidationPlots_DATA.root')

D, P = HG.getDataHistograms(f, ('LxySig_DPHI', 'LxySig_IDPHI'), addFlows=False)

h = {k:D[k]['data'] for k in D}

c = {k:h[k].GetCumulative(False) for k in h}

cumRatio = c['LxySig_IDPHI'].Clone()
cumRatio.Divide(c['LxySig_DPHI'])

for k in h:
    h[k].Rebin(5)

distRatio = h['LxySig_IDPHI'].Clone()
distRatio.Divide(h['LxySig_DPHI'])

pDist      = {k:Plotter.Plot(h[k], '#Delta#Phi {} #pi/2'.format('<' if '_DPHI' in k else '>'), 'lp', 'hist e') for k in h}
pCum       = {k:Plotter.Plot(c[k], '#Delta#Phi {} #pi/2'.format('<' if '_DPHI' in k else '>'), 'lp', 'hist') for k in c}
pCumRatio  = Plotter.Plot(cumRatio, '', '', 'hist')
pDistRatio = Plotter.Plot(distRatio, '', '', 'hist')

#### Plot 1
canvas = Plotter.Canvas()
canvas.addMainPlot(pCum['LxySig_IDPHI'])
canvas.addMainPlot(pCum['LxySig_DPHI'])
pCum ['LxySig_IDPHI'].setColor(R.kRed )
pCum ['LxySig_DPHI' ].setColor(R.kBlue)
canvas.makeLegend(lWidth=.2)
canvas.cleanup('pdfs/cum.pdf')

#### Plot 2
canvas = Plotter.Canvas()
canvas.addMainPlot(pCumRatio)
pCumRatio.setColor(R.kBlue)
pCumRatio.setTitles(Y='Ratio of CR/SR')
canvas.cleanup('pdfs/ratio.pdf')

#### Plot 3
canvas = Plotter.Canvas()
canvas.addMainPlot(pDist['LxySig_IDPHI'])
canvas.addMainPlot(pDist['LxySig_DPHI'])
pDist['LxySig_IDPHI'].setColor(R.kRed )
pDist['LxySig_DPHI' ].setColor(R.kBlue)
canvas.makeLegend(lWidth=.2)
canvas.cleanup('pdfs/dist.pdf')

#### Plot 4
canvas = Plotter.Canvas()
canvas.addMainPlot(pDistRatio)
pDistRatio.setColor(R.kBlue)
pDistRatio.setTitles(Y='Ratio of CR/SR')
canvas.cleanup('pdfs/ratioDist.pdf')

#### KS Probability
print h['LxySig_IDPHI'].KolmogorovTest(h['LxySig_DPHI'])
