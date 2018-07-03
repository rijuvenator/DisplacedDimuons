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

for NAME in (
    # Background MC
    'DY100to200'                   ,
    'DY10to50'                     ,
    'DY50toInf'                    ,
    'tW'                           ,
    'tbarW'                        ,
    'ttbar'                        ,
    'WW'                           ,
    'WJets'                        ,
    'WZ'                           ,
    'WZ-ext'                       ,
    'ZZ'                           ,
    'ZZ-ext'                       ,
    # Data
    'DoubleMuonRun2016B-07Aug17-v2',
    'DoubleMuonRun2016C-07Aug17'   ,
    'DoubleMuonRun2016D-07Aug17'   ,
    'DoubleMuonRun2016E-07Aug17'   ,
    'DoubleMuonRun2016F-07Aug17'   ,
    'DoubleMuonRun2016G-07Aug17'   ,
    'DoubleMuonRun2016H-07Aug17'   ,
    ):
    FNAME = F_NTUPLE.format(NAME)
    output += '{NAME} {FNAME}\n'.format(**locals())

open('NTuples.dat', 'w').write(output)
