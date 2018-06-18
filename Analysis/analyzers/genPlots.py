import math
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.Analyzer as Analyzer
from DisplacedDimuons.Common.Constants import DIR_EOS_RIJU, SIGNALS, SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr

#### CLASS AND FUNCTION DEFINITIONS ####
# histogram configuration object
# declared once per signal point and calculates all the histogram properties
# add new histograms here
class HistogramConfigurations(object):
    def __init__(self, fs, sp):
        mH, mX, cTau = sp
        self.mH, self.mX, self.cTau = mH, mX, cTau
        self.fs = fs

        # these values help calculate useful bin limits
        HErr = 0.05 * 3/2.
        XErr = 0.005

        # the Lxy upper is best set by whether it's the min, mid, or max cTau
        LxyUppers = [150., 1500., 15000.]
        LxyUpper = LxyUppers[SIGNALS[mH][mX].index(cTau)]

        # all the H PT seem to fit in 0-250
        HPtUpper = 250.

        # this seems to be a nice upper limit for X PT
        XPtUpper = (mH-mX)*1.4

        # muon pT seems to depend only on Higgs mass
        MuPtUpper = mH/2.

        # actual init code. saves constructor argument for each histogram type

        # this is just a temporary dictionary storing the configuration parameters
        # the dictionary is of format key : ((axisTuple1), (axisTuple2))
        # and axisTuples are of format (title, nBins, binLow, binHigh)
        # makeAttrDict knows what to do with this exact format
        attributes = {
            'massH'      : [['Higgs Mass [GeV]' , 100, mH*(1-HErr), mH*(1+HErr)]                                  ],
            'pTH'        : [['Higgs p_{T} [GeV]', 100, 0.         , HPtUpper   ]                                  ],
            'cTau'       : [['c#tau [mm]'       , 100, 0.         , cTau*6.    ]                                  ],
            'beta'       : [['#beta = v/c'      , 100, 0.         , 1.         ]                                  ],
            'Lxy'        : [['L_{xy} [mm]'      , 100, 0.         , LxyUpper   ]                                  ],
            'dR'         : [['#DeltaR'          , 100, 0.         , 4.5        ]                                  ],
            'dPhiMuMu'   : [['#mu#mu #Delta#phi', 100, -math.pi   , math.pi    ]                                  ],
            'dPhiMuX'    : [['#muX #Delta#phi'  , 100, -math.pi   , math.pi    ]                                  ],
            'massX'      : [['X Mass [GeV]'     , 100, mX*(1-XErr), mX*(1+XErr)]                                  ],
            'pTX'        : [['X p_{T} [GeV]'    , 100, 0.         , XPtUpper   ]                                  ],
            'cosAlpha'   : [['cos(#alpha)'      , 100, -1.        , 1.         ]                                  ],
            'd0'         : [['d_{0} [mm]'       , 100, 0.         , cTau*2.    ]                                  ],
            'pTmu'       : [['#mu p_{T} [GeV]'  , 100, 0.         , MuPtUpper  ]                                  ],
            'etaMu'      : [['#mu #eta'         , 100, -5.        , 5          ]                                  ],
            'LxyVSLz'    : [['L_{z} [mm]'       , 350, 0.         , 1000.      ], ['L_{xy} [mm]'   , 200, 0., 50.]],
        }

        self.data = {}
        for key,config in attributes.iteritems():
            self.data[key] = self.makeAttrDict(key, config)

    # returns KEY_HTo2XTo(FS)_(mH)_(mX)_(cTau)
    def HName(self, key):
        return key + '_HTo2XTo' + self.fs + '_' + SPStr(self.mH, self.mX, self.cTau)

    # returns a dictionary of histogram attributes: name, title, nAxes, and axis dictionaries
    # each of which have a title, nBins, binLow, and binHigh key
    def makeAttrDict(self, key, config):
        attrDict = {'name':self.HName(key), 'nAxes':len(config)}
        axisHeaders = ('title', 'nBins', 'binLow', 'binHigh')
        titleString = ''
        for axisNumber, axisTuple in enumerate(config):
            attrDict['axis'+str(axisNumber+1)] = dict(zip(axisHeaders, axisTuple))
            titleString += ';{}'
        titleString += ';Counts'
        attrDict['title'] = titleString.format(*(attrDict['axis'+str(axisNumber+1)]['title'] for axisNumber in range(len(config))))
        return attrDict
    
    # this allows for example R.TH1F(*HConfig[key])
    def __getitem__(self, key):
        AD = self.data[key]
        histArgs = [AD['name'], AD['title']]
        for axisNumber in range(AD['nAxes']):
            histArgs.append(AD['axis'+str(axisNumber+1)]['nBins'  ])
            histArgs.append(AD['axis'+str(axisNumber+1)]['binLow' ])
            histArgs.append(AD['axis'+str(axisNumber+1)]['binHigh'])
        return histArgs

