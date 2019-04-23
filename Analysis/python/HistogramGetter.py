import re
import ROOT as R
import DisplacedDimuons.Common.DataHandler as DH
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS, BGORDER

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
def getAddedSignalHistograms(FILE, fs, keylist, getIndividuals=False):
    # allow passing a string or a list
    if type(keylist) == str:
        keylist = [keylist]

    # loop through the keys, add up all the signalpoints, return a dictionary of histograms
    HISTS = {}
    INDIV = {}
    for key in keylist:
        INDIV[key] = {}
        HISTS[key] = getHistogram(FILE, (fs, SIGNALPOINTS[0]), key).Clone()
        if getIndividuals:
            INDIV[key][SIGNALPOINTS[0]] = getHistogram(FILE, (fs, SIGNALPOINTS[0]), key).Clone()
    for sp in SIGNALPOINTS[1:]:
        for key in keylist:
            HISTS[key].Add(getHistogram(FILE, (fs, sp), key))
            if getIndividuals:
                INDIV[key][sp] = getHistogram(FILE, (fs, sp), key).Clone()

    if not getIndividuals:
        return HISTS
    else:
        return HISTS, INDIV

# get added weighted background histograms
# keylist is a single key (string) or a list of keys
# stack and addFlows are bools
# rebin is a single int or a list of ints (for 2D plots)
# rebinVeto is a lambda specifying which keys NOT to rebin, with the key as an input
# extraScale is an extra scaling factor (needed for comparing to 10% of data)
def getBackgroundHistograms(FILE, keylist, stack=True, addFlows=True, rebin=None, rebinVeto=None, extraScale=None):
    # allow passing a string or a list
    if type(keylist) == str:
        keylist = [keylist]

    # loop through the keys
    # if stack, make a THStack; otherwise, get started by using the first histogram
    # loop through the bg keys, addFlows if desired, scale, rebin if desired
    # if stack, Add
    # if not stack and this isn't the first, also Add
    # if not stack and this is the first, clone ("get started")
    # return dictionary of dictionary of histograms, and plot configs
    HISTS = {}
    PConfig = {}
    for key in keylist:
        HISTS[key] = {}
        PConfig[key] = {'stack':('', '', 'hist')}
        if stack:
            HISTS[key]['stack'] = R.THStack('hStack', '')
        for ref in BGORDER:
            HISTS[key][ref] = getHistogram(FILE, ref, key).Clone()
            if addFlows:
                RT.addFlows(HISTS[key][ref])
            HISTS[key][ref].Scale(PLOTCONFIG[ref]['WEIGHT'])
            if extraScale is not None:
                HISTS[key][ref].Scale(extraScale)
            if rebin is not None and (rebinVeto is None or (rebinVeto is not None and not rebinVeto(key))):
                is2D = 'TH2' in str(HISTS[key][ref].__class__)
                if is2D:
                    if not hasattr(rebin, '__iter__'):
                        print '[HISTOGRAMGETTER ERROR]: For 2D plots, "rebin" must be a list of 2 rebin values'
                        exit()
                    HISTS[key][ref].Rebin2D(*rebin)
                else:
                    HISTS[key][ref].Rebin(rebin)
            PConfig[key][ref] = (PLOTCONFIG[ref]['LATEX'], 'f', 'hist')
            if not stack and ref == BGORDER[0]:
                HISTS[key]['stack'] = HISTS[key][ref].Clone()
                continue
            HISTS[key]['stack'].Add(HISTS[key][ref])

    return HISTS, PConfig

# get added data histograms
# interface is similar to above
def getDataHistograms(FILE, keylist, addFlows=True, rebin=None, rebinVeto=None):
    # allow passing a string or a list
    if type(keylist) == str:
        keylist = [keylist]

    DataKeys = ['DoubleMuonRun2016{}-07Aug17{}'.format(era, '' if era != 'B' else '-v2') for era in ('B', 'C', 'D', 'E', 'F', 'G', 'H')]

    # loop through the keys
    # if stack, make a THStack; otherwise, get started by using the first histogram
    # loop through the bg keys, addFlows if desired, scale, rebin if desired
    # if stack, Add
    # if not stack and this isn't the first, also Add
    # if not stack and this is the first, clone ("get started")
    # return dictionary of dictionary of histograms, and plot configs
    HISTS = {}
    PConfig = {}
    for key in keylist:
        HISTS[key] = {}
        PConfig[key] = {'data':('DoubleMuon2016', 'pe', 'pe')}
        for ref in DataKeys:
            HISTS[key][ref] = getHistogram(FILE, ref, key).Clone()
            if addFlows:
                RT.addFlows(HISTS[key][ref])
            if rebin is not None and (rebinVeto is None or (rebinVeto is not None and not rebinVeto(key))):
                is2D = 'TH2' in str(HISTS[key][ref].__class__)
                if is2D:
                    if not hasattr(rebin, '__iter__'):
                        print '[HISTOGRAMGETTER ERROR]: For 2D plots, "rebin" must be a list of 2 rebin values'
                        exit()
                    HISTS[key][ref].Rebin2D(*rebin)
                else:
                    HISTS[key][ref].Rebin(rebin)
            if ref == DataKeys[0]:
                HISTS[key]['data'] = HISTS[key][ref].Clone()
                continue
            HISTS[key]['data'].Add(HISTS[key][ref])

    return HISTS, PConfig

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

# DY50toInf job #6 fails with file open error on/after pat_203.root
# This job consists of files 19 190-199 2 20 200-206 = 20 files
# Corresponding to 201,005 events that do not end up in the final ROOT file
# The full DY50toInf dataset is 122,547,040 events
# The PAT dataset is 10,259,410 events (passing the trigger)
# So an approximation for the real number of events that went into the final ROOT file is
# 122547040 * (1 - 201005/10259410)
# Recompute the weight based on this.

s = SAMPLES['DY50toInf']
PLOTCONFIG['DY50toInf']['WEIGHT'] = (s.crossSection * s.kFactor) / ( (s.nEvents * (1. - 201005./10259410.)) * (1. - 2. * s.negFrac)) * INTEGRATED_LUMINOSITY_2016
