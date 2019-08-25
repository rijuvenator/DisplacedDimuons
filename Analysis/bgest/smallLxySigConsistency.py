import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT

# to make the LxySig < 6 plot
# supersedes, say, studyTransferFactorUncertainty (a bit of a misnomer)
#
# prepare two files, Full_SR_Less.txt and Full_CR_Less.txt
# which contain the data events with the full selection from DSADump
# with LxySig < 6; there were 60 and 55 events
#
# Also get the output of data on studyAsymmetryWithCuts with QCD and DY mode
#
# Finally, embed the "histogram" for SS events with LxySig < 6 passing
# full selection (with PAT association, etc.); there were 4 here
#
# config is from analyzeDSADump; I just need LxySig here
# the for loops later are from some scripts in this folder for parsing an
# inverted PAT dump

hists = {
    'Full_SR'        : R.TH1F('h_Full_SR'        , '', 6, 0., 6.),
    'Full_CR'        : R.TH1F('h_Full_CR'        , '', 6, 0., 6.),

    'PRev_SR'        : R.TH1F('h_PRev_SR'        , '', 6, 0., 6.),
    'PRev_CR'        : R.TH1F('h_PRev_CR'        , '', 6, 0., 6.),

    'PRev_SS'        : R.TH1F('h_PRev_SS'        , '', 6, 0., 6.),
    'PRev_OS'        : R.TH1F('h_PRev_OS'        , '', 6, 0., 6.),

    'Full_CR_Corr'   : R.TH1F('h_Full_CR_Corr'   , '', 6, 0., 6.),
    'Full_CR_Corr_SS': R.TH1F('h_Full_CR_Corr_SS', '', 6, 0., 6.),

}

# run over the SR and CR for full selection for OS
config = {
    'LxySig'   : {'cast':float, 'col':10},
}

for region in ('SR', 'CR'):
    with open('Full_{}_Less6.txt'.format(region)) as f:
        for line in f:
            cols = line.strip('\n').split()
            vals = {key:config[key]['cast'](cols[config[key]['col']]) for key in config}

            hists['Full_{}'.format(region)].Fill(vals['LxySig'])

# run over the inverted PAT files to get the high-stats transfer factors later
def whichRegion(deltaPhi):
    if   deltaPhi <    R.TMath.Pi()/4.: return 'SR'
    elif deltaPhi > 3.*R.TMath.Pi()/4.: return 'CR'
    return None

def safeDivide(a, b):
    try:
        return a/float(b)
    except:
        return 0.

c = 0
with open('DaddyDSA_DataOnly_LxySig1.txt') as f:
    for line in f:
        cols = line.strip('\n').split()
        PATLxySig = float(cols[14])
        DSALxySig = float(cols[15])
        deltaPhi  = float(cols[18])
        mass      = float(cols[-4])
        sign      = cols[-1]

        region = whichRegion(deltaPhi)

        if region is None: continue

        if sign == 'OS':
            hists['PRev_{}'.format(region)].Fill(DSALxySig)

        #if c > 10000: break
        c += 1

with open('DaddyDSA_DataOnly_LxySig60-115.txt') as f:
    for line in f:

        cols = line.strip('\n').split()
        PATLxySig = float(cols[14])
        DSALxySig = float(cols[15])
        deltaPhi  = float(cols[18])
        mass      = float(cols[-4])
        sign      = cols[-1]

        region = whichRegion(deltaPhi)

        if region is None: continue

        if region == 'SR':
            hists['PRev_{}'.format(sign)  ].Fill(DSALxySig)

# same sign "histogram"
SameSignHistProxy = {
    1 : 1,
    2 : 2,
    3 : 0,
    4 : 0,
    5 : 0,
    6 : 1,
}

