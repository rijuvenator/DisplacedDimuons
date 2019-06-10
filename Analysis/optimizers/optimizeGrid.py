import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Analysis.HistogramGetter as HG
import re, itertools

FIGURE_OF_MERIT = 'ZBi'
#FIGURE_OF_MERIT = 'ZPL'

R.gStyle.SetPadTickY(0)

FILES = {
    'Signal' : R.TFile.Open('roots/HaikuPlots_Trig_HTo2XTo2Mu2J.root'),
    'Data'   : R.TFile.Open('roots/HaikuPlots_IDPHI_DATA.root'),
}

SignalInfo = {
#   (1000, 350,   35) : {'nEvents':27999, 'sigmaBLimit' : 0.     },
    (1000, 350,  350) : {'nEvents':29997, 'sigmaBLimit' : 2.5e-3 },
    (1000, 350, 3500) : {'nEvents':27999, 'sigmaBLimit' : 3.5e-3 },
#   (1000, 150,   10) : {'nEvents':26000, 'sigmaBLimit' : 0.     },
    (1000, 150,  100) : {'nEvents':30000, 'sigmaBLimit' : 4.0e-3 },
    (1000, 150, 1000) : {'nEvents':29000, 'sigmaBLimit' : 1.7e-3 },
#   (1000,  50,    4) : {'nEvents':30000, 'sigmaBLimit' : 0.     },
    (1000,  50,   40) : {'nEvents':28000, 'sigmaBLimit' : 2.1e-2 },
    (1000,  50,  400) : {'nEvents':30000, 'sigmaBLimit' : 4.1e-3 },
#   (1000,  20,    2) : {'nEvents':29000, 'sigmaBLimit' : 0.     },
    (1000,  20,   20) : {'nEvents':27000, 'sigmaBLimit' : 1.0    },
    (1000,  20,  200) : {'nEvents':30000, 'sigmaBLimit' : 1.5e-1 },
#   ( 400, 150,   40) : {'nEvents':30000, 'sigmaBLimit' : 0.     },
    ( 400, 150,  400) : {'nEvents':30000, 'sigmaBLimit' : 2.7e-3 },
    ( 400, 150, 4000) : {'nEvents':30000, 'sigmaBLimit' : 4.4e-3 },
#   ( 400,  50,    8) : {'nEvents':30000, 'sigmaBLimit' : 0.     },
    ( 400,  50,   80) : {'nEvents':28000, 'sigmaBLimit' : 1.0e-2 },
    ( 400,  50,  800) : {'nEvents':30000, 'sigmaBLimit' : 2.7e-3 },
#   ( 400,  20,    4) : {'nEvents':30000, 'sigmaBLimit' : 0.     },
    ( 400,  20,   40) : {'nEvents':30000, 'sigmaBLimit' : 4.8e-2 },
    ( 400,  20,  400) : {'nEvents':30000, 'sigmaBLimit' : 9.6e-3 },
#   ( 200,  50,   20) : {'nEvents':25000, 'sigmaBLimit' : 0.     },
    ( 200,  50,  200) : {'nEvents':30000, 'sigmaBLimit' : 8.8e-3 },
    ( 200,  50, 2000) : {'nEvents':30000, 'sigmaBLimit' : 9.7e-3 },
#   ( 200,  20,    7) : {'nEvents':30000, 'sigmaBLimit' : 0.     },
    ( 200,  20,   70) : {'nEvents':29000, 'sigmaBLimit' : 4.3e-2 },
    ( 200,  20,  700) : {'nEvents':30000, 'sigmaBLimit' : 9.2e-3 },
#   ( 125,  50,   50) : {'nEvents':30000, 'sigmaBLimit' : 0.     },
    ( 125,  50,  500) : {'nEvents':30000, 'sigmaBLimit' : 2.7e-2 },
    ( 125,  50, 5000) : {'nEvents':30000, 'sigmaBLimit' : 6.8e-2 },
#   ( 125,  20,   13) : {'nEvents':30000, 'sigmaBLimit' : 0.     },
    ( 125,  20,  130) : {'nEvents':30000, 'sigmaBLimit' : 4.8e-2 },
    ( 125,  20, 1300) : {'nEvents':30000, 'sigmaBLimit' : 4.3e-2 },
}

def ScaleFactor(sp):
    return SignalInfo[sp]['sigmaBLimit'] / SignalInfo[sp]['nEvents'] * HG.INTEGRATED_LUMINOSITY_2016

