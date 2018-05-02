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

# Filter on displaced muons
process.load("DisplacedDimuons.PATFilter.DimuonPreselector_cfi")
process.p += process.dimuonPreselector

# Dump all HLT paths and pass/fail counts at the end of each run/job
process.hlTrigReport = cms.EDAnalyzer("HLTrigReport",
                                      HLTriggerResults = cms.InputTag("TriggerResults","","HLT")
                                      )
process.MessageLogger.categories.append("HLTrigReport")
process.report = cms.EndPath(process.hlTrigReport)

#print process.dumpPython()

if __name__ == '__main__' and 'submit' in sys.argv:
    crab_cfg = '''
from CRABClient.UserUtilities import config
config = config()
config.General.requestName = 'ana_TriggerReduction_%(name)s'
config.General.workArea = 'crab'
#config.General.transferLogs = True
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'tuple_data_crab.py'
config.Data.inputDataset =  '%(ana_dataset)s'
config.Data.inputDBS = 'global'                       
config.Data.publication = True
config.Data.outputDatasetTag = 'ana_TriggerReduction_%(name)s'
config.Data.outLFNDirBase = '/store/user/alfloren'
#config.Data.ignoreLocality = True
config.Data.splitting = 'LumiBased'
config.Data.totalUnits = -1
config.Data.unitsPerJob = 20
config.Data.runRange = '276315-276340'
config.Data.lumiMask = '/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON_MuonPhys.txt'
#config.Site.whitelist = ["T2_CH_CERN"]
config.Site.storageSite = 'T2_CH_CERN'
'''

    

    #create_only = 'create_only' in sys.argv
    just_testing = 'testing' in sys.argv
    
    dataset_details = [
            #('DoubleMuonRun2016B-07Aug17_ver2', '/DoubleMuon/Run2016B-07Aug17_ver2-v1/AOD'),
           # ('DoubleMuonRun2016C-07Aug17', '/DoubleMuon/Run2016C-07Aug17-v1/AOD'),
            ('DoubleMuonRun2016D-07Aug17', '/DoubleMuon/Run2016D-07Aug17-v1/AOD'),
           # ('DoubleMuonRun2016E-07Aug17', '/DoubleMuon/Run2016E-07Aug17-v1/AOD'),
           # ('DoubleMuonRun2016F-07Aug17', '/DoubleMuon/Run2016F-07Aug17-v1/AOD'),
            #('DoubleMuonRun2016G-07Aug17', '/DoubleMuon/Run2016G-07Aug17-v1/AOD'),
            #('DoubleMuonRun2016H-07Aug17', '/DoubleMuon/Run2016H-07Aug17-v1/AOD'),	    
            ]

    for name, ana_dataset in dataset_details:
            print name

            new_py = open('tuple_data.py').read()
            open('tuple_data_crab.py', 'wt').write(new_py)

          
            open('crabConfig.py', 'wt').write(crab_cfg % locals())
        
            if not just_testing:
                os.system('crab submit -c crabConfig.py')

    if not just_testing:
            os.system('rm crabConfig.py tuple_data_crab.py tuple_data_crab.pyc')                  
       
