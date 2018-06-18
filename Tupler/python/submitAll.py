import subprocess as bash
import DisplacedDimuons.Tupler.Utilities.dataHandler as DH
from DisplacedDimuons.Common.Constants import SIGNALPOINTS, PATSIGNALPOINTS

# for the time being, we only have a few PAT tuple signal points; these are stored in PATSIGNALPOINTS
# as of right now, Tuesday June 12 2018 at 15:43 CET, we have 2 signal points for HTo2XTo2Mu2J only
# When all 66 PAT Tuples are produced, PATSIGNALPOINTS can be removed and everything can be replaced with SIGNALPOINTS
# Additionally, we have 1 PAT Tuple for data and 1 PAT Tuple for DY100to200; the submissions for exactly those are below
# In particular, the script skips BG MC for anything except the 1 sample for DY100to200

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
Do_4Mu_AODOnly   = True
Do_4Mu           = False
Do_2Mu2J_GenOnly = False
Do_2Mu2J_AODOnly = True
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
    for mH, mX, cTau in PATSIGNALPOINTS:
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
    for mH, mX, cTau in PATSIGNALPOINTS:
        verbose('SIGNAL {} : {} {} {}'.format('HTo2XTo2Mu2J', mH, mX, cTau))
        bash.call('python runNTupler.py HTo2XTo2Mu2J --signalpoint {mH} {mX} {cTau}           {MODE}'.format(**locals()), shell=True)

# submit all background MC jobs
if Do_Background:
    mcSamples = DH.getBackgroundSamples()
    for data in mcSamples:
        verbose('BACKGROUND : {}'.format(data.name))
        if data.name == 'DY100to200':
            bash.call('python runNTupler.py {NAME} {MODE}'.format(NAME=data.name, MODE=MODE), shell=True)
        else:
            pass
            # Do not make nTuples for anything other than the DY100to200 PAT tuple set for now
            #bash.call('python runNTupler.py {NAME} --aodonly {MODE}'.format(NAME=data.name, MODE=MODE), shell=True)

# submit all data jobs
if Do_Data:
    dataSamples = DH.getDataSamples()
    for data in dataSamples:
        verbose('DATA : {}'.format(data.name))
        bash.call('python runNTupler.py {NAME} {MODE}'.format(NAME=data.name, MODE=MODE), shell=True)
