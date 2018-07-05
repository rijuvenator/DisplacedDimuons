#!/usr/bin/env python

import sys, os, datetime, FWCore.ParameterSet.Config as cms
import json
from DisplacedDimuons.PATFilter.PATTuple_cfg import process
from DisplacedDimuons.PATFilter.tools import query_yes_no
#from crab_cfg import crab_cfg

#process.maxEvents.input = -1
process.maxEvents.input = 1000

process.source.fileNames = [
    '/store/data/Run2016D/DoubleMuon/AOD/07Aug17-v1/10000/00554E0D-7497-E711-806A-02163E019C5C.root'
    ]

# Global tag for the 7-Aug-2017 reprocessing of 2016 data
process.GlobalTag.globaltag = "80X_dataRun2_2016LegacyRepro_v4"

# Remove anything that requires MC truth
from DisplacedDimuons.PATFilter.PATTools import removeMCUse
removeMCUse(process)

# Filter on HLT paths
process.hltFilter = cms.EDFilter("HLTHighLevel",
                                 TriggerResultsTag = cms.InputTag("TriggerResults","","HLT"),
                                 HLTPaths = cms.vstring("HLT_L2DoubleMu*_NoVertex*"), # provide list of HLT paths (or patterns) you want
                                 andOr = cms.bool(True), # to deal with multiple triggers: True (OR) accept if ANY is true, False (AND) accept if ALL are true
                                 throw = cms.bool(True)  # throw exception on unknown path names
                                 )
process.p += process.hltFilter

# Filter on displaced standalone and/or global muons if needed; disabled for now
# process.load("DisplacedDimuons.PATFilter.DimuonPreselector_cfi")
# process.p += process.dimuonPreselector

# Dump all HLT paths and pass/fail counts at the end of each run/job
process.hlTrigReport = cms.EDAnalyzer("HLTrigReport",
                                      HLTriggerResults = cms.InputTag("TriggerResults","","HLT")
                                      )
process.MessageLogger.categories.append("HLTrigReport")
process.report = cms.EndPath(process.hlTrigReport)

#print process.dumpPython()

if __name__ == '__main__' and 'submit' in sys.argv:

    #create_only = 'create_only' in sys.argv
    just_testing = 'testing' in sys.argv or '--testing' in sys.argv
    limit_memory = 'limit_memory' in sys.argv or '--limit_memory' in sys.argv
    dryrun = 'dryrun' in sys.argv or '--dryrun' in sys.argv

    # 7-Aug-2017 re-reco of the 2016 dataset: 287,057,183 events; 66.5 TB
    dataset_details = [
        # 2016B: runs 273150-275655; 82,535,526 events; 15.9 TB
        ('DoubleMuonRun2016B-07Aug17_ver2', '/DoubleMuon/Run2016B-07Aug17_ver2-v1/AOD'),
        # 2016C: runs 275656-276314; 27,934,629 events;  6.6 TB
        ('DoubleMuonRun2016C-07Aug17', '/DoubleMuon/Run2016C-07Aug17-v1/AOD'),
        # 2016D: runs 276315-276830; 33,861,745 events;  7.6 TB
        ('DoubleMuonRun2016D-07Aug17', '/DoubleMuon/Run2016D-07Aug17-v1/AOD'),
        # 2016E: runs 276831-277931; 28,246,946 events;  6.8 TB
        ('DoubleMuonRun2016E-07Aug17', '/DoubleMuon/Run2016E-07Aug17-v1/AOD'),
        # 2016F: runs 277932-278819; 20,329,921 events;  5.1 TB
        ('DoubleMuonRun2016F-07Aug17', '/DoubleMuon/Run2016F-07Aug17-v1/AOD'),
        # 2016G: runs 278820-280384; 45,235,604 events; 11.7 TB
        ('DoubleMuonRun2016G-07Aug17', '/DoubleMuon/Run2016G-07Aug17-v1/AOD'),
        # 2016H: runs 281613-284044; 48,912,812 events; 12.8 TB
        ('DoubleMuonRun2016H-07Aug17', '/DoubleMuon/Run2016H-07Aug17-v1/AOD')
        ]

    # load the CRAB configuration
    with open('crab_cfg.json', 'r') as f:
        crab_cfg = json.load(f)['config_data']

    for name, ana_dataset in dataset_details:
        print name

        new_py = open('tuple_data.py').read()
        open('tuple_data_crab.py', 'wt').write(new_py)

         # extract 'custom_tag' from the dict such that it can be properly
        # inserted again later on
        locals_dict = locals()
        locals_dict['custom_tag'] = crab_cfg['custom_tag']

        # fill in all known values
        for k in crab_cfg.keys():
            crab_cfg[k] = (crab_cfg[k] % locals_dict)

        # dynamically modify certain elements of crab_cfg 
        if os.environ['USER'] in ['stempl']:
            crab_cfg['config.Site.storageSite'] = "'T2_AT_Vienna'"
        elif 'config.Site.storageSite' not in crab_cfg.keys():
            crab_cfg['config.Site.storageSite'] = "'T2_CH_CERN'"

        if "USER" in crab_cfg['config.Data.inputDataset']:
            print('+++ Warning: You are using phys03 DBS. ' \
                    'Are you sure about this?')
            crab_cfg['config.Data.inputDBS'] = "'phys03'"
        else:
            crab_cfg['config.Data.inputDBS'] = "'global'"

        if limit_memory:
            crab_cfg['config.JobType.maxMemoryMB'] = "2500"
        else:
            crab_cfg['config.JobType.maxMemoryMB'] = "8000"

        # define entries that should not be written to the final config file
        discard_keys = ['custom_tag']

        # further preparations for the final output file
        crab_cfg_str = 'from CRABClient.UserUtilities import config, ' \
                'getUsernameFromSiteDB'
        crab_cfg_str += '\nconfig = config()\n'
        crab_cfg_str += '\n'.join(['{} = {}'.format(k,v) for k,v in zip(
            crab_cfg.keys(), crab_cfg.values()) if k not in discard_keys])

        # write the crab config file
        open('crabConfig.py', 'wt').write(crab_cfg_str % locals_dict)
        print('Crab config file \'crabConfig.py\' written.')

        if not just_testing:
            print('\n\nCurrent CRAB configuration:\n')
            with open('crabConfig.py', 'r') as cc:
                for l in cc.readlines():
                    print('    {}'.format(l.strip('\n')))

            print('\n')
            if not query_yes_no('Proceed with submission?', default='yes'):
                print('Aborting submission...')
                sys.exit(1)
            else:
                pass

            dryrun_str = ' --dryrun' if dryrun else ''

            os.system('crab submit -c crabConfig.py' + dryrun_str)

    if not just_testing:
        os.system('rm crabConfig.py crabConfig.pyc tuple_data_crab.py tuple_data_crab.pyc')

