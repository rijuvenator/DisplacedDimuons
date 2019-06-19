import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuons.Analysis.AnalysisTools as AT
import DisplacedDimuons.Analysis.HistogramGetter as HG
import re, itertools
from OptimizerTools import SignalInfo, ScaleFactor, calculateFOM, PARSER

ARGS = PARSER.parse_args()
FIGURE_OF_MERIT = ARGS.FOM

R.gStyle.SetPadTickY(0)

FILES = {
    'Signal' : R.TFile.Open('roots/HaikuPlots_Trig_HTo2XTo2Mu2J.root'),
    'Data'   : R.TFile.Open('roots/HaikuPlots_IDPHI_DATA.root'),
}

CONFIG = {
        'vtxChi2' : {'forward':True , 'pretty':'dimuon vtx chi^{2}'            , 'VALS': (50, 20, 10, 5, 1)       },
        'LxySig'  : {'forward':False, 'pretty':'dimuon L_{xy}/#sigma_{L_{xy}}' , 'VALS': (3, 5, 6, 10, 15, 20, 25)},
        'trkChi2' : {'forward':True , 'pretty':'muon trk chi^{2}/dof'          , 'VALS': (10, 4, 3, 2, 1)         },
        'd0Sig'   : {'forward':False, 'pretty':'muon d_{0}/#sigma_{d_{0}}'     , 'VALS': (0, 1, 2, 5, 10)         },
}

KEYS = CONFIG.keys()

def others(key):
    return [k for k in KEYS if k != key]

DATA = {}

def fillData(fs, sp, quantity, hkey):
    # get histograms
    s = HG.getHistogram(FILES['Signal'], (fs, sp), hkey)
    DHists, DPConfig = HG.getDataHistograms(FILES['Data'], hkey, addFlows=False)
    b = DHists[hkey]['data']

    if SignalInfo[sp]['sigmaBLimit'] == 0.: return

    s.Scale(ScaleFactor(sp))

    # get cumulatives
    sCum = s.GetCumulative(CONFIG[quantity]['forward'])
    bCum = b.GetCumulative(CONFIG[quantity]['forward'])

    # fill f.o.m. histogram, and keep track of max f.o.m. and cut value
    nBins = sCum.GetNbinsX()
    xAxis = sCum.GetXaxis()
    data = []

    for ibin in range(1,nBins+1):
        S, B, cutVal, FOMs = calculateFOM(s, b, sCum, bCum, nBins, ibin, xAxis, CONFIG[quantity]['forward'])
        for gridPoint in CONFIG[quantity]['VALS']:
            if abs(cutVal-gridPoint) < .01:
                data.append({'cut':cutVal, 'ZBi':FOMs['ZBi'], 'ZPL':FOMs['ZPL'], 's':S, 'b':B})
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
