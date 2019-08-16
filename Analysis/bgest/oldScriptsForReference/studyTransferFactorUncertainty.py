import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT

FILES = {
    'Prompt' : R.TFile.Open('roots/Hists.root'),
    'Full'   : R.TFile.Open('roots/ValidationPlots_DATA.root'),
}

keyList = {
    'Prompt' : [
                'hLessLxySig'  ,
                'hMoreLxySig'  ,
                'hLessDeltaPhi',
                'hMoreDeltaPhi',
                ],
    'Full'   : ['LxySig_IDPHI', 'LxySig_DPHI'],
}

DHists = {'Prompt':{}, 'Full':{}}
for which in keyList:
    if which == 'Prompt':
        for key in keyList[which]:
            DHists[which][key] = HG.getHistogram(FILES[which], 'Data', key).Clone()
    else:
        D, P = HG.getDataHistograms(FILES[which], keyList[which], addFlows=False)
        DHists[which] = {key:D[key]['data'] for key in D}

#### Correction factors from "inverted PAT" CR and SR ####

# these are 0.5 bins

#DHists['Prompt']['hLessLxySig'].GetXaxis().SetRange(1, 12)
#DHists['Prompt']['hMoreLxySig'].GetXaxis().SetRange(1, 12)

# now they're 1 bins
DHists['Prompt']['hLessLxySig'].Rebin(2)
DHists['Prompt']['hMoreLxySig'].Rebin(2)

# up to 6
DHists['Prompt']['hLessLxySig'].GetXaxis().SetRange(1, 6)
DHists['Prompt']['hMoreLxySig'].GetXaxis().SetRange(1, 6)

print 'Less', DHists['Prompt']['hLessLxySig'].Integral(1, 6)
print 'More', DHists['Prompt']['hMoreLxySig'].Integral(1, 6)

#DHists['Prompt']['hLessLxySig'].Clone()
DHists['Prompt']['hLessLxySig'].Divide(DHists['Prompt']['hMoreLxySig'])

p = Plotter.Plot(DHists['Prompt']['hLessLxySig'], '', '', 'p')
c = Plotter.Canvas()
c.addMainPlot(p)
p.SetMarkerSize(2)
p.SetMarkerColor(R.kBlue)
p.setTitles(Y='Binwise SR Integral / CR Integral per 0.5')
c.cleanup('x.pdf')

##### "Corrected" CR distributions in "full" CR and SR #####

weights = []
for ibin in xrange(1, 13):
    weights.append(DHists['Prompt']['hLessLxySig'].GetBinContent(ibin))

# these are 0.05 bins

# now they're 0.5 bins
#DHists['Full']['LxySig_DPHI' ].Rebin(10)
#DHists['Full']['LxySig_IDPHI'].Rebin(10)

# now they're 1 bins
DHists['Full']['LxySig_DPHI' ].Rebin(20)
DHists['Full']['LxySig_IDPHI'].Rebin(20)

# up to 6
DHists['Full']['LxySig_DPHI' ].GetXaxis().SetRange(1, 6)
DHists['Full']['LxySig_IDPHI'].GetXaxis().SetRange(1, 6)

DHists['Full']['LxySig_IDPHI_Reweighted'] = DHists['Full']['LxySig_IDPHI'].Clone()

SSCounts = (3, 5, 1, 0, 3, 1)
OSINVCounts = (43, 57, 45, 19, 15, 13)
SSINVCounts = (35, 50, 32, 12, 11, 5)
OSINVCounts, SSINVCounts = zip(*((70, 52),
(97, 76),
(66, 40),
(27, 21),
(17, 14),
(19, 5 )))
SSEvents = {i+1:SSCounts[i]*float(OSINVCounts[i])/SSINVCounts[i] for i in xrange(6)}

#DHists['Full']['LxySig_IDPHI_Reweighted'].Multiply(DHists['Prompt']['hLessLxySig'])
#for ibin in xrange(1, 13):
for ibin in xrange(1, DHists['Full']['LxySig_IDPHI_Reweighted'].GetNbinsX()+1):
    DHists['Full']['LxySig_IDPHI_Reweighted'].SetBinContent(ibin, DHists['Full']['LxySig_IDPHI_Reweighted'].GetBinContent(ibin) * weights[ibin-1] + SSEvents[ibin])
    DHists['Full']['LxySig_IDPHI_Reweighted'].SetBinError  (ibin, DHists['Full']['LxySig_IDPHI_Reweighted'].GetBinContent(ibin)**0.5             )

p = {
    'SR'   : Plotter.Plot(DHists['Full']['LxySig_DPHI'            ], 'SR'          , 'pl', 'hist e'),
    'CR'   : Plotter.Plot(DHists['Full']['LxySig_IDPHI'           ], 'CR'          , 'pl', 'hist e'),
    'CRRW' : Plotter.Plot(DHists['Full']['LxySig_IDPHI_Reweighted'], 'CR corrected', 'pl', 'hist e'),
}
colors = {'SR':R.kBlack, 'CR':R.kRed, 'CRRW':R.kBlue}
c = Plotter.Canvas()
for key in ('CR', 'CRRW', 'SR'):
    c.addMainPlot(p[key])
    print key, p[key].Integral()
    p[key].setColor(colors[key])
c.makeLegend(lWidth=.2)
c.legend.resizeHeight()
c.setMaximum(recompute=True)
c.firstPlot.SetMaximum(60.)
c.cleanup('y.pdf')

##### Ratios #####

Ratios = {}
Ratios['UC'] = p['SR'].Clone(); Ratios['UC'].Divide(p['CR'  ].plot)
Ratios['CC'] = p['SR'].Clone(); Ratios['CC'].Divide(p['CRRW'].plot)

for ibin in xrange(1, Ratios['UC'].GetNbinsX()+1):
    print p['SR'].GetBinContent(ibin), p['CR'].GetBinContent(ibin), Ratios['UC'].GetBinContent(ibin)

pp = {
    'UC'   : Plotter.Plot(Ratios['UC'], 'SR/CR'          , 'pl', 'hist e'),
    'CC'   : Plotter.Plot(Ratios['CC'], 'SR/CR corrected', 'pl', 'hist e'),
}

# set errors
for ibin in xrange(1, pp['UC'].GetNbinsX()+1):
    a, b = p['SR'].GetBinContent(ibin), p['CR'].GetBinContent(ibin)
    pp['UC'].SetBinError(ibin, (a/b) * ( (a**0.5/a)**2. + (b**0.5/b)**2. )**0.5 )
    a, b = p['SR'].GetBinContent(ibin), p['CRRW'].GetBinContent(ibin)
    pp['CC'].SetBinError(ibin, (a/b) * ( (a**0.5/a)**2. + (b**0.5/b)**2. )**0.5 )

colors = {'UC':R.kRed, 'CC':R.kBlue}
c = Plotter.Canvas()
for key in ('UC', 'CC'):
    c.addMainPlot(pp[key])
    pp[key].setColor(colors[key])
c.makeLegend(lWidth=.24)
c.legend.resizeHeight()
c.setMaximum(recompute=True)
c.firstPlot.SetMaximum(2.)
c.firstPlot.setTitles(Y='Ratio of SR/CR')
c.cleanup('z.pdf')