# for each bin, get the DY transfer factor, propagate the error correctly, fill corrected histograms and set errors
for ibin in xrange(1, hists['PRev_SR'].GetNbinsX()+1):

    PRevSR, PRevCR, PRevOS, PRevSS = [hists[x].GetBinContent(ibin) for x in ('PRev_SR', 'PRev_CR', 'PRev_OS', 'PRev_SS')]

    factor = safeDivide(PRevSR, PRevCR)
    errorFactor = factor * ( 1./PRevSR + 1./PRevCR )**0.5
    print 'DY  : {} : {:6.0f} {:6.0f} {:.3f}'.format(ibin, PRevSR, PRevCR, factor)

    hists['Full_CR_Corr'].SetBinContent(ibin, hists['Full_CR'].GetBinContent(ibin) * factor)
    
    error = hists['Full_CR_Corr'].GetBinContent(ibin) * ( safeDivide(1., hists['Full_CR'].GetBinContent(ibin)) + (errorFactor/factor)**2. )**0.5
    hists['Full_CR_Corr'].SetBinError(ibin, error)

    ssFactor = safeDivide(PRevOS, PRevSS)
    errorSSFactor = ssFactor * (1./PRevOS + 1./PRevSS)**0.5
    print 'QCD : {} : {:6.0f} {:6.0f} {:.3f}'.format(ibin, PRevOS, PRevSS, ssFactor)

    hists['Full_CR_Corr_SS'].SetBinContent(ibin, hists['Full_CR'].GetBinContent(ibin) * factor + SameSignHistProxy[ibin] * ssFactor)

    ssError = SameSignHistProxy[ibin] * ssFactor * ( safeDivide(1., SameSignHistProxy[ibin]) + (errorSSFactor/ssFactor)**2. )**0.5
    totalError = (error**2. + ssError**2.)**0.5
    hists['Full_CR_Corr_SS'].SetBinError(ibin, totalError)

# Garwood error bars
hists['Full_SR'].SetBinErrorOption(R.TH1.kPoisson)

# make the plot
p = {
    'SR'         : Plotter.Plot(hists['Full_SR'        ], 'SR'          , 'elp', 'pe'),
    'CR'         : Plotter.Plot(hists['Full_CR'        ], 'CR'          , 'elp', 'pe'),
    'CR_Corr'    : Plotter.Plot(hists['Full_CR_Corr'   ], 'CR w/ DY'    , 'elp', 'pe'),
    'CR_Corr_SS' : Plotter.Plot(hists['Full_CR_Corr_SS'], 'CR w/ DY+QCD', 'elp', 'pe'),
}

c = Plotter.Canvas(lumi='Data 2016, 36.3 fb^{-1} (13 TeV)', cWidth=600)
c.addMainPlot(p['SR'        ])
c.addMainPlot(p['CR_Corr_SS'])
c.addMainPlot(p['CR_Corr'   ])
c.addMainPlot(p['CR'        ])

colors = {'SR':R.kRed, 'CR_Corr_SS':R.kViolet, 'CR_Corr':R.kGreen+1, 'CR':R.kAzure}
for key in p: p[key].setColor(colors[key], which='LM')

c.makeLegend(pos='tr', lWidth=.35, autoOrder=False)
c.legend.addLegendEntry(p['SR'        ])
c.legend.addLegendEntry(p['CR'        ])
c.legend.addLegendEntry(p['CR_Corr'   ])
c.legend.addLegendEntry(p['CR_Corr_SS'])
c.legend.resizeHeight()

c.firstPlot.setTitles(X='L_{xy}/#sigma_{L_{xy}}', Y='Events')

c.cleanup('smallLxySig.pdf', mode='LUMI')

for other in ('CR', 'CR_Corr', 'CR_Corr_SS'):
    c = Plotter.Canvas(lumi='Data 2016, 36.3 fb^{-1} (13 TeV)', cWidth=600)
    c.addMainPlot(p['SR' ])
    c.addMainPlot(p[other])

    p['SR' ].setColor(colors['SR' ], which='LM')
    p[other].setColor(colors[other], which='LM')

    c.makeLegend(pos='tr', lWidth=.35, autoOrder=False)
    c.legend.addLegendEntry(p['SR' ])
    c.legend.addLegendEntry(p[other])
    c.legend.resizeHeight()

    c.firstPlot.setTitles(X='L_{xy}/#sigma_{L_{xy}}', Y='Events')

    c.cleanup('smallLxySig_{}.pdf'.format(other), mode='LUMI')