# wrapper for TTree::Draw
def Draw(t, HConfig, key, expressions):
    for i, expr in enumerate(expressions):
        t.Draw('{expr}>>{isFirst}{hName}'.format(expr=expr, isFirst='' if i==0 else '+', hName=HConfig.HName(key)))

# opens file, gets tree, sets aliases, declares histograms, fills histograms, closes file
def fillPlots(fs, sp, HList, FNAME):
    # get file and tree
    #f = R.TFile.Open('root://eoscms.cern.ch/'+DIR_EOS_RIJU + 'NTuples/genOnly_ntuple_{}_{}.root'.format('HTo2XTo'+fs, SPStr(sp)))
    f = R.TFile.Open(FNAME.format('HTo2XTo'+fs+'_'+SPStr(sp)))
    t = f.Get('SimpleNTupler/DDTree')

    # set basic particle aliases
    RT.setGenAliases(t, fs)

    # set additional aliases from HAliases
    for alias, expr in HAliases.iteritems():
        t.SetAlias(alias, expr)

    # define histogram configurations for this signal point
    HConfig = HistogramConfigurations(fs, sp)

    # declare histograms
    # make sure histograms don't get deleted when file is closed
    # fill histograms using TTree::Draw
    for key in HList:
        if key not in HConfig.data:
            raise Exception('At least one histogram key: '+key+' not known')
        nAxes = str(HConfig.data[key]['nAxes'])
        HISTS[(fs, sp)][key] = getattr(R, 'TH'+nAxes+'F')(*HConfig[key])
        Draw(t, HConfig, key, HExpressions[key])
        HISTS[(fs, sp)][key].SetDirectory(0)

    # cleanup
    del t
    f.Close()
    del f

