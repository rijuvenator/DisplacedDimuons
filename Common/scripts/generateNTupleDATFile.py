import DisplacedDimuons.Common.Constants as Constants
import DisplacedDimuons.Common.Utilities as Utilities
import os

##### Place the output of this script, "NTuples.dat", in ../dat
##### It is required by the DataHandler library for setting nTuple info
##### and therefore by Analysis

def parseNTuplePath(user, tupleName):
    path = Constants.NTUPLES_ROOTDIR[user]
    ntuple = 'ntuple_{}.root'.format(tupleName)
    return os.path.join(path, ntuple)
    
output = ''

# Signal samples
for SP in Constants.SIGNALPOINTS:
    for FS in ('4Mu', '2Mu2J'):
        NAME = 'HTo2XTo{FS}_{SPSTR}'.format(FS=FS, SPSTR=Utilities.SPStr(SP))
        FNAME = parseNTuplePath('valuev', NAME)
        # FNAME = F_NTUPLE.format(NAME)
        output += '{NAME} {FNAME}\n'.format(**locals())

# Signal samples (re-HLT)
for SP in Constants.REHLT_SIGNALPOINTS:
    for FS in ('2Mu2J',):
        for SEEDING in ('CosmicSeed', 'ppSeed'):
            NAME = 'reHLT_HTo2XTo{FS}_{SEEDING}_{SPSTR}'.format(
                    FS=FS, SPSTR=Utilities.SPStr(SP), SEEDING=SEEDING)
            FNAME = parseNTuplePath('stempl', NAME)
            # FNAME = F_NTUPLE.format(NAME)
            output += '{NAME} {FNAME}\n'.format(**locals())

for NAME, USER in (
    # Background MC
    ('DY10to50'                     , 'valuev'),
    ('DY50toInf'                    , 'valuev'),
    ('tW'                           , 'valuev'),
    ('tbarW'                        , 'valuev'),
    ('ttbar'                        , 'valuev'),
    ('WW'                           , 'valuev'),
    ('WJets'                        , 'valuev'),
    ('WZ'                           , 'valuev'),
#   ('WZ-ext'                       , 'valuev'),
    ('ZZ'                           , 'valuev'),
#   ('ZZ-ext'                       , 'valuev'),
    ('QCD20toInf-ME'                , 'valuev'),
    ('QCD30to50'                    , 'valuev'),
    ('QCD50to80'                    , 'valuev'),
    ('QCD80to120'                   , 'valuev'),
    # Data
    ('DoubleMuonRun2016B-07Aug17-v2', 'valuev'),
    ('DoubleMuonRun2016C-07Aug17'   , 'valuev'),
    ('DoubleMuonRun2016D-07Aug17'   , 'valuev'),
    ('DoubleMuonRun2016E-07Aug17'   , 'valuev'),
    ('DoubleMuonRun2016F-07Aug17'   , 'valuev'),
    ('DoubleMuonRun2016G-07Aug17'   , 'valuev'),
    ('DoubleMuonRun2016H-07Aug17'   , 'valuev'),
    # Cosmics data
    ('CosmicsRun2016D_reAOD-HLT_UGMT-base-bottomOnly_HLT-CosmicSeed'               , 'stempl'),
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base-bottomOnly_HLT-CosmicSeed'               , 'stempl'),
    ('CosmicsRun2016D_reAOD-HLT_UGMT-base-bottomOnly_HLT-ppSeed'                   , 'stempl'),
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base-bottomOnly_HLT-ppSeed'                   , 'stempl'),
    ('CosmicsRun2016D_reAOD-HLT_UGMT-base_HLT-CosmicSeed'                          , 'stempl'),
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base_HLT-CosmicSeed'                          , 'stempl'),
    ('CosmicsRun2016D_reAOD-HLT_UGMT-base_HLT-ppSeed'                              , 'stempl'),
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base_HLT-ppSeed'                              , 'stempl'),
    # ('CosmicsRun2016D_reAOD-HLT_UGMT-bottomOnly_HLT-CosmicSeed'                    , 'stempl'),
    ('CosmicsRun2016E_reAOD-HLT_UGMT-bottomOnly_HLT-CosmicSeed'                    , 'stempl'),
    # ('CosmicsRun2016D_reAOD-HLT_UGMT-bottomOnly_HLT-ppSeed'                        , 'stempl'),
    ('CosmicsRun2016E_reAOD-HLT_UGMT-bottomOnly_HLT-ppSeed'                        , 'stempl'),
    ('CosmicsRun2016D_reAOD-HLT_StoppedPtlsSubsetJSON_HLT-CosmicSeed'    , 'stempl'),
    ('CosmicsRun2016E_reAOD-HLT_StoppedPtlsSubsetJSON_HLT-CosmicSeed'    , 'stempl'),
    ('CosmicsRun2016E_reAOD-HLT_UGMT-bottomOnly_HLT-CosmicSeed-SingleMuOpen'       , 'stempl'),
    ('CosmicsRun2016E_reAOD-HLT_UGMT-bottomOnly_HLT-ppSeed-SingleMuOpen'           , 'stempl'),
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base_HLT-CosmicSeed_reHLTvalidation_run276936', 'stempl'),
    ('CosmicsRun2016E_reAOD-HLT_UGMT-base_HLT-CosmicSeed_reHLTvalidation_run276910', 'stempl'),
    # NoBPTX data
    ('NoBPTXRun2016D-07Aug17_StoppedPtlsSubsetJSON'       , 'stempl'),
    ('NoBPTXRun2016E-07Aug17_StoppedPtlsSubsetJSON'       , 'stempl'),
    ('NoBPTXRun2016D-07Aug17_reAOD-HLT_cosmic-seeded-path', 'stempl'),
    ('NoBPTXRun2016D-07Aug17_reAOD-HLT_pp-seeded-path'    , 'stempl'),
    ('NoBPTXRun2016E-07Aug17_reHLTvalidation_run276936'   , 'stempl'),
    ('NoBPTXRun2016E-07Aug17_reHLTvalidation_run276910'   , 'stempl'),
    ):
    FNAME = parseNTuplePath(USER, NAME)
    output += '{NAME} {FNAME}\n'.format(**locals())

open('NTuples.dat', 'w').write(output)
