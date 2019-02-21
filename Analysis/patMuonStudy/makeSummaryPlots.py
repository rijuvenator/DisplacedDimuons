import DisplacedDimuons.Analysis.SummaryPlotter as SumPlotter
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import DisplacedDimuons.Analysis.HistogramGetter as HG
R, makeSummaryPlot, initializeData, Plotter = SumPlotter.R, SumPlotter.makeSummaryPlot, SumPlotter.initializeData, SumPlotter.Plotter

DATA = initializeData()
with open('text/replacePAT.txt') as f:
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
        print '{:17s} {:5.0f} {:.4%}'.format(str(sp), DATA[fs][sp]['PAT-vtxChi2-Overflow'], DATA[fs][sp]['PAT-vtxChi2-Overflow']/h.Integral(0, h.GetNbinsX()+1))

    FITRANGES = {
            (1000, 150, 1000) : {'PAT' : (-.01, .01)},
            (1000, 50, 400  ) : {'PAT' : (-.01, .01)},
            (1000, 20, 20   ) : {'PAT' : (-.02, .02) ,
                                 'DSA' : (-15., 15 )},
            (1000, 20, 200  ) : {'PAT' : (-.01, .01) ,
                                 'DSA' : (-20., 20.)},
            (400, 150, 4000 ) : {'PAT' : (-.01, .01)},
            (400, 50, 800   ) : {'PAT' : (-.01, .01) ,
                                 'DSA' : (-15., 15 )},
            (400, 20, 40    ) : {'DSA' : (-15., 15 )},
            (400, 20, 400   ) : {'PAT' : (-.01, .01) ,
                                 'DSA' : (-15., 15 )},
            (200, 50, 2000  ) : {'PAT' : (-.01, .01) ,
                                 'DSA' : (-15., 15 )},
            (200, 20, 700   ) : {'PAT' : (-.01, .01) ,
                                 'DSA' : (-15., 15 )},
            (125, 50, 500   ) : {'PAT' : (-.01, .01) ,
                                 'DSA' : (-15., 15 )},
            (125, 50, 5000  ) : {'PAT' : (-.01, .01) ,
                                 'DSA' : (-15., 15 )},
            (125, 20, 130   ) : {'PAT' : (-.01, .01) ,
                                 'DSA' : (-15., 15 )},
            (125, 20, 1300  ) : {'PAT' : (-.01, .01) ,
                                 'DSA' : (-15., 15 )},
    }

    h = HG.getHistogram(f, (fs, sp), 'PAT-LxyRes')
    if sp in FITRANGES and 'PAT' in FITRANGES[sp]:
        FR = FITRANGES[sp]['PAT']
    else:
        FR = (-.05, .05)
    func = R.TF1('f', 'gaus', *FR)
    h.Fit('f', 'R')
    DATA[fs][sp]['PAT-LxyRes-Mean'] = abs(func.GetParameter(1))
    DATA[fs][sp]['PAT-LxyRes-StdDev'] = func.GetParameter(2)
    #DATA[fs][sp]['PAT-LxyRes'] = h.GetStdDev()

    h = HG.getHistogram(f, (fs, sp), 'DSA-LxyRes')
    if sp in FITRANGES and 'DSA' in FITRANGES[sp]:
        FR = FITRANGES[sp]['DSA']
    else:
        FR = (-5., 5.)
    func = R.TF1('f', 'gaus', *FR)
    h.Fit('f', 'R')
    DATA[fs][sp]['DSA-LxyRes-Mean'] = abs(func.GetParameter(1))
    DATA[fs][sp]['DSA-LxyRes-StdDev'] = func.GetParameter(2)
    #DATA[fs][sp]['DSA-LxyRes'] = h.GetStdDev()

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('repPct',),
    ';;% replaced',
    {'repPct':'% replaced'},
    {'repPct':R.kRed},
    {'min':0., 'max':100.},
    'pdfs/PAT_percentReplaced_Combined_2Mu2J.pdf'
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('PAT-LxySig', 'DSA-LxySig'),
    ';;#LTL_{xy}/#sigma_{L_{xy}}#GT',
    {'PAT-LxySig':'PAT', 'DSA-LxySig':'DSA'},
    {'PAT-LxySig':R.kRed, 'DSA-LxySig':R.kRed+2},
    {'min':0., 'max':2500.},
    'pdfs/PAT_LxySig_Mean_Combined_2Mu2J.pdf',
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
#    'pdfs/PAT_LxySig_Overflow_Combined_2Mu2J.pdf',
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
#    'pdfs/PAT_LxySig_Overflow_Combined_2Mu2J.pdf',
#)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('Frac-LxySig-Overflow',),
    ';;% overflow of L_{xy}/#sigma_{L_{xy}}',
    {'Frac-LxySig-Overflow':'Overflow',},
    {'Frac-LxySig-Overflow':R.kRed,},
    {'min':0., 'max':100.},
    'pdfs/PAT_Frac-LxySig_Overflow_Combined_2Mu2J.pdf',
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('PAT-vtxChi2',),
    ';;#LTvtx #chi^{2}/dof#GT',
    {'PAT-vtxChi2':'chi2',},
    {'PAT-vtxChi2':R.kRed,},
    {'min':0., 'max':100.},
    'pdfs/PAT_vtxChi2_Combined_2Mu2J.pdf',
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('DSA-LxyRes-StdDev', 'PAT-LxyRes-StdDev'),
    ';;Fitted Gaussian #sigma : reco L_{xy} #minus gen L_{xy} [cm]',
    {'PAT-LxyRes-StdDev':'PAT', 'DSA-LxyRes-StdDev':'DSA'},
    {'PAT-LxyRes-StdDev':R.kRed, 'DSA-LxyRes-StdDev':R.kRed+2},
    {'min':1.e-3, 'max':100.},
    'pdfs/PAT_LxyRes_StdDev_Combined_2Mu2J.pdf',
    'tl',
    True
)

makeSummaryPlot(
    DATA,
    '2Mu2J',
    ('DSA-LxyRes-Mean', 'PAT-LxyRes-Mean'),
    ';;Fitted Gaussian #mu : reco L_{xy} #minus gen L_{xy} [cm]',
    {'PAT-LxyRes-Mean':'PAT', 'DSA-LxyRes-Mean':'DSA'},
    {'PAT-LxyRes-Mean':R.kRed, 'DSA-LxyRes-Mean':R.kRed+2},
    {'min':1.e-7, 'max':40.},
    'pdfs/PAT_LxyRes_Mean_Combined_2Mu2J.pdf',
    'tl',
    True
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
    c.cleanup('pdfs/MC_'+hkey+'.pdf')
