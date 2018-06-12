#!/usr/bin/env python

import sys, os, datetime, FWCore.ParameterSet.Config as cms
from DisplacedDimuons.PATFilter.PATTuple_cfg import process
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
    crab_cfg = '''
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()
config.General.requestName = 'PATFilter_%(name)s'
config.General.workArea = 'crab'
#config.General.transferLogs = True
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'tuple_data_crab.py'
config.Data.inputDataset =  '%(ana_dataset)s'
config.Data.inputDBS = 'global'
config.Data.publication = True
config.Data.outputDatasetTag = 'PATFilter_%(name)s'
config.Data.outLFNDirBase = '/store/user/' + getUsernameFromSiteDB()
#config.Data.ignoreLocality = True
config.Data.splitting = 'LumiBased'
config.Data.totalUnits = -1
config.Data.unitsPerJob = 20
#config.Data.runRange = '273150-284044' # full run range for 2016 data
config.Data.runRange = '276315-276340'
config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON_MuonPhys.txt'
#config.Site.whitelist = ["T2_CH_CERN"]
config.Site.storageSite = 'T2_CH_CERN'
'''

    #create_only = 'create_only' in sys.argv
    just_testing = 'testing' in sys.argv

    # 7-Aug-2017 re-reco of the 2016 dataset: 287,057,183 events; 66.5 TB
    dataset_details = [
        # 2016B: runs 273150-275655; 82,535,526 events; 15.9 TB
        #('DoubleMuonRun2016B-07Aug17_ver2', '/DoubleMuon/Run2016B-07Aug17_ver2-v1/AOD'),
        # 2016C: runs 275656-276314; 27,934,629 events;  6.6 TB
        # ('DoubleMuonRun2016C-07Aug17', '/DoubleMuon/Run2016C-07Aug17-v1/AOD'),
        # 2016D: runs 276315-276830; 33,861,745 events;  7.6 TB
        ('DoubleMuonRun2016D-07Aug17', '/DoubleMuon/Run2016D-07Aug17-v1/AOD'),
        # 2016E: runs 276831-277931; 28,246,946 events;  6.8 TB
        # ('DoubleMuonRun2016E-07Aug17', '/DoubleMuon/Run2016E-07Aug17-v1/AOD'),
        # 2016F: runs 277932-278819; 20,329,921 events;  5.1 TB
        # ('DoubleMuonRun2016F-07Aug17', '/DoubleMuon/Run2016F-07Aug17-v1/AOD'),
        # 2016G: runs 278820-280384; 45,235,604 events; 11.7 TB
        # ('DoubleMuonRun2016G-07Aug17', '/DoubleMuon/Run2016G-07Aug17-v1/AOD'),
        # 2016H: runs 281613-284044; 48,912,812 events; 12.8 TB
        # ('DoubleMuonRun2016H-07Aug17', '/DoubleMuon/Run2016H-07Aug17-v1/AOD')
        ]

    for name, ana_dataset in dataset_details:
        print name

        new_py = open('tuple_data.py').read()
        open('tuple_data_crab.py', 'wt').write(new_py)
  
        open('crabConfig.py', 'wt').write(crab_cfg % locals())

        if not just_testing:
            os.system('crab submit -c crabConfig.py')

    if not just_testing:
        os.system('rm crabConfig.py crabConfig.pyc tuple_data_crab.py tuple_data_crab.pyc')
