import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
import argparse

# this script supersedes the old checkLxySigCutEffect script
# now it just takes the actual text files as input
# You need a MC (DY style) and data files (DY and QCD style)

parser = argparse.ArgumentParser()
parser.add_argument('--mc'   , dest='MC'   , action='store_true')
parser.add_argument('--style', dest='STYLE', choices=['DY', 'QCD'], default='DY')
args = parser.parse_args()

HISTS = {'Mass' : {}, 'DeltaR' : {}, 'DeltaPhi' : {}}

MassArgs = {
    'DY' : (200, 0., 200.),
    'QCD': ( 60, 0., 120.),
}

for i in xrange(1,11):
    HISTS['Mass'    ][i] = R.TH1F('mass_{}'    .format(i), ';m_{#mu#mu} [GeV];Frequency', *MassArgs[args.STYLE])
    HISTS['DeltaR'  ][i] = R.TH1F('deltaR_{}'  .format(i), ';#DeltaR(#mu#mu);Frequency' , 50 , 0.,   5.        )
    HISTS['DeltaPhi'][i] = R.TH1F('deltaPhi_{}'.format(i), ';|#Delta#Phi|;Frequency'    , 100, 0., R.TMath.Pi())

for line in open('DaddyDSA_{}Only_LxySig{}.txt'.format('Data' if not args.MC else 'MC', '1' if args.STYLE == 'DY' else '60-115')):
    cols = line.strip('\n').split()

    name      =       cols[ 0]
    weight    = float(cols[ 4])
    PATLxySig = float(cols[14])
    DSALxySig = float(cols[15])
    deltaPhi  = float(cols[18])
    mass      = float(cols[27])
    deltaR    = float(cols[28])
    sign      =       cols[30]

    if args.MC and 'DY50' not in name: continue

    for i in xrange(1, 11):
        if i < DSALxySig:
            if args.STYLE == 'DY' and PATLxySig > 1.: continue
            if deltaPhi < R.TMath.Pi()/4.:
                HISTS['Mass'    ][i].Fill(mass,     weight)
                HISTS['DeltaR'  ][i].Fill(deltaR,   weight)
            if True:
                HISTS['DeltaPhi'][i].Fill(deltaPhi, weight)

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
    label = 'Data 2016' if not args.MC else 'Drell-Yan Simulation'
    #notsquare = (key == 'DeltaPhi' and args.STYLE == 'QCD')
    notsquare = False
    c = Plotter.Canvas(lumi='{}, 36.3 fb^{{-1}} (13 TeV)'.format(label), cWidth=800 if notsquare else 600)
    plots = {i:Plotter.Plot(HISTS[key][i], 'L_{{xy}}/#sigma_{{L_{{xy}}}} > {}'.format(i), 'l', 'hist') for i in HISTS[key]}
    for i in xrange(1,11):
        plots[i].Scale(1./plots[i].Integral(0, plots[i].GetNbinsX()+1))
        plots[i].Rebin(2)
        c.addMainPlot(plots[i])
        plots[i].setColor(colors[i])
    c.makeLegend(pos='tr', fontscale=.7, lWidth=.2)
    if False and key == 'DeltaPhi':
        c.firstPlot.SetMaximum(0.05)
    else:
        c.setMaximum()
    c.firstPlot.SetMinimum(0.)
    c.legend.resizeHeight()
    if key == 'deltaR':
        c.legend.moveLegend(X=-.3)
    if not notsquare : c.firstPlot.scaleTitleOffsets(1.3, 'Y')
    c.cleanup('BGEST_EffectOfLxySigCut_{}_{}_{}-Like.pdf'.format(key, 'Data' if not args.MC else 'MC', args.STYLE), mode='LUMI')
