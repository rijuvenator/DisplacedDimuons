import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter

f = R.TFile.Open('roots/Fixed_All.root')
h = f.Get('h_LxyVSLxySig_Data')

proj = {}
DPHIBINS = 5

def reformat(string, DPHIBINS):
    if '0#pi' in string: return '0'
    if '1#pi' in string: return string.replace('1#pi', '#pi')
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

    if True:
        proj[i] = h.Project3D('new{}_z'.format(i))
        print proj[i].Integral()

        c = Plotter.Canvas(lumi=getLumiStr(DPHIBINS, i), logy=True)
        c.addMainPlot(Plotter.Plot(proj[i], '', '', 'hist'))
        c.drawText('n = {}'.format(proj[i].Integral()), (.6, .6))
        #c.firstPlot.setTitles(X='#sigma_{L_{xy}}', Y='Counts')
        #c.firstPlot.setTitles(X='L_{xy}', Y='Counts')
        c.firstPlot.setTitles(X='L_{xy}/#sigma_{L_{xy}}', Y='Counts')
        c.cleanup('plot_{}.pdf'.format(i))

    if False:
        proj[i] = h.Project3D('new{}_yz'.format(i))
        print proj[i].Integral()

        c = Plotter.Canvas(lumi=getLumiStr(DPHIBINS, i))
        #c = Plotter.Canvas()
        #R.gStyle.SetMarkerStyle(R.kDot)
        c.addMainPlot(Plotter.Plot(proj[i], '', '', 'colz'))
        c.mainPad.SetLogz()
        #c.firstPlot.SetMarkerStyle(R.kDot)
        if True:
            line = R.TLine(0., 0., 100./7., 100.)
            line.Draw()
        if False:
            line = R.TLine(7., 0., 7., 100.)
            line.Draw()
        c.scaleMargins(2., 'R')
        #c.scaleMargins(0.5, 'L')
        #c.firstPlot.setTitles(X='|#Delta#Phi|', Y='L_{xy}')
        #c.firstPlot.setTitles(X='L_{xy}/#sigma_{L_{xy}}', Y='L_{xy}')
        c.firstPlot.setTitles(X='#sigma_{L_{xy}}', Y='L_{xy}')
        c.cleanup('plot_{}.pdf'.format(i))
