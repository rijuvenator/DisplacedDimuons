import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT

MAGICNUMBER = 16

def getBinFromNum(num):
    return '{:>04s}'.format(str(bin(num))[2:])

def getNumFromBin(b):
    return int('0b'+b, 2)

def getKeyFromNum(num):
    b = getBinFromNum(num)
    ACRO = 'TARS'
    i = '{}{}{}{}'.format(*[ACRO[x] if b[x]=='1' else '' for x in xrange(len(b))])
    return i if i != '' else 'X'

def getNumFromKey(key):
    n = 0
    if 'T' in key: n += 8
    if 'A' in key: n += 4
    if 'R' in key: n += 2
    if 'S' in key: n += 1
    return n

def getHKeyFromKey(key):
    return 'Lxy-Trig{}-Acc{}-Reco{}-Sel{}'.format(
        '1' if 'T' in key else '0',
        '1' if 'A' in key else '0',
        '1' if 'R' in key else '0',
        '1' if 'S' in key else '0',
    )

FILE = R.TFile.Open('SignalEfficiencies_R.root')
#HISTS = HG.getAddedSignalHistograms(FILE, '2Mu2J', [getHKeyFromKey(getKeyFromNum(num)) for num in xrange(MAGICNUMBER)])
HISTS = {getHKeyFromKey(getKeyFromNum(num)):HG.getHistogram(FILE, ('2Mu2J', (1000, 350, 3500)), getHKeyFromKey(getKeyFromNum(num))) for num in xrange(MAGICNUMBER)}
#HISTS = {getHKeyFromKey(getKeyFromNum(num)):HG.getHistogram(FILE, ('2Mu2J', (200, 50, 2000)), getHKeyFromKey(getKeyFromNum(num))) for num in xrange(MAGICNUMBER)}

def getHist(keys):
    for i, key in enumerate(keys):
        if i == 0:
            h = HISTS[getHKeyFromKey(key)].Clone()
        else:
            h.Add(HISTS[getHKeyFromKey(key)])
    return h

def makePlot(config, order, fname, lumi):
    g = {}
    p = {}
    for key in config:
        hNum = getHist(config[key]['numer'])
        hDen = getHist(config[key]['denom'])
        hNum.Rebin(5)
        hDen.Rebin(5)
        g[key] = R.TGraphAsymmErrors(hNum, hDen, 'cp')
        p[key] = Plotter.Plot(g[key], config[key]['leg'], 'lp', 'pe')

    c = Plotter.Canvas(lumi=lumi)
    for key in order:
        c.addMainPlot(p[key])
        p[key].setColor(config[key]['col'], which='LM')

    if False:
        c.makeLegend(lWidth=.125, pos='tl')
        c.legend.resizeHeight()
        c.legend.moveLegend(X=.06, Y=-.4)

    if True:
        c.makeLegend(lWidth=.125, pos='tr')
        c.legend.resizeHeight()
        #c.legend.moveLegend(X=-.3)

    c.firstPlot.SetMinimum(0.)
    c.firstPlot.SetMaximum(1.)
    c.firstPlot.setTitles(X='gen L_{xy} [cm]', Y='Efficiency')

    #c.firstPlot.GetXaxis().SetRangeUser(0., 250.)

    c.cleanup('{}.pdf'.format(fname))

KEYS = {num:getKeyFromNum(num) for num in xrange(MAGICNUMBER)}

# for status report, for form factor harmony with run 1,
# colors are black, red, blue in that order, and width was square (so 600)

ALL_REGIONS  = [KEYS[num] for num in KEYS                                                              ]
TRIG_REGIONS = [KEYS[num] for num in KEYS if 'T' in KEYS[num]                                          ]
RECO_REGIONS = [KEYS[num] for num in KEYS if 'R' in KEYS[num] and 'T' in KEYS[num]                     ]
SEL_REGIONS  = [KEYS[num] for num in KEYS if 'S' in KEYS[num] and 'R' in KEYS[num] and 'T' in KEYS[num]]

