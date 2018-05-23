import subprocess as bash
import DisplacedDimuons.Tupler.Utilities.dataHandler as DH
from DisplacedDimuons.Common.Constants import SIGNALPOINTS

# change MODE to one of:
#    --crab  (submit to CRAB)
#    --batch (submit to LXBATCH)
#    --test  (run locally for 1000 events)
#    <empty> (run locally for the entire dataset)
MODE = '--crab'

# block booleans
Do_4Mu_GenOnly   = True
Do_4Mu           = True
Do_2Mu2J_GenOnly = True
Do_2Mu2J         = True
Do_Background    = True
Do_Data          = True

# verbose printer
def verbose(message):
    print '\033[31m=== {} ===\033[m'.format(message)

# submit all HTo2XTo4Mu signal gen only jobs
if Do_4Mu_GenOnly:
    for mH, mX, cTau in SIGNALPOINTS:
        verbose('GEN ONLY SIGNAL {} : {} {} {}'.format('HTo2XTo4Mu', mH, mX, cTau))
        bash.call('python runNTupler.py HTo2XTo4Mu --signalpoint {mH} {mX} {cTau} --genonly {MODE}'.format(**locals()), shell=True)

# submit all HTo2XTo4Mu signal jobs
if Do_4Mu:
    for mH, mX, cTau in SIGNALPOINTS:
        verbose('SIGNAL {} : {} {} {}'.format('HTo2XTo4Mu', mH, mX, cTau))
        bash.call('python runNTupler.py HTo2XTo4Mu --signalpoint {mH} {mX} {cTau} --aodonly {MODE}'.format(**locals()), shell=True)

# submit all HTo2XTo2Mu2J signal gen only jobs
if Do_2Mu2J_GenOnly:
    for mH, mX, cTau in SIGNALPOINTS:
        verbose('GEN ONLY SIGNAL {} : {} {} {}'.format('HTo2XTo2Mu2J', mH, mX, cTau))
        bash.call('python runNTupler.py HTo2XTo2Mu2J --signalpoint {mH} {mX} {cTau} --genonly {MODE}'.format(**locals()), shell=True)

# submit all HTo2XTo2Mu2J signal jobs
if Do_2Mu2J:
    for mH, mX, cTau in SIGNALPOINTS:
        verbose('SIGNAL {} : {} {} {}'.format('HTo2XTo2Mu2J', mH, mX, cTau))
        bash.call('python runNTupler.py HTo2XTo2Mu2J --signalpoint {mH} {mX} {cTau} --aodonly {MODE}'.format(**locals()), shell=True)

# submit all background MC jobs
if Do_Background:
    mcSamples = DH.getBackgroundSamples()
    for data in mcSamples:
        verbose('BACKGROUND : {}'.format(data.name))
        if data.name == 'DY100to200':
            bash.call('python runNTupler.py {NAME} {MODE}'.format(NAME=data.name, MODE=MODE), shell=True)
        else:
            bash.call('python runNTupler.py {NAME} --aodonly {MODE}'.format(NAME=data.name, MODE=MODE), shell=True)

# submit all data jobs
if Do_Data:
    dataSamples = DH.getDataSamples()
    for data in dataSamples:
        verbose('DATA : {}'.format(data.name))
        bash.call('python runNTupler.py {NAME} {MODE}'.format(NAME=data.name, MODE=MODE), shell=True)