CONFIG = {
        'vtxChi2' : {'forward':True , 'pretty':'dimuon vtx chi^{2}'            , 'VALS': (50, 20, 10, 5, 1)       },
        'LxySig'  : {'forward':False, 'pretty':'dimuon L_{xy}/#sigma_{L_{xy}}' , 'VALS': (3, 5, 6, 10, 15, 20, 25)},
        'trkChi2' : {'forward':True , 'pretty':'muon trk chi^{2}/dof'          , 'VALS': (10, 4, 3, 2, 1)         },
        'd0Sig'   : {'forward':False, 'pretty':'muon d_{0}/#sigma_{d_{0}}'     , 'VALS': (0, 1, 2, 5, 10)         },
}

KEYS = CONFIG.keys()

def others(key):
    return [k for k in KEYS if k != key]

if FIGURE_OF_MERIT == 'ZBi':
    def FOM(nOn, nOff):
        return AT.ZBi(nOn, nOff, 1.)
    FOMLeg = 'Z_{Bi}'
elif FIGURE_OF_MERIT == 'ZPL':
    def FOM(nOn, nOff):
        return AT.ZPL(nOn, nOff, 1.)
    FOMLeg = 'Z_{PL}'

DATA = {}

def fillData(fs, sp, quantity, hkey):
    # get histograms
    s = HG.getHistogram(FILES['Signal'], (fs, sp), hkey)
    DHists, DPConfig = HG.getDataHistograms(FILES['Data'], hkey, addFlows=False)
    b = DHists[hkey]['data']

    if SignalInfo[sp]['sigmaBLimit'] == 0.: return

    n = s.Integral(0, s.GetNbinsX()+1)
    s.Scale(ScaleFactor(sp))

    # get cumulatives
    sCum = s.GetCumulative(CONFIG[quantity]['forward'])
    bCum = b.GetCumulative(CONFIG[quantity]['forward'])

    # fill f.o.m. histogram, and keep track of max f.o.m. and cut value
    nBins = sCum.GetNbinsX()
    xAxis = sCum.GetXaxis()
    data = []

    fom_max = 0.
    opt_cut = 0.
    s_opt = 0.
    b_opt = 0.

    for ibin in range(1,nBins+1):
        S = sCum.GetBinContent(ibin)
        B = bCum.GetBinContent(ibin)
        if not CONFIG[quantity]['forward']:
            S += s.GetBinContent(nBins+1)
            B += b.GetBinContent(nBins+1)
        ZBiVal = AT.ZBi(S+B, B, 1.)
        ZPLVal = AT.ZPL(S+B, B, 1.)
        cutVal = xAxis.GetBinUpEdge(ibin) if CONFIG[quantity]['forward'] else xAxis.GetBinLowEdge(ibin)
        for gridPoint in CONFIG[quantity]['VALS']:
            if abs(cutVal-gridPoint) < .01:
                data.append({'cut':cutVal, 'ZBi':ZBiVal, 'ZPL':ZPLVal, 's':S, 'b':B})
                break

    DATA[hkey] = data

for fs in ('2Mu2J',):
    for sp in SignalInfo:
    #for sp in SIGNALPOINTS:
    #for sp in ((125, 20, 130),):
    #for sp in ((1000, 20, 200),):
    #for sp in ((1000, 150, 1000),):
        print '***** HTo2XTo2Mu2J', sp[0], sp[1], sp[2], '*****'
        #for quantity in CONFIG:
        for quantity in ('LxySig',):
            keys = others(quantity)
            for vals in itertools.product(*[CONFIG[k]['VALS'] for k in keys]):
                fstring = '{}_'
                fstring += '_'.join(['{}-{}'] * len(keys))
                hkey = fstring.format(quantity, *[item for keyvalpair in zip(keys, vals) for item in keyvalpair])
                fillData(fs, sp, quantity, hkey)
                for dic in DATA[hkey]:
                    prestring = '{:7s} {:2.0f} ::: ' + ' ::: '.join(['{:7s} {:2d}'] * len(keys))
                    prestring = prestring.format(quantity, dic['cut'], *[item for keyvalpair in zip(keys, vals) for item in keyvalpair])
                    print prestring + ' ::: {:8.3f} {:4.0f} {:7.4f} {:7.4f}'.format(
                            dic['s'], dic['b'], dic['ZBi'], dic['ZPL']
                    )
                print ''
            print ''
        print ''
