import DisplacedDimuons.Common.Constants as Constants
import DisplacedDimuons.Common.Utilities as Utilities
import os

##### Place the output of this script, "NTuples.dat", in ../dat
##### It is required by the DataHandler library for setting nTuple info
##### and therefore by Analysis

# At the moment, Constants.DIR_EOS is /eos/cms/store/user/adasgupt/DisplacedDimuons/
# except if the username is stempl, in which case it gets set to something else
# Keep that in mind if running this script

F_NTUPLE     = os.path.join(Constants.DIR_EOS, 'NTuples/ntuple_{}.root'        )
F_AOD_NTUPLE = os.path.join(Constants.DIR_EOS, 'NTuples/aodOnly_ntuple_{}.root')

output = ''
for SP in Constants.SIGNALPOINTS:
    for FS in ('4Mu', '2Mu2J'):
        NAME = 'HTo2XTo{FS}_{SPSTR}'.format(FS=FS, SPSTR=Utilities.SPStr(SP))
        if SP in Constants.PATSIGNALPOINTS and FS == '2Mu2J':
            FNAME = F_NTUPLE.format(NAME)
        else:
            FNAME = F_AOD_NTUPLE.format(NAME)
        output += '{NAME} {FNAME}\n'.format(**locals())

for NAME in ('DY100to200', 'DoubleMuonRun2016D-07Aug17'):
    FNAME = F_NTUPLE.format(NAME)
    output += '{NAME} {FNAME}\n'.format(**locals())

open('NTuples.dat', 'w').write(output)
