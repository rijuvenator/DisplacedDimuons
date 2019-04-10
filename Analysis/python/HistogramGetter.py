import re
import ROOT as R
import DisplacedDimuons.Common.DataHandler as DH
from DisplacedDimuons.Common.Constants import SIGNALPOINTS

# integrated luminosity for 2016
INTEGRATED_LUMINOSITY_2016 = 35900.

######################################
#### HISTOGRAM GETTER AND REGEXES ####
######################################

# I name my histograms with a strict naming convention
# Therefore it is very easy to parse the list of keys and split it up with a regex
# so that the list of histograms can be organized by sample
# These regexes help do exactly that

Patterns = {
    'HTo2XTo4Mu'   : re.compile(r'(.*)_HTo2XTo4Mu_(\d{3,4})_(\d{2,3})_(\d{1,4})'),
    'HTo2XTo2Mu2J' : re.compile(r'(.*)_HTo2XTo2Mu2J_(\d{3,4})_(\d{2,3})_(\d{1,4})')
}
for sample in (
    'DY10to50'     ,
    'WJets'        ,
    'WW'           ,
    'WZ'           ,
    'ZZ'           ,
    'tW'           ,
    'tbarW'        ,
    'QCD20toInf-ME',
    'DY50toInf'    ,
    'ttbar'        ,
    ):
    Patterns[sample] = re.compile(r'(.*)_'+sample)
for sample in (
    'DoubleMuonRun2016B-07Aug17-v2',
    'DoubleMuonRun2016C-07Aug17'   ,
    'DoubleMuonRun2016D-07Aug17'   ,
    'DoubleMuonRun2016E-07Aug17'   ,
    'DoubleMuonRun2016F-07Aug17'   ,
    'DoubleMuonRun2016G-07Aug17'   ,
    'DoubleMuonRun2016H-07Aug17'   ,
    'NoBPTXRun2016D_07Aug17'       ,
    'NoBPTXRun2016E_07Aug17'       ,
    'CosmicsRun2016D_reAOD_HLT_UGMT_base_bottomOnly_CosmicSeed',
    'CosmicsRun2016E_reAOD_HLT_UGMT_base_bottomOnly_CosmicSeed',
    'CosmicsRun2016D_reAOD_HLT_UGMT_base_bottomOnly_ppSeed',
    'CosmicsRun2016E_reAOD_HLT_UGMT_base_bottomOnly_ppSeed',
    'CosmicsRun2016D_reAOD_HLT_UGMT_base_CosmicSeed',
    'CosmicsRun2016E_reAOD_HLT_UGMT_base_CosmicSeed',
    'CosmicsRun2016D_reAOD_HLT_UGMT_base_ppSeed',
    'CosmicsRun2016E_reAOD_HLT_UGMT_base_ppSeed',
    'CosmicsRun2016D_reAOD_HLT_UGMT_bottomOnly_CosmicSeed',
    'CosmicsRun2016E_reAOD_HLT_UGMT_bottomOnly_CosmicSeed',
    'CosmicsRun2016D_reAOD_HLT_UGMT_bottomOnly_ppSeed',
    'CosmicsRun2016E_reAOD_HLT_UGMT_bottomOnly_ppSeed',
    ):
    Patterns[sample] = re.compile(r'(.*)_'+sample)

# Define the function that loops over the keys in a hadded histogram ROOT file
# produced by an Analyzer using the correct naming convention
# this is usually HNAME_(SAMPLE) or HNAME_HTo2XTo(FS)_(MH)_(MX)_(CTAU)
# return a dictionary whose keys are either a string SAMPLE
# or a tuple (FS, SP) where SP is the usual (MH, MX, CTAU) and FS is 4Mu or 2Mu2J
# and SetDirectory(0) so that the histograms don't disappear