config = {
    'trig' : {'numer':TRIG_REGIONS  , 'denom':ALL_REGIONS , 'col':R.kRed  , 'leg':'Trigger Efficiency'       },
    'reco' : {'numer':RECO_REGIONS  , 'denom':ALL_REGIONS , 'col':R.kBlue , 'leg':'Reconstruction Efficiency'},
    'full' : {'numer':SEL_REGIONS   , 'denom':ALL_REGIONS , 'col':R.kBlack, 'leg':'Full Efficiency'          },
}
order = ('trig', 'reco', 'full')

makePlot(config, order, 'Eff', '2#mu Signal')

ACC_REGIONS  = [KEYS[num] for num in KEYS if 'A' in KEYS[num]]
TRIG_REGIONS = [key for key in TRIG_REGIONS if 'A' in key]
RECO_REGIONS = [key for key in RECO_REGIONS if 'A' in key]
SEL_REGIONS  = [key for key in SEL_REGIONS  if 'A' in key]

config = {
    'trig' : {'numer':TRIG_REGIONS  , 'denom':ACC_REGIONS , 'col':R.kRed  , 'leg':'Trigger Efficiency'       },
    'reco' : {'numer':RECO_REGIONS  , 'denom':ACC_REGIONS , 'col':R.kBlue , 'leg':'Reconstruction Efficiency'},
    'full' : {'numer':SEL_REGIONS   , 'denom':ACC_REGIONS , 'col':R.kBlack, 'leg':'Full Efficiency'          },
}
order = ('trig', 'reco', 'full')

makePlot(config, order, 'EffAcc', '2#mu Signal in Acceptance')

ALL_REGIONS  = [KEYS[num] for num in KEYS                                                              ]
TRIG_REGIONS = [KEYS[num] for num in KEYS if 'T' in KEYS[num]                                          ]
RECO_REGIONS = [KEYS[num] for num in KEYS if 'R' in KEYS[num] and 'T' in KEYS[num]                     ]
SEL_REGIONS  = [KEYS[num] for num in KEYS if 'S' in KEYS[num] and 'R' in KEYS[num] and 'T' in KEYS[num]]

config = {
    'trig' : {'numer':TRIG_REGIONS  , 'denom':ALL_REGIONS , 'col':R.kRed  , 'leg':'Trigger Efficiency'       },
    'reco' : {'numer':RECO_REGIONS  , 'denom':TRIG_REGIONS, 'col':R.kBlue , 'leg':'Reconstruction Efficiency'},
    'full' : {'numer':SEL_REGIONS   , 'denom':RECO_REGIONS, 'col':R.kBlack, 'leg':'Full Efficiency'          },
}
order = ('trig', 'reco', 'full')

makePlot(config, order, 'Test', '2#mu Signal')

ACC_REGIONS  = [KEYS[num] for num in KEYS if 'A' in KEYS[num]]
TRIG_REGIONS = [key for key in TRIG_REGIONS if 'A' in key]
RECO_REGIONS = [key for key in RECO_REGIONS if 'A' in key]
SEL_REGIONS  = [key for key in SEL_REGIONS  if 'A' in key]

config = {
    'trig' : {'numer':TRIG_REGIONS  , 'denom':ACC_REGIONS , 'col':R.kRed  , 'leg':'Trigger Efficiency'       },
    'reco' : {'numer':RECO_REGIONS  , 'denom':TRIG_REGIONS, 'col':R.kBlue , 'leg':'Reconstruction Efficiency'},
    'full' : {'numer':SEL_REGIONS   , 'denom':RECO_REGIONS, 'col':R.kBlack, 'leg':'Full Efficiency'          },
}
order = ('trig', 'reco', 'full')

makePlot(config, order, 'TestAcc', '2#mu Signal in Acceptance')
