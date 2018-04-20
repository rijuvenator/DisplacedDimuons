#!/usr/bin/env python

import sys, os, datetime, FWCore.ParameterSet.Config as cms
from DisplacedDimuons.PATFilter.PATTuple_cfg import process
from crab_cfg import crab_cfg

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

if __name__ == '__main__' and hasattr(sys, 'argv') and 'submit' in sys.argv:
    job_control_ex = '''
config.Data.splitting = 'LumiBased'
config.Data.totalUnits = -1
config.Data.unitsPerJob = %(lumis_per_job)s
#config.Data.lumiMask = 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON_MuonPhys.txt'
#config.Data.runRange = '273150-284044'
config.Data.lumiMask = '%(lumi_mask)s'
config.Data.ignoreLocality = True #x runD to avoid blacklist issue
'''

    lumis_per_job = 20
    lumi_mask = ''

    #create_only = 'create_only' in sys.argv
    just_testing = 'testing' in sys.argv
    scheduler = 'condor' if 'grid' not in sys.argv else 'glite'

    def submit(d):
        new_py = open('tuple_data.py').read()
        new_py += '\n\nprocess.GlobalTag.globaltag = "%(tag)s"\n' % d
        pset = 'crab/psets/tuple_data_crab_%(name)s.py' % d
        open(pset, 'wt').write(new_py)

        job_control = job_control_ex % d
        for k,v in locals().iteritems():
            d[k] = v
        open('crabConfig.py', 'wt').write(crab_cfg % d)
        if not just_testing:
            #if create_only:
                #os.system('crab -create')
            #else:
            os.system('crab submit -c crabConfig.py') #--dryrun
            os.system('rm -f crabConfig.py tmp.json')

    run_limits = []
    for x in sys.argv:
        try:
            run_limits.append(int(x))
        except ValueError:
            pass

    if run_limits:
        run1, run2 = run_limits
        if len(run_limits) != 2 or run1 > run2:
            raise RuntimeError('if any, must specify exactly two numeric arguments   min_run max_run  with max_run >= min_run')

        # Make up a fake lumi_mask that contains all lumis possible
        # for every run in the run range, since crab doesn't seem to
        # listen for a runselection parameter anymore.
        json = ['"%i": [[1,26296]]' % r for r in xrange(run_limits[0], run_limits[1] + 1)]
        open('tmp.json', 'wt').write('{' + ', '.join(json) + '}')
        lumi_mask = 'tmp.json'

        # 7-Aug-2017 re-reco of the 2016 dataset: 287,057,183 events; 66.5 TB
        # There are no good LSs in this data set, see
        # /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON_MuonPhys.txt
        # if run1 >= 272760 and run1 < 273150: #  4,199,947 events;  0.8 TB
        #    dataset = '/DoubleMuon/Run2016B-07Aug17_ver1-v1/AOD'
        #    name    = 'DoubleMuonRun2016B-07Aug17_ver1'
        if run1 >= 273150 and run1 < 275656:   # 82,535,526 events; 15.9 TB
            dataset = '/DoubleMuon/Run2016B-07Aug17_ver2-v1/AOD'
            name    = '/DoubleMuonRun2016B-07Aug17_ver2'
        elif run1 >= 275656 and run1 < 276315: # 27,934,629 events;  6.6 TB
            dataset = '/DoubleMuon/Run2016C-07Aug17-v1/AOD'
            name    = '/DoubleMuonRun2016C-07Aug17'
        elif run1 >= 276315 and run1 < 276831: # 33,861,745 events;  7.6 TB
            dataset = '/DoubleMuon/Run2016D-07Aug17-v1/AOD'
            name    = '/DoubleMuonRun2016D-07Aug17'
        elif run1 == 276831 and run1 < 277932: # 28,246,946 events;  6.8 TB
            dataset = '/DoubleMuon/Run2016E-07Aug17-v1/AOD'
            name    = '/DoubleMuonRun2016E-07Aug17'
        elif run1 >= 277932 and run1 < 278820: # 20,329,921 events;  5.1 TB
            dataset = '/DoubleMuon/Run2016F-07Aug17-v1/AOD'
            name    = '/DoubleMuonRun2016F-07Aug17'
        elif run1 >= 278820 and run1 < 280385: # 45,235,604 events; 11.7 TB
            dataset = '/DoubleMuon/Run2016G-07Aug17-v1/AOD'
            name    = '/DoubleMuonRun2016G-07Aug17'
        elif run1 >= 281613 and run1 < 284045: # 48,912,812 events; 12.8 TB
            dataset = '/DoubleMuon/Run2016H-07Aug17-v1/AOD'
            name    = '/DoubleMuonRun2016H-07Aug17'
        else:
            raise ValueError("don't know how to do a run_limits production for run range [%i,%i]" % run_limits)

        # Data re-reco: same global tag for all runs
        tag = '80X_dataRun2_2016LegacyRepro_v4'
        name = '%s_%i_%i_%s' % (name, run_limits[0], run_limits[1], datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
        print name, tag

        submit(locals())
    else:
        raise ValueError('must do a run-limits production until one dataset is closed')
        x = [
            ]
        for name, dataset, tag in x:
            submit(locals())
