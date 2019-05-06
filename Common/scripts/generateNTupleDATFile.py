import DisplacedDimuons.Common.Constants as Constants
import DisplacedDimuons.Common.Utilities as Utilities
import os

##### Place the output of this script, "NTuples.dat", in ../dat
##### It is required by the DataHandler library for setting nTuple info
##### and therefore by Analysis

# At the moment, Constants.DIR_EOS is /eos/cms/store/user/adasgupt/DisplacedDimuons/
# except if the username is stempl, in which case it gets set to something else
# Keep that in mind if running this script

F_NTUPLE = os.path.join(Constants.DIR_EOS, 'NTuples/ntuple_{}.root')

output = ''

# Signal samples
for SP in Constants.SIGNALPOINTS:
    for FS in ('4Mu', '2Mu2J'):
        NAME = 'HTo2XTo{FS}_{SPSTR}'.format(FS=FS, SPSTR=Utilities.SPStr(SP))
        FNAME = F_NTUPLE.format(NAME)
        output += '{NAME} {FNAME}\n'.format(**locals())

# # Signal samples (re-HLT)
# for SP in Constants.REHLT_SIGNALPOINTS:
#     for FS in ('2Mu2J',):
#         for HLTfilter in ('CosmicSeed', 'ppSeed'):
#             NAME = 'HTo2XTo{FS}_reHLT_{HLTFILTER}_{SPSTR}'.format(
#                     FS=FS, SPSTR=Utilities.SPStr(SP), HLTFILTER=HLTfilter)
#             FNAME = F_NTUPLE.format(NAME)
#             output += '{NAME} {FNAME}\n'.format(**locals())

for NAME in (
    # Background MC
    'DY10to50'                     ,
    'DY50toInf'                    ,
    'tW'                           ,
    'tbarW'                        ,
    'ttbar'                        ,
    'WW'                           ,
    'WJets'                        ,
    'WZ'                           ,
#   'WZ-ext'                       ,
    'ZZ'                           ,
#   'ZZ-ext'                       ,
    'QCD20toInf-ME'                ,
    'QCD30to50'                    ,
    'QCD50to80'                    ,
    'QCD80to120'                   ,
    # Data
    'DoubleMuonRun2016B-07Aug17-v2',
    'DoubleMuonRun2016C-07Aug17'   ,
    'DoubleMuonRun2016D-07Aug17'   ,
    'DoubleMuonRun2016E-07Aug17'   ,
    'DoubleMuonRun2016F-07Aug17'   ,
    'DoubleMuonRun2016G-07Aug17'   ,
    'DoubleMuonRun2016H-07Aug17'   ,
    # # Cosmics data
    # 'CosmicsRun2016D_reAOD-HLT_UGMT-base-bottomOnly_HLT-CosmicSeed',
    # 'CosmicsRun2016E_reAOD-HLT_UGMT-base-bottomOnly_HLT-CosmicSeed',
    # 'CosmicsRun2016D_reAOD-HLT_UGMT-base-bottomOnly_HLT-ppSeed'    ,
    # 'CosmicsRun2016E_reAOD-HLT_UGMT-base-bottomOnly_HLT-ppSeed'    ,
    # 'CosmicsRun2016D_reAOD-HLT_UGMT-base_HLT-CosmicSeed'           ,
    # 'CosmicsRun2016E_reAOD-HLT_UGMT-base_HLT-CosmicSeed'           ,
    # 'CosmicsRun2016D_reAOD-HLT_UGMT-base_HLT-ppSeed'               ,
    # 'CosmicsRun2016E_reAOD-HLT_UGMT-base_HLT-ppSeed'               ,
    # 'CosmicsRun2016D_reAOD-HLT_UGMT-bottomOnly_HLT-CosmicSeed'     ,
    # 'CosmicsRun2016E_reAOD-HLT_UGMT-bottomOnly_HLT-CosmicSeed'     ,
    # 'CosmicsRun2016D_reAOD-HLT_UGMT-bottomOnly_HLT-ppSeed'         ,
    # 'CosmicsRun2016E_reAOD-HLT_UGMT-bottomOnly_HLT-ppSeed'         ,
    # # NoBPTX data
    # 'NoBPTXRun2016D-07Aug17'                                       ,
    # 'NoBPTXRun2016E-07Aug17'                                       ,
    # 'NoBPTXRun2016D-07Aug17_reAOD-HLT_cosmic-seeded-path'          ,
    # 'NoBPTXRun2016D-07Aug17_reAOD-HLT_pp-seeded-path'              ,
    ):
    FNAME = F_NTUPLE.format(NAME)
    output += '{NAME} {FNAME}\n'.format(**locals())

open('NTuples.dat', 'w').write(output)
