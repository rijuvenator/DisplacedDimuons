import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter

f = R.TFile.Open('roots/Fixed_All.root')
h = f.Get('h_LxyVSLxySig_Data')

proj = {}
DPHIBINS = 5

def reformat(string, DPHIBINS):
    if '0#pi' in string: return '     0'
    if '1#pi' in string: return string.replace('1#pi', '  #pi')
    if string == '{}#pi/{}'.format(DPHIBINS, DPHIBINS): return '#pi'
    return string

def getLumiStr(DPHIBINS, i):
    return '{} < |#Delta#Phi| < {}'.format(
        reformat('{}#pi/{}'.format(i  , DPHIBINS), DPHIBINS),
        reformat('{}#pi/{}'.format(i+1, DPHIBINS), DPHIBINS),
    )

for i in xrange(DPHIBINS):
    size = int(100./DPHIBINS)
    binRange = (1 + size*i, size*(i+1))
    h.GetXaxis().SetRange(*binRange)

    #h.GetYaxis().SetRange(1, 100)
    #h.GetZaxis().SetRange(1, 100)

    proj[i] = h.Project3D('new{}_y'.format(i))
    print proj[i].Integral()

c = Plotter.Canvas()#logy=True)
for i in xrange(DPHIBINS):
    proj[i].Scale(1./proj[i].Integral(0, 301))
    c.addMainPlot(Plotter.Plot(proj[i], getLumiStr(DPHIBINS, i), 'l', 'hist'))
    c.plotList[-1].setColor(i+1)
#c.firstPlot.setTitles(X='#sigma_{L_{xy}}', Y='Counts')
c.firstPlot.setTitles(X='L_{xy}', Y='Counts')
#c.firstPlot.setTitles(X='L_{xy}/#sigma_{L_{xy}}', Y='Counts')
c.makeLegend(lWidth=.2)
c.setMaximum()
c.firstPlot.GetXaxis().SetRangeUser(0., 20.)
c.legend.resizeHeight()
c.legend.moveLegend(X=-.1)
c.cleanup('plot.pdf')
