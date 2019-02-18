import DisplacedDimuons.Analysis.SummaryPlotter as SumPlotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HG
R, makeSummaryPlot, initializeData, Plotter = SumPlotter.R, SumPlotter.makeSummaryPlot, SumPlotter.initializeData, SumPlotter.Plotter

DATA = initializeData()
with open('replacePAT.txt') as f:
    for line in f:
        if '%' in line or '---' in line: continue
        cols = line.strip('\n').split()
        fs = cols[0]
        sp = tuple(map(int, cols[1:4]))
        #DATA[fs][sp]['den'] = int(cols[4])
        #DATA[fs][sp]['num'] = int(cols[5])
        DATA[fs][sp]['repPct'] = float(cols[6])

f = R.TFile.Open('roots/PATMuonStudyPlots_Trig_Combined_BS8_2Mu2J.root')
fs = '2Mu2J'
for sp in SIGNALPOINTS:
    h = HG.getHistogram(f, (fs, sp), 'DSA-LxySig')
    DATA[fs][sp]['DSA-LxySig'] = h.GetMean()
    DATA[fs][sp]['DSA-LxySig-Overflow'] = h.GetBinContent(h.GetNbinsX()+1)

    h = HG.getHistogram(f, (fs, sp), 'PAT-LxySig')
    DATA[fs][sp]['PAT-LxySig'] = h.GetMean()
    DATA[fs][sp]['PAT-LxySig-Overflow'] = h.GetBinContent(h.GetNbinsX()+1)

    DATA[fs][sp]['Frac-LxySig-Overflow'] = h.GetBinContent(h.GetNbinsX()+1)/h.Integral(0, h.GetNbinsX()+1)*100.

    h = HG.getHistogram(f, (fs, sp), 'PAT-vtxChi2')
    DATA[fs][sp]['PAT-vtxChi2'] = h.GetMean()
    DATA[fs][sp]['PAT-vtxChi2-Overflow'] = h.GetBinContent(h.GetNbinsX()+1)

    if DATA[fs][sp]['PAT-vtxChi2-Overflow'] > 0.:
        print sp, DATA[fs][sp]['PAT-vtxChi2-Overflow'], '{:.4%}'.format(DATA[fs][sp]['PAT-vtxChi2-Overflow']/h.Integral(0, h.GetNbinsX()+1))

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('repPct',),
    ';;% replaced',
    {'repPct':'% replaced'},
    {'repPct':R.kRed},
    {'min':0., 'max':100.},
    'PAT_percentReplaced_Combined_2Mu2J.pdf'
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('PAT-LxySig', 'DSA-LxySig'),
    ';;#LTL_{xy}/#sigma_{L_{xy}}#GT',
    {'PAT-LxySig':'PAT', 'DSA-LxySig':'DSA'},
    {'PAT-LxySig':R.kRed, 'DSA-LxySig':R.kRed+2},
    {'min':0., 'max':2500.},
    'PAT_LxySig_Mean_Combined_2Mu2J.pdf',
    'tl'
)

#makeSummaryPlot(
#    DATA,
#    '2Mu2J',
#    ('PAT-LxySig-Overflow', 'DSA-LxySig-Overflow'),
#    ';;L_{xy}/#sigma_{L_{xy}} Overflow',
#    {'PAT-LxySig-Overflow':'PAT', 'DSA-LxySig-Overflow':'DSA'},
#    {'PAT-LxySig-Overflow':R.kRed, 'DSA-LxySig-Overflow':R.kRed+2},
#    {'min':0., 'max':500.},
#    'PAT_LxySig_Overflow_Combined_2Mu2J.pdf',
#    'tl'
#)

#makeSummaryPlot(
#    DATA,
#    '2Mu2J',
#    ('PAT-LxySig-Overflow',),
#    ';;% overflow of L_{xy}/#sigma_{L_{xy}}',
#    {'PAT-LxySig-Overflow':'Overflow',},
#    {'PAT-LxySig-Overflow':R.kRed,},
##   {'min':0., 'max':1500.},
##   {'min':0., 'max':2300.},
#    {'min':0., 'max':100.},
#    'PAT_LxySig_Overflow_Combined_2Mu2J.pdf',
#)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('Frac-LxySig-Overflow',),
    ';;% overflow of L_{xy}/#sigma_{L_{xy}}',
    {'Frac-LxySig-Overflow':'Overflow',},
    {'Frac-LxySig-Overflow':R.kRed,},
    {'min':0., 'max':100.},
    'PAT_Frac-LxySig_Overflow_Combined_2Mu2J.pdf',
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('PAT-vtxChi2',),
    ';;#LTvtx #chi^{2}/dof#GT',
    {'PAT-vtxChi2':'chi2',},
    {'PAT-vtxChi2':R.kRed,},
    {'min':0., 'max':100.},
    'PAT_vtxChi2_Combined_2Mu2J.pdf',
)

##########
f = R.TFile.Open('roots/PATMuonStudyPlots_Combined_BS8_MC.root')
BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf')
PC = HG.PLOTCONFIG
for hkey in ('PAT-LxySig', 'DSA-LxySig'):
    h = HG.getHistogram(f, BGORDER[0], hkey).Clone()
    h.Scale(PC[BGORDER[0]]['WEIGHT'])
    for ref in BGORDER[1:]:
        thisH = HG.getHistogram(f, ref, hkey).Clone()
        thisH.Scale(PC[ref]['WEIGHT'])
        h.Add(thisH)

    print hkey, h.GetMean()
    print hkey, 'Overflow', h.GetBinContent(h.GetNbinsX()+1)/h.Integral(0, h.GetNbinsX()+1)*100.

    h.Rebin(10)
    h.GetXaxis().SetRangeUser(0., 1000.)
    p = Plotter.Plot(h, '', 'l', 'hist')
    c = Plotter.Canvas(logy=True)
    c.addMainPlot(p)
    c.cleanup('plot_'+hkey+'.pdf')
