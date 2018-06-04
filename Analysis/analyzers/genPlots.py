import math
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
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
        HErr = (0.05 if mH != 1000 else 0.30) * 3/2.
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
            'massX'      : [['X Mass [GeV]'     , 100, mX*(1-XErr), mX*(1+XErr)]                                  ],
            'cTau'       : [['c#tau [mm]'       , 100, 0.         , cTau*6.    ]                                  ],
            'pTH'        : [['Higgs p_{T} [GeV]', 100, 0.         , HPtUpper   ]                                  ],
            'pTX'        : [['X p_{T} [GeV]'    , 100, 0.         , XPtUpper   ]                                  ],
            'pTmu'       : [['#mu p_{T} [GeV]'  , 100, 0.         , MuPtUpper  ]                                  ],
            'beta'       : [['#beta = v/c'      , 100, 0.         , 1.         ]                                  ],
            'etaMu'      : [['#mu #eta'         , 100, -5.        , 5          ]                                  ],
            'dPhi'       : [['#mu #Delta#phi'   , 100, -math.pi   , math.pi    ]                                  ],
            'cosAlpha'   : [['cos(#alpha)'      , 100, -1.        , 1.         ]                                  ],
            'Lxy'        : [['L_{xy} [mm]'      , 100, 0.         , LxyUpper   ]                                  ],
            'd0'         : [['d_{0} [mm]'       , 100, 0.         , cTau*2.    ]                                  ],
            'd00'        : [['#Deltad_{0} [cm]' , 100, -.1        , .1         ]                                  ],
            'dR'         : [['#DeltaR'          , 100, 0.         , 4.5        ]                                  ],
            'LxyVSLz'    : [['L_{z} [mm]'       , 350, 0.         , 1000.      ], ['L_{xy} [mm]'   , 200, 0., 50.]],
            'd00VSpTrel' : [['#Deltad_{0} [cm]' , 100, -.1        , .1         ], ['p_{T}rel [GeV]', 100, 0., 50.]],
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
def fillPlots(fs, sp, HList):
    # get file and tree
    f = R.TFile.Open('root://eoscms.cern.ch/'+DIR_EOS_RIJU + 'NTuples/genOnly_ntuple_{}_{}.root'.format('HTo2XTo'+fs, SPStr(sp)))
    t = f.Get('SimpleNTupler/DDTree')

    # set basic particle aliases
    RT.setGenAliases(t)

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

#### ALL GLOBAL VARIABLES DECLARED HERE ####
# empty histogram dictionary
HISTS = {}
# empty files dictionary
FILES = {}


# list of histogram keys to actually fill this time
#HList = (
#   'massH',
#   'massX',
#   'cTau',
#   'pTH',
#   'pTX',
#   'pTmu',
#   'beta',
#   'etaMu',
#   'dPhi',
#   'cosAlpha',
#   'Lxy',
#   'd0',
#   'd00',
#   'dR',
#   'LxyVSLz',
#   'd00VSpTrel'
#)
# with a single argument parallelize with : parallel python genPlots.py ::: massH massX cTau pTH pTX pTmu beta etaMu dPhi cosAlpha Lxy d0 d00 dR LxyVSLz d00VSpTrel
import sys
HList = (sys.argv[-1],)

