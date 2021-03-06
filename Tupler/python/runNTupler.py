import os, re
import subprocess as bash
from DisplacedDimuons.Common.Constants import CMSSW_BASE
import DisplacedDimuons.Tupler.Utilities.CFGParser as CFGParser

CONFIG = CFGParser.getConfiguration()
F_CMS_CFG = 'submit_cfg.py'
if CONFIG.BATCH and not CONFIG.TEST:
    bash.call('mkdir -p cfg', shell=True)
    try:
        COUNT = int(bash.check_output('ls cfg | grep -c "submit.*py"', shell=True).strip('\n'))+1
    except bash.CalledProcessError:
        COUNT = 1
    F_CMS_CFG = 'cfg/submit_cfg_{}.py'.format(COUNT)

# verbose printer
def verbose(header, data):
    print '\n\033[32m{}:\n----------\n\033[m'.format(header), data

# write the cmsRun config file
def WriteCMSRUNConfig(CONFIG):
    CMS_CFG = open('NTupler_cfg.py').read()
    replaceDict = {
        r'^(MAXEVENTS\s+=).*' : r"\1 {}"  .format(CONFIG.MAXEVENTS      ),
        r'^(INPUTFILES\s+=).*': r"\1 {}"  .format(str(CONFIG.INPUTFILES)),
        r'^(OUTPUTFILE\s+=).*': r"\1 '{}'".format(CONFIG.OUTPUTFILE     ),
        r'^(ISMC\s+=).*'      : r"\1 {}"  .format(CONFIG.DATA.isMC      ),
        r'^(ISSIGNAL\s+=).*'  : r"\1 {}"  .format(CONFIG.DATA.isSignal  ),
        r'^(FINALSTATE\s+=).*': r"\1 '{}'".format(CONFIG.FINALSTATE     ),
        r'^(GENS_TAG\s+=).*'  : r"\1 {}"  .format(str(CONFIG.GENS_TAG)  ),
        r'^(SOURCE\s+=).*'    : r"\1 '{}'".format(CONFIG.SOURCE         ),
    }
    for key, val in replaceDict.iteritems():
        CMS_CFG = re.sub(key, val, CMS_CFG, count=1, flags=re.MULTILINE)
    open(F_CMS_CFG, 'w').write(CMS_CFG)
    if CONFIG.VERBOSE: verbose('CMSRUN CONFIG FILE', CMS_CFG)
WriteCMSRUNConfig(CONFIG)

