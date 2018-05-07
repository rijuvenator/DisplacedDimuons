import subprocess as bash
from DisplacedDimuons.Common.Constants import SIGNALPOINTS, RECOSIGNALPOINTS

# change MODE to one of:
#    --crab  (submit to CRAB)
#    --batch (submit to LXBATCH)
#    --test  (run locally for 1000 events)
MODE = '--crab'

## submit all HTo2XTo4Mu signal gen only jobs
#for mH, mX, cTau in enumerate(SIGNALPOINTS):
#	bash.call('python runNTupler.py HTo2XTo4Mu --signalpoint {mH} {mX} {cTau} --genonly {MODE}'.format(**locals()), shell=True)

# submit all HTo2XTo4Mu signal jobs
for mH, mX, cTau in enumerate(RECOSIGNALPOINTS):
	bash.call('python runNTupler.py HTo2XTo4Mu --signalpoint {mH} {mX} {cTau} {MODE}'.format(**locals()), shell=True)

# submit all background MC jobs
for data in mcSamples:
	bash.call('python runNTupler.py {NAME} {MODE}'.format(NAME=data.name, MODE=MODE), shell=True)