# TTree aliases: alias : expr
HAliases = {
    'cTau1'    : 'X1.mass/sqrt(pow(X1.energy,2)-pow(X1.mass,2))*sqrt(pow(mu11.x-X1.x,2) + pow(mu11.y-X1.y,2) + pow(mu11.z-X1.z,2))*10.',
    'cTau2'    : 'X2.mass/sqrt(pow(X2.energy,2)-pow(X2.mass,2))*sqrt(pow(mu21.x-X2.x,2) + pow(mu21.y-X2.y,2) + pow(mu21.z-X2.z,2))*10.',
    'beta1'    : 'sqrt(pow(X1.energy,2)-pow(X1.mass,2))/X1.energy',
    'beta2'    : 'sqrt(pow(X2.energy,2)-pow(X2.mass,2))/X2.energy',
    'dPhi1'    : 'TVector2::Phi_mpi_pi(mu11.phi-mu12.phi)',
    'dPhi2'    : 'TVector2::Phi_mpi_pi(mu21.phi-mu22.phi)',
    'Lxy1'     : 'sqrt(pow(mu11.x-X1.x,2) + pow(mu11.y-X1.y,2))*10.',
    'Lxy2'     : 'sqrt(pow(mu21.x-X2.x,2) + pow(mu21.y-X2.y,2))*10.',
    'Lz1'      : 'abs(mu11.z-X1.z)',
    'Lz2'      : 'abs(mu21.z-X2.z)',
    'd011'     : '(mu11.d0)*10.',
    'd012'     : '(mu12.d0)*10.',
    'd021'     : '(mu21.d0)*10.',
    'd022'     : '(mu22.d0)*10.',
    'd0011'    : 'TMath::Abs(mu11.x*mu11.pt*TMath::Sin(mu11.phi)-mu11.y*mu11.pt*TMath::Cos(mu11.phi))/mu11.pt-mu11.d0',
    'd0012'    : 'TMath::Abs(mu12.x*mu12.pt*TMath::Sin(mu12.phi)-mu12.y*mu12.pt*TMath::Cos(mu12.phi))/mu12.pt-mu12.d0',
    'd0021'    : 'TMath::Abs(mu21.x*mu21.pt*TMath::Sin(mu21.phi)-mu21.y*mu21.pt*TMath::Cos(mu21.phi))/mu21.pt-mu21.d0',
    'd0022'    : 'TMath::Abs(mu22.x*mu22.pt*TMath::Sin(mu22.phi)-mu22.y*mu22.pt*TMath::Cos(mu22.phi))/mu22.pt-mu22.d0',
    'dR1'      : 'sqrt(pow(mu11.eta-mu12.eta,2) + pow(TVector2::Phi_mpi_pi(mu11.phi-mu12.phi),2))',
    'dR2'      : 'sqrt(pow(mu21.eta-mu22.eta,2) + pow(TVector2::Phi_mpi_pi(mu21.phi-mu22.phi),2))',
    'pTrel11'  : 'sqrt(pow(mu11.pt*TMath::Sin(mu11.phi) - X1.pt*TMath::Sin(X1.phi),2) + pow(mu11.pt*TMath::Cos(mu11.phi) - X1.pt*TMath::Cos(X1.phi),2))',
    'pTrel12'  : 'sqrt(pow(mu12.pt*TMath::Sin(mu12.phi) - X1.pt*TMath::Sin(X1.phi),2) + pow(mu12.pt*TMath::Cos(mu12.phi) - X1.pt*TMath::Cos(X1.phi),2))',
    'pTrel21'  : 'sqrt(pow(mu21.pt*TMath::Sin(mu21.phi) - X2.pt*TMath::Sin(X2.phi),2) + pow(mu21.pt*TMath::Cos(mu21.phi) - X2.pt*TMath::Cos(X2.phi),2))',
    'pTrel22'  : 'sqrt(pow(mu22.pt*TMath::Sin(mu22.phi) - X2.pt*TMath::Sin(X2.phi),2) + pow(mu22.pt*TMath::Cos(mu22.phi) - X2.pt*TMath::Cos(X2.phi),2))',
}

# TTree draw configuration: histogram name : (list of Draw expressions)
HExpressions = {
    'massH'      : ('H.mass',),
    'massX'      : ('X1.mass', 'X2.mass'),
    'cTau'       : ('cTau1', 'cTau2'),
    'pTH'        : ('H.pt',),
    'pTX'        : ('X1.pt', 'X2.pt'),
    'pTmu'       : ('mu11.pt', 'mu12.pt', 'mu21.pt', 'mu22.pt'),
    'beta'       : ('beta1', 'beta2'),
    'etaMu'      : ('mu11.eta', 'mu12.eta', 'mu21.eta', 'mu22.eta'),
    'dPhi'       : ('dPhi1', 'dPhi2'),
    'cosAlpha'   : ('mu11.cosAlpha', 'mu21.cosAlpha'),
    'Lxy'        : ('Lxy1', 'Lxy2'),
    'd0'         : ('d011', 'd012', 'd021', 'd022'),
    'd00'        : ('d0011', 'd0012', 'd0021', 'd0022'),
    'dR'         : ('dR1', 'dR2'),
    'LxyVSLz'    : ('Lz1:Lxy1','Lz2:Lxy2'),
    'd00VSpTrel' : ('pTrel11:d0011', 'pTrel12:d0012','pTrel21:d0021','pTrel22:d0022')
}

#### MAIN CODE ####
# loop over signal points
for fs in ('4Mu',):
    for sp in SIGNALPOINTS:
        HISTS[(fs, sp)] = {}
        fillPlots(fs, sp, HList)
        print 'Created plots for', fs, sp
# now that plots are filled, loop over signal points and write to files
for fs in ('4Mu',):
    for key in HList:
        FILES[key] = R.TFile.Open('roots/GenPlots_{}.root'.format(key), 'RECREATE')
        FILES[key].cd()
        for sp in SIGNALPOINTS:
            HISTS[(fs, sp)][key].Write()
        print 'Written ROOT file for all signal points for', fs, key
