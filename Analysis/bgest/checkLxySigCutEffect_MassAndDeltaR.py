import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT

# make a bunch of Hists.root with
# for i in {1..10}; do makeAsymmetryHists.py DaddyDSA.txt --cutoff $i & done
# then this will make the comparison plot across cuts

HISTS = {'Mass' : {}, 'DeltaR' : {}, 'DeltaPhi' : {}}

for i in xrange(1,11):
#   HISTS['Mass'    ][i] = R.TH1F('mass_{}'    .format(i), ';m_{#mu#mu} [GeV];Frequency', 200, 0., 200.        )
    HISTS['Mass'    ][i] = R.TH1F('mass_{}'    .format(i), ';m_{#mu#mu} [GeV];Frequency', 40 , 0.,  40.        )
    HISTS['DeltaR'  ][i] = R.TH1F('deltaR_{}'  .format(i), ';#DeltaR(#mu#mu);Frequency' , 50 , 0.,   5.        )
    HISTS['DeltaPhi'][i] = R.TH1F('deltaPhi_{}'.format(i), ';|#Delta#Phi|;Frequency'    , 100, 0., R.TMath.Pi())

for line in open('DaddyDSA_DataOnly_OS_LxySig60-115.txt'):
#for line in open('DaddyDSA_DataOnly_OS_LxySig1.txt'):
    cols = line.strip('\n').split()

    PATLxySig = float(cols[14])
    DSALxySig = float(cols[15])
    deltaPhi  = float(cols[18])
    mass      = float(cols[27])
    deltaR    = float(cols[28])

    for i in xrange(1, 11):
        if i < DSALxySig:
            HISTS['Mass'    ][i].Fill(mass)
            HISTS['DeltaR'  ][i].Fill(deltaR)
            HISTS['DeltaPhi'][i].Fill(deltaPhi)

colors = {
    1 : R.kRed,
    2 : R.kOrange+7,
    3 : R.kOrange,
    4 : R.kYellow,
    5 : R.kGreen,
    6 : R.kGreen+2,
    7 : R.kTeal+5,
    8 : R.kBlue,
    9 : R.kViolet+1,
    10: R.kMagenta
}

# these plots are square (for my thesis)
# remove the cWidth argument, remove the mode argument, and remove the scaleTitleOffsets call for rectangular

for key in HISTS:
    c = Plotter.Canvas(lumi='Data 2016, 36.3 fb^{-1} (13 TeV)', cWidth=600 if key != 'DeltaPhi' else 800)
    plots = {i:Plotter.Plot(HISTS[key][i], 'L_{{xy}}/#sigma_{{L_{{xy}}}} > {}'.format(i), 'l', 'hist') for i in HISTS[key]}
    for i in xrange(1,11):
        plots[i].Scale(1./plots[i].Integral(0, plots[i].GetNbinsX()+1))
        plots[i].Rebin(2)
        c.addMainPlot(plots[i])
        plots[i].setColor(colors[i])
    c.makeLegend(pos='tr', fontscale=.7, lWidth=.2)
    #c.firstPlot.SetMaximum(0.05)
    c.setMaximum()
    c.firstPlot.SetMinimum(0.)
    #c.firstPlot.setTitles(Y='Frequency', X='|#Delta#Phi|')
    c.legend.resizeHeight()
    if key == 'deltaR':
        c.legend.moveLegend(X=-.3)
    if key != 'DeltaPhi' : c.firstPlot.scaleTitleOffsets(1.3, 'Y')
    c.cleanup('BGEST_EffectOfLxySigCut_{}_Data.pdf'.format(key), mode='LUMI')