# submit to CRAB
if CONFIG.CRAB and not CONFIG.TEST:
    # get the dataset key for the dataset to run over
    if CONFIG.NAME in CFGParser.DEFAULT_DATASETS:
        SAMPLE = CONFIG.NAME
    else:
        SAMPLE = 'DEFAULT'
    DATASETKEY = CFGParser.DEFAULT_DATASETS[SAMPLE][CONFIG.SOURCE]

    # since crab mode doesn't do a DAS query, one final check to make sure
    # we don't try to submit a CRAB job with _ as a dataset
    if CONFIG.DATA.datasets[DATASETKEY] == '_':
        print '[DATAHANDLER ERROR]: Invalid dataset _, likely a PATTuple set not created yet. Please try --aodonly for sample', CONFIG.DATA.name
        exit()

    # crab submission script
    # note the output directory: T2_CH_CERN, and /store/user/USER/DisplacedDimuons/CRAB/
    # change this if desired
    CRAB_CFG = '''
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()
config.General.requestName             = 'nTupler_{NAME}'
config.General.workArea                = 'crab'
config.General.transferLogs            = True
config.JobType.pluginName              = 'Analysis'
config.JobType.psetName                = '{PSET_NAME}'
config.JobType.allowUndistributedCMSSW = {ALLOWUNDISTRIBUTEDCMSSW}
config.Data.inputDataset               = '{INPUT_DATASET}'
config.Data.inputDBS                   = '{INPUT_DBS}'
config.Data.publication                = {PUBLISH}
config.Data.publishDBS                 = '{PUBLISH_DBS}'
config.Data.ignoreLocality             = {IGNORE_LOCALITY}
config.Data.splitting                  = '{SPLITTING}'
config.Data.totalUnits                 = {TOTAL_UNITS}
config.Data.unitsPerJob                = {UNITS_PER_JOB}
config.Data.runRange                   = '{RUN_RANGE}'
config.Data.lumiMask                   = '{LUMI_MASK}'
config.Data.outLFNDirBase              = '/store/user/%s/DisplacedDimuons/CRAB/' % (getUsernameFromSiteDB())
config.Data.outputDatasetTag           = 'ntuple_{NAME}'
if getUsernameFromSiteDB() in ('escalant', 'stempl'):
    STORAGESITE = 'T2_AT_Vienna'
else:
    STORAGESITE = 'T2_CH_CERN'
config.Site.storageSite                = STORAGESITE
config.Site.whitelist                  = ['T2_CH_CERN', 'T2_AT_Vienna']
'''
    CRAB_CFG = CRAB_CFG.format(
        NAME                    = CONFIG.DATA.name + ('_GEN' if CONFIG.SOURCE == 'GEN' else '') + ('_AOD' if CONFIG.SOURCE == 'AOD' else ''),
        PSET_NAME               = F_CMS_CFG,
        ALLOWUNDISTRIBUTEDCMSSW = True,
        INPUT_DATASET           = CONFIG.DATA.datasets[DATASETKEY],
        INPUT_DBS               = CONFIG.DATA.instances[DATASETKEY].replace('prod/', ''),
        PUBLISH                 = False,
        PUBLISH_DBS             = 'phys03',
        IGNORE_LOCALITY         = True,
        SPLITTING               = 'FileBased',
        TOTAL_UNITS             = -1,
        UNITS_PER_JOB           = 500,
        RUN_RANGE               = '',
        # LUMI_MASK               = '/afs/cern.ch/user/s/stempl/public/DDM/StoppPtls_json_subset.txt',
        LUMI_MASK               = '/afs/cern.ch/user/s/stempl/public/DDM/cosmics-jsons/CosmicJSON_E_D_UGMT_base_and_bottomOnly.txt',
        # LUMI_MASK               = '/afs/cern.ch/user/s/stempl/public/DDM/cosmics-jsons/reHLT-validationJSON_sameLScontent.txt',
        # LUMI_MASK               = '/afs/cern.ch/user/s/stempl/public/DDM/cosmics-jsons/reHLT-validationJSON_differentLScontent.txt',
    )
    # comment out lines not needed -- to be improved by doing it based on data vs mc
    COMMENTS = ('transferLogs', 'ignoreLocality', 'runRange', 'lumiMask')
    for parameter in COMMENTS:
        CRAB_CFG = re.sub(r'(config.*'+parameter+')', r'#\1', CRAB_CFG)

    if CONFIG.VERBOSE: verbose('CRAB CONFIG FILE', CRAB_CFG)

    F_CRAB_CFG = 'crabConfig.py'
    open(F_CRAB_CFG, 'w').write(CRAB_CFG)
    if CONFIG.SUBMIT:
        bash.call('crab submit -c {}'.format(F_CRAB_CFG), shell=True)
        bash.call('rm {F} {F}c'.format(F=F_CRAB_CFG), shell=True)
        bash.call('rm {F} {F}c'.format(F=F_CMS_CFG ), shell=True)
    else:
        bash.call('rm {F}'.format(F=F_CRAB_CFG), shell=True)
        bash.call('rm {F}'.format(F=F_CMS_CFG ), shell=True)


# submit to LXBATCH
elif CONFIG.BATCH and not CONFIG.TEST:
    # assumes the proxy in /tmp/x509up_u***** created after voms-proxy-init
    # was copied to ~/ i.e. /afs/cern.ch/user/U/USER/x509up_uUID
    USER  = os.environ['USER']
    ID    = bash.check_output('id -u', shell=True).strip('\n')
    PROXY = '/afs/cern.ch/user/{}/{}/x509up_u{}'.format(USER[0], USER, ID)

    # batch submission script
    LXBATCH = '''
#!/bin/bash
export X509_USER_PROXY={PROXY}
cd {CMSSW_BASE}/src/
eval `scramv1 runtime -sh`
cd DisplacedDimuons/Tupler/python
cmsRun {F_CMS_CFG}
rm {F_CMS_CFG}
rm -f core.*
'''.format(
        CMSSW_BASE = CMSSW_BASE,
        PROXY      = PROXY,
        F_CMS_CFG  = F_CMS_CFG
    )
    if CONFIG.VERBOSE: verbose('LXBATCH SUBMIT SCRIPT', LXBATCH)

    F_LXBATCH = 'submit_lxbatch.sh'
    open(F_LXBATCH, 'w').write(LXBATCH)
    if CONFIG.SUBMIT:
        bash.call('bsub -q 1nh -J tup_{} < {}'.format(CONFIG.DATA.name, F_LXBATCH), shell=True)
    bash.call('rm {}'.format(F_LXBATCH), shell=True)

# run locally, test mode or otherwise
else:
    if CONFIG.SUBMIT:
        bash.call('cmsRun {}'.format(F_CMS_CFG), shell=True)
        bash.call('rm {F}'.format(F=F_CMS_CFG), shell=True)
