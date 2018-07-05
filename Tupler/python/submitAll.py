import subprocess as bash
import DisplacedDimuons.Common.DataHandler as DH
from DisplacedDimuons.Common.Constants import SIGNALPOINTS

# Monday July 2 2018 at 10:47 CET:
# all HTo2XTo2Mu2J signal    PAT Tuples are available (33)
# all HTo2XTo4Mu   signal    PAT Tuples are available (33)
# all BG MC                  PAT Tuples are available (11) EXCEPT
#   - most mass binned DY
#   - QCD
# all DoubleMuon Run2016 B-H PAT Tuples are available (7)

# change MODE to one of:
#    --crab  (submit to CRAB)
#    --batch (submit to LXBATCH)
#    --test  (run locally for 1000 events)
#    <empty> (run locally for the entire dataset)
# you can also append
#    --verbose  (print out args, cmsRun cfg, and CRAB cfg)
#    --nosubmit (do not submit this job, whether CRAB, BATCH, or local)
MODE = '--crab'

# block booleans
Do_4Mu_GenOnly   = False
Do_4Mu_AODOnly   = False
Do_4Mu           = True
Do_2Mu2J_GenOnly = False
Do_2Mu2J_AODOnly = False
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
        bash.call('python runNTupler.py HTo2XTo4Mu   --signalpoint {mH} {mX} {cTau} --genonly {MODE}'.format(**locals()), shell=True)

# submit all HTo2XTo4Mu signal aod only jobs
if Do_4Mu_AODOnly:
    for mH, mX, cTau in SIGNALPOINTS:
        verbose('AOD ONLY SIGNAL {} : {} {} {}'.format('HTo2XTo4Mu', mH, mX, cTau))
        bash.call('python runNTupler.py HTo2XTo4Mu   --signalpoint {mH} {mX} {cTau} --aodonly {MODE}'.format(**locals()), shell=True)

# submit all HTo2XTo4Mu signal PAT Tuple jobs
if Do_4Mu:
    for mH, mX, cTau in SIGNALPOINTS:
        verbose('SIGNAL {} : {} {} {}'.format('HTo2XTo4Mu', mH, mX, cTau))
        bash.call('python runNTupler.py HTo2XTo4Mu   --signalpoint {mH} {mX} {cTau}           {MODE}'.format(**locals()), shell=True)

# submit all HTo2XTo2Mu2J signal gen only jobs
if Do_2Mu2J_GenOnly:
    for mH, mX, cTau in SIGNALPOINTS:
        verbose('GEN ONLY SIGNAL {} : {} {} {}'.format('HTo2XTo2Mu2J', mH, mX, cTau))
        bash.call('python runNTupler.py HTo2XTo2Mu2J --signalpoint {mH} {mX} {cTau} --genonly {MODE}'.format(**locals()), shell=True)

# submit all HTo2XTo2Mu2J signal aod only jobs
if Do_2Mu2J_AODOnly:
    for mH, mX, cTau in SIGNALPOINTS:
        verbose('AOD ONLY SIGNAL {} : {} {} {}'.format('HTo2XTo2Mu2J', mH, mX, cTau))
        bash.call('python runNTupler.py HTo2XTo2Mu2J --signalpoint {mH} {mX} {cTau} --aodonly {MODE}'.format(**locals()), shell=True)

# submit all HTo2XTo2Mu2J signal PAT Tuple jobs
if Do_2Mu2J:
    for mH, mX, cTau in SIGNALPOINTS:
        verbose('SIGNAL {} : {} {} {}'.format('HTo2XTo2Mu2J', mH, mX, cTau))
        bash.call('python runNTupler.py HTo2XTo2Mu2J --signalpoint {mH} {mX} {cTau}           {MODE}'.format(**locals()), shell=True)

# submit all background MC jobs
if Do_Background:
    mcSamples = DH.getBackgroundSamples()
    for data in mcSamples:
        verbose('BACKGROUND : {}'.format(data.name))
        if data.datasets['PAT'] == '_': continue
        bash.call('python runNTupler.py {NAME} {MODE}'.format(NAME=data.name, MODE=MODE), shell=True)

# submit all data jobs
if Do_Data:
    dataSamples = DH.getDataSamples()
    for data in dataSamples:
        verbose('DATA : {}'.format(data.name))
        bash.call('python runNTupler.py {NAME} {MODE}'.format(NAME=data.name, MODE=MODE), shell=True)