# get all histograms
def getHistograms(FILE):
    f = R.TFile.Open(FILE)
    HISTS = {}
    for hkey in [tkey.GetName() for tkey in f.GetListOfKeys()]:
        if 'HTo2X' in hkey:
            if '4Mu' in hkey:
                # hkey has the form KEY_HTo2XTo4Mu_mH_mX_cTau
                matches = Patterns['HTo2XTo4Mu'].match(hkey)
                fs = '4Mu'
            elif '2Mu2J' in hkey:
                # hkey has the form KEY_HTo2XTo2Mu2J_mH_mX_cTau
                matches = Patterns['HTo2XTo2Mu2J'].match(hkey)
                fs = '2Mu2J'
            key = matches.group(1)
            sp = tuple(map(int, matches.group(2, 3, 4)))
            if (fs, sp) not in HISTS:
                HISTS[(fs, sp)] = {}
            HISTS[(fs, sp)][key] = f.Get(hkey)
            HISTS[(fs, sp)][key].SetDirectory(0)
        else:
            # hkey has the form KEY_SAMPLE
            for sample, pattern in Patterns.iteritems():
                matches = pattern.match(hkey)
                if matches:
                    key = matches.group(1)
                    if sample not in HISTS:
                        HISTS[sample] = {}
                    HISTS[sample][key] = f.Get(hkey)
                    HISTS[sample][key].SetDirectory(0)
    return HISTS

# get histograms one at a time
def getHistogram(FILE, ref, key):
    if type(ref) == tuple:
        hkey = '{}_HTo2XTo{}_{}_{}_{}'.format(key, ref[0], *ref[1])
    else:
        hkey = '{}_{}'.format(key, ref)
    return FILE.Get(hkey)

# get added signal histograms
def getAddedSignalHistograms(FILE, fs, keylist):
    HISTS = {}
    for key in keylist:
        HISTS[key] = getHistogram(FILE, (fs, SIGNALPOINTS[0]), key).Clone()
    for sp in SIGNALPOINTS[1:]:
        for key in keylist:
            HISTS[key].Add(getHistogram(FILE, (fs, sp), key))
    return HISTS

############################
#### PLOT CONFIGURATION ####
############################

# Here stores sample specific information for configuring plots:
# name, legend name, color, and sample weight
# The sample weight is obtained from the DataHandler dataset classes
# using the cross section, kFactor, nEvents, and negFrac
# The script that generates the background data file adds any _ext samples
# to their main sample, because the tuples are hadded together

SAMPLES = DH.getAllSamples()
PLOTCONFIG = {}
PlotData = (
    ('HTo2XTo4Mu'                   , 'H#rightarrow2X#rightarrow4#mu'  , R.kBlue),
    ('HTo2XTo2Mu2J'                 , 'H#rightarrow2X#rightarrow2#mu2j', R.kBlue),
    ('DY10to50'                     , 'Drell-Yan M(10, 50)'            , 210    ),
    ('DY50toInf'                    , 'Drell-Yan M(50, #infty)'        , 209    ),
    ('WJets'                        , 'W+Jets'                         , 52     ),
    ('WW'                           , 'WW'                             , 208    ),
    ('WZ'                           , 'WZ'                             , 98     ),
    ('ZZ'                           , 'ZZ'                             , 94     ),
    ('tW'                           , 'tW'                             , 66     ),
    ('tbarW'                        , '#bar{t}W'                       , 63     ),
    ('ttbar'                        , 't#bar{t}'                       , 4      ),
    ('QCD20toInf-ME'                , 'QCD p_{T}(20, #infty)'          , R.kOrange),
    ('DoubleMuonRun2016B-07Aug17-v2', 'DoubleMuon2016B'                , 1      ),
    ('DoubleMuonRun2016C-07Aug17'   , 'DoubleMuon2016C'                , 1      ),
    ('DoubleMuonRun2016D-07Aug17'   , 'DoubleMuon2016D'                , 1      ),
    ('DoubleMuonRun2016E-07Aug17'   , 'DoubleMuon2016E'                , 1      ),
    ('DoubleMuonRun2016F-07Aug17'   , 'DoubleMuon2016F'                , 1      ),
    ('DoubleMuonRun2016G-07Aug17'   , 'DoubleMuon2016G'                , 1      ),
    ('DoubleMuonRun2016H-07Aug17'   , 'DoubleMuon2016H'                , 1      ),
)
for name, latex, color in PlotData:
    if name.startswith('HTo2X') or name.startswith('DoubleMuon'):
        sampleWeight = 1.
    else:
        s = SAMPLES[name]
        sampleWeight = (s.crossSection * s.kFactor) / (s.nEvents * (1. - 2. * s.negFrac)) * INTEGRATED_LUMINOSITY_2016
    PLOTCONFIG[name] = {'LATEX':latex, 'COLOR':color, 'WEIGHT':sampleWeight}