# this generalizes the old HAliases and HExpressions dictionaries
# to accomodate two different final state configurations, with different aliases and expressions
# for 4Mu,   we have X1, X2, mu11, mu12, mu21, mu22
# for 2Mu2J, we have X     , mu1 , mu2
def makeAliasesAndExpressions(fs):
    # used to build TTree aliases below
    tformulae = {
        # one per X, uses mu1 info only
        'cTau'    : '10.*{X}.mass/sqrt(pow({X}.energy,2)-pow({X}.mass,2))*sqrt(pow({MU1}.x-{X}.x,2) + pow({MU1}.y-{X}.y,2) + pow({MU1}.z-{X}.z,2))',
        'beta'    : 'sqrt(pow({X}.energy,2)-pow({X}.mass,2))/{X}.energy',
        'Lxy'     : '10.*sqrt(pow({MU1}.x-{X}.x,2) + pow({MU1}.y-{X}.y,2))',
        'Lz'      : 'abs({MU1}.z-{X}.z)',
        'dR'      : '{MU1}.deltaR',

        # one per X, uses mu1 and mu2 info
        'dPhiMuMu': 'TVector2::Phi_mpi_pi({MU1}.phi-{MU2}.phi)',
        'dPhiMuX' : 'TVector2::Phi_mpi_pi({MU}.phi-{X}.phi)',

        # one per muon
        'd0'      : '10.*({MU}.d0)',
        'pTrel'   : 'sqrt(pow({MU}.pt*TMath::Sin({MU}.phi)-{X}.pt*TMath::Sin({X}.phi),2) + pow({MU}.pt*TMath::Cos({MU}.phi)-{X}.pt*TMath::Cos({X}.phi),2))',
    }

    # basic particle aliases are set in RootTools
    # extra TTree aliases are set here, as key : alias
    # the actual alias is gotten from the formulae above
    aliases = {}
    def setAliases(X):
        # per X quantities
        # dPhi can be lumped in here because its keys are compatible
        for key in ('cTau', 'beta', 'Lxy', 'Lz', 'dR', 'dPhiMuMu'):
            aliases[key+X] = tformulae[key].format(X='X'+X, MU1='mu'+X+'1', MU2='mu'+X+'2')

        # per muon quantities
        for key in ('d0', 'pTrel', 'dPhiMuX'):
            for mu in ('1', '2'):
                aliases[key+X+mu] = tformulae[key].format(MU='mu'+X+mu, X='X'+X)

    # TTree draw expressions as histogram name : [list of Draw expressions]
    # the Draw wrapper above will draw them in order, adding a + for multiple
    expressions = {
        # fixed
        'massH'      : ['H.mass'], # H0 mass        : H.mass
        'pTH'        : ['H.pt'],   # H0 pT          : H.pT

        # per X, alias above
        'cTau'       : [],         # X cTau         : cTau
        'beta'       : [],         # X beta         : beta
        'Lxy'        : [],         # X Lxy          : Lxy
        'dR'         : [],         # X deltaR       : dR
        'dPhiMuMu'   : [],         # X deltaPhiMuMu : dPhiMuMu
        'dPhiMuX'    : [],         # X deltaPhiMuX  : dPhiMuX

        # per X, alias in RT
        'massX'      : [],         # X mass         : X.mass
        'pTX'        : [],         # X pT           : X.pT
        'cosAlpha'   : [],         # X cosAlpha     : mu.cosAlpha

        # per muon, alias above
        'd0'         : [],         # mu d0          : d0

        # per muon, alias in RT
        'pTmu'       : [],         # mu pT          : mu.pt
        'etaMu'      : [],         # mu eta         : mu.eta

        # 2D plots, handle specially
        'LxyVSLz'    : [],         # Lxy vs Lz      : Lz:Lxy
    }
    def setExpressions(X):
        # per X quantities with aliases
        for key in ('cTau', 'beta', 'Lxy', 'dR', 'dPhiMuX'):
            expressions[key].append(key+X)

        # per muon quantities with aliases
        for key in ('d0','dPhiMuMu'):
            for mu in ('1', '2'):
                expressions[key].append(key+X+mu)

        # per X quantities without aliases
        for key, string in (('massX', '{X}.mass'), ('pTX', '{X}.pt'), ('cosAlpha', '{MU1}.cosAlpha')):
            expressions[key].append(string.format(X='X'+X, MU1='mu'+X+'1'))

        # per muon quantities without aliases
        for key, string in (('pTmu', '{MU}.pt'), ('etaMu', '{MU}.eta')):
            for mu in ('1', '2'):
                expressions[key].append(string.format(MU='mu'+X+mu))

        # 2D plots
        for key, string in (('LxyVSLz', 'Lz{X}:Lxy{X}'),):
            expressions[key].append(string.format(X=X))

    # fill the aliases and expressions dictionaries
    XLists = {'4Mu' : ('1', '2'), '2Mu2J' : ('',)}
    for X in XLists[fs]:
        setAliases(X)
        setExpressions(X)

    return aliases, expressions

#### ALL GLOBAL VARIABLES DECLARED HERE ####
# empty histogram dictionary
HISTS = {}

# empty files dictionary
FILES = {}

# list of histogram keys, copied from the inside of HistogramConfigurations
HList = (
   'massH'     ,
   'pTH'       ,
   'cTau'      ,
   'beta'      ,
   'Lxy'       ,
   'dR'        ,
   'dPhi'      ,
   'massX'     ,
   'pTX'       ,
   'cosAlpha'  ,
   'd0'        ,
   'pTmu'      ,
   'etaMu'     ,
   'LxyVSLz'   ,
)

#### MAIN CODE ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setFNAME(ARGS)
    if not ARGS.NAME.startswith('HTo2X'):
        raise Exception('[ANALYZER ERROR]: This script runs on signal only.')
    fs = ARGS.NAME.replace('HTo2XTo', '')
    sp = tuple(ARGS.SIGNALPOINT)
    HAliases, HExpressions = makeAliasesAndExpressions(fs)

    HISTS[(fs, sp)] = {}
    fillPlots(fs, sp, HList, ARGS.FNAME)
    print 'Created all plots for', fs, sp

    FileName = 'roots/GenPlots_HTo2XTo{FS}_{SP}.root'.format(FS=fs, SP=SPStr(sp)) if not ARGS.TEST else 'test.root'
    FILES[(fs, sp)] = R.TFile.Open(FileName, 'RECREATE')
    FILES[(fs, sp)].cd()
    for key in HList:
        HISTS[(fs, sp)][key].Write()
    print 'Written ROOT file for all plots for', fs, sp
