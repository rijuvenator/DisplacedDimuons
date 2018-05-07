import os, re
import subprocess as bash
from DisplacedDimuons.Common.Constants import CMSSW_BASE
import DisplacedDimuons.Tupler.Utilities.CFGParser as CFGParser

CONFIG = CFGParser.getConfiguration()
F_CMS_CFG = 'submit_cfg.py'

# verbose printer
def verbose(header, data):
    print '\n\033[32m{}:\n----------\n\033[m'.format(header), data

# write the cmsRun config file
def WriteCMSRUNConfig(CONFIG):
    CMS_CFG = open('NTupler_cfg.py').read()
    replaceDict = {
        r'^(MAXEVENTS\s+=).*' : r"\1 {}"  .format(CONFIG.MAXEVENTS      ),
        r'^(INPUTFILES\s+=).*': r"\1 {}"  .format(str(CONFIG.INPUTFILES)),
        r'^(PLUGIN\s+=).*'    : r"\1 '{}'".format(CONFIG.PLUGIN         ),
        r'^(OUTPUTFILE\s+=).*': r"\1 '{}'".format(CONFIG.OUTPUTFILE     ),
        r'^(ISMC\s+=).*'      : r"\1 {}"  .format(CONFIG.DATA.isMC      ),
    }
    for key, val in replaceDict.iteritems():
        CMS_CFG = re.sub(key, val, CMS_CFG, count=1, flags=re.MULTILINE)
    open(F_CMS_CFG, 'w').write(CMS_CFG)
    if CONFIG.VERBOSE: verbose('CMSRUN CONFIG FILE', CMS_CFG)
WriteCMSRUNConfig(CONFIG)

# submit to CRAB
if CONFIG.CRAB and not CONFIG.TEST:
    CRAB_CFG = '''
from CRABClient.UserUtilities import config
config = config()
config.General.requestName   = 'nTupler_{NAME}'
config.General.workArea      = 'crab'
config.General.transferLogs  = True
config.JobType.pluginName    = 'Analysis'
config.JobType.psetName      = '{PSET_NAME}'
config.Data.inputDataset     = '{INPUT_DATASET}'
config.Data.inputDBS         = '{INPUT_DBS}'
config.Data.publication      = {PUBLISH}
config.Data.publishDBS       = '{PUBLISH_DBS}'
config.Data.ignoreLocality   = {IGNORE_LOCALITY}
config.Data.splitting        = '{SPLITTING}'
config.Data.totalUnits       = {TOTAL_UNITS}
config.Data.unitsPerJob      = {UNITS_PER_JOB}
config.Data.runRange         = '{RUN_RANGE}'
config.Data.lumiMask         = '{LUMI_MASK}'
config.Data.outLFNDirBase    = '{OUTPUT_DIR}'
config.Data.outputDatasetTag = 'ntuple_{NAME}'
config.Site.storageSite      = 'T2_CH_CERN'
config.Site.whiteList        = ['T2_CH_CERN']
'''
    CRAB_CFG = CRAB_CFG.format(
        NAME            = CONFIG.DATA.name,
        PSET_NAME       = F_CMS_CFG,
        INPUT_DATASET   = CONFIG.DATA.dataset,
        INPUT_DBS       = CONFIG.DATA.instance.replace('prod/', ''),
        PUBLISH         = False,
        PUBLISH_DBS     = 'phys03',
        IGNORE_LOCALITY = True,
        SPLITTING       = 'FileBased',
        TOTAL_UNITS     = -1,
        UNITS_PER_JOB   = 10,
        RUN_RANGE       = '',
        LUMI_MASK       = '',
        OUTPUT_DIR      = CONFIG.EOSDIR,
    )
    # comment out lines not needed -- to be improved by doing it based on data vs mc
    COMMENTS = ('transferLogs', 'ignoreLocality', 'runRange', 'lumiMask')
    for parameter in COMMENTS:
        CRAB_CFG = re.sub(r'(config.*'+parameter+')', r'#\1', CRAB_CFG)

    if CONFIG.VERBOSE: verbose('CRAB CONFIG FILE', CRAB_CFG)

    F_CRAB_CFG = 'crabConfig.py'
    open(F_CRAB_CFG, 'w').write(CRAB_CFG)
    #bash.call('crab submit -c {}'.format(F_CRAB_CFG), shell=True)
    bash.call('rm {}'.format(F_CRAB_CFG), shell=True)


# submit to LXBATCH
elif CONFIG.BATCH and not CONFIG.TEST:
    LXBATCH = '''
#!/bin/bash
export X509_USER_PROXY={PROXY}
cd {CMSSW_BASE}/src/
eval `scramv1 runtime -sh`
cd DisplacedDimuons/Tupler/python
cmsRun {F_CMS_CFG}
rm -f core.*
'''.format(
        CMSSW_BASE = CMSSW_BASE,
        PROXY      = '/afs/cern.ch/user/a/adasgupt/x509up_u79337',
        F_CMS_CFG  = F_CMS_CFG
    )
    if CONFIG.VERBOSE: verbose('LXBATCH SUBMIT SCRIPT', LXBATCH)

    F_LXBATCH = 'submit_lxbatch.sh'
    open(F_LXBATCH, 'w').write(LXBATCH)
    #bash.call('bsub -q 1nh -J tup_{} < {}'.format(CONFIG.DATA.name, F_LXBATCH), shell=True)
    bash.call('rm {}'.format(F_LXBATCH), shell=True)

# run locally
else:
    pass
    #bash.call('cmsRun {}'.format(F_CMS_CFG), shell=True)

# remove the cmsRun configuration file
bash.call('rm {}'.format(F_CMS_CFG), shell=True)
