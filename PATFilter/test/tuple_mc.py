#!/usr/bin/env python

import sys, os
from DisplacedDimuons.PATFilter.PATTuple_cfg import cms, process

#process.maxEvents.input = -1
process.maxEvents.input = 500

process.source.fileNames = [
#- Interactive jobs only, for testing
#- official Z+jets sample
#    '/store/mc/RunIISummer16DR80Premix/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/AODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/110000/001AC973-60E2-E611-B768-001E67586A2F.root'
#- 2mu2jets signal
    'root://cms-xrd-global.cern.ch//store/user/escalant/HTo2LongLivedTo2mu2jets_MH-1000_MFF-150_CTau-1000mm_TuneCUETP8M1_13TeV_pythia8/crab_HTo2LongLivedTo2mu2jets_MH-1000_MFF-150_CTau-1000mm_TuneCUETP8M1_13TeV_pythia8_May2018-AOD-v0/180513_123637/0000/EXO-RunIISummer17DR80_HTo2LongLivedTo2mu2jets_MH-1000_MFF-150_CTau-1000mm_TuneCUETP8M1_13TeV_pythia8_1.root'
#- 4mu signal
#    'root://cms-xrd-global.cern.ch//store/user/escalant/HTo2LongLivedTo4mu_MH-1000_MFF-150_CTau-1000mm_TuneCUETP8M1_13TeV_pythia8/crab_HTo2LongLivedTo4mu_MH-1000_MFF-150_CTau-1000mm_TuneCUETP8M1_13TeV_pythia8_May2018-AOD-v0/180513_123603/0000/EXO-RunIISummer17DR80_HTo2LongLivedTo4mu_MH-1000_MFF-150_CTau-1000mm_TuneCUETP8M1_13TeV_pythia8_1.root'
    ]

# Global tags
# RunIISummer16DR80Premix (aka "Moriond17") campaign, CMSSW_8_0_X
process.GlobalTag.globaltag = '80X_mcRun2_asymptotic_2016_TrancheIV_v6'
# CMSSW_9_2_X
# process.GlobalTag.globaltag = '92X_upgrade2017_realistic_v12'

# Prune the list of GEN particles and use the reduced genParticles collection for REC-GEN matching for PAT muons
# "switchHLTProcessName" is not needed for RunIISummer16 campaign, but leave it in
from DisplacedDimuons.PATFilter.PATTools import pruneGenPartsAndRedefineMCMatching, switchHLTProcessName
pruneGenPartsAndRedefineMCMatching(process)

# To switch off parts using RECO tier; not needed at the moment
#AODOnly(process)

# Count events with positive and negative weights and store the
# result in a histogram
process.TFileService = cms.Service('TFileService',
                                   fileName = cms.string('mcweights.root')
                                   )
process.load("DisplacedDimuons.PATFilter.EventCounter_cfi")
process.p += process.EventCounter

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

# Dump the list of genParticles in a format similar to that from turning on PYTHIA's verbosity
process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.particleListDrawer = cms.EDAnalyzer("ParticleListDrawer",
                                            maxEventsToPrint = cms.untracked.int32(20),
                                            src = cms.InputTag("genParticles","","SIM"),
                                            printOnlyHardInteraction = cms.untracked.bool(False),
                                            useMessageLogger = cms.untracked.bool(True)
                                            )
process.MessageLogger.categories.append("ParticleListDrawer")
#process.p += process.particleListDrawer

#print process.dumpPython()

def optimize_units_per_job(nevents, min_nevents=50000000):
    if not isinstance(nevents, int):
        raise TypeError('Non-integer type of \'nevents\': {}'.format(
            type(nevents)))

    if nevents < min_nevents:
        return int(6200)

    # empirical scale factor: 122.5M events with 15k units per job
    # result in about 8000 crab jobs
    scale_factor = 375.0 / 3063676.0

    return int(round(scale_factor * nevents))


if __name__ == '__main__' and 'submit' in sys.argv:
    crab_cfg = '''
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()
config.General.requestName = 'MC2016_%(name)s_Jun2018-test-v3'
config.General.workArea = 'crab'
#config.General.transferLogs = True
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'crab/psets/tuple_mc_crab_%(name)s.py'
config.Data.inputDataset =  '%(dataset)s'
# config.Data.publication = True
config.Data.publication = False
config.Data.outputDatasetTag = 'MC2016_%(name)s'
config.Data.outLFNDirBase    = '/store/user/' + getUsernameFromSiteDB()
# config.Data.splitting = 'Automatic'
config.Data.splitting = 'EventAwareLumiBased'
config.Data.ignoreLocality = True
config.Data.totalUnits = -1
if getUsernameFromSiteDB() in ["escalant", "stempl"]:
    storageSite = 'T2_AT_Vienna'
else:
    storageSite = 'T2_CH_CERN'

if "USER" in config.Data.inputDataset:
    inputDBS = 'phys03'
else:
    inputDBS = 'global'
config.Data.inputDBS = inputDBS

config.Site.whitelist = ["T2_*"]
config.Site.storageSite = storageSite
# config.Site.storageSite = 'T2_CH_CERN'
'''

    just_testing = 'testing' in sys.argv or '--testing' in sys.argv
    create_only  = 'create_only' in sys.argv
    limit_memory = 'limit_memory' in sys.argv
    user_unitsPerJob = 'user_unitsPerJob' in sys.argv

    from DisplacedDimuons.PATFilter.MCSamples import samples
    for sample in samples:
       
        if not 'dy50ToInf' in sample.name and \
                not 'tbarW' in sample.name and \
                not 'ttbar' in sample.name:
            continue

        print sample.name
        print sample.dataset
        #print sample.__dict__

        new_py = open('tuple_mc.py').read()
        # new_py += '\nswitchHLTProcessName(process, "%(hlt_process_name)s")\n' % sample.__dict__

        # Keep all events in signal samples in order to study efficiencies, etc.
        if sample.is_signal:
            new_py += '\nprocess.patDefaultSequence.remove(process.hltFilter)\n'
            # new_py += '\nprocess.patDefaultSequence.remove(process.dimuonPreselector)\n'

        sample.pset = 'crab/psets/tuple_mc_crab_%(name)s.py' % sample.__dict__
        os.system('mkdir -p crab/psets')
        open(sample.pset,'wt').write(new_py)

        open('crabConfig.py', 'wt').write(crab_cfg % sample.__dict__)

        # set max memory
        with open('crabConfig.py', 'a') as f:
            if limit_memory:
                f.write('\nconfig.JobType.maxMemoryMB = 2500')
            else:
                f.write('\nconfig.JobType.maxMemoryMB = 8000')

        # set units per job 
        if 'config.Data.unitsPerJob' in crab_cfg:
            raise RuntimeError('Double definition of ' \
                    '\'config.Data.unitsPerJob\'')

        with open('crabConfig.py', 'a') as f:
            cfg_key = 'config.Data.unitsPerJob' 
            if not user_unitsPerJob:
                cfg_val = optimize_units_per_job(sample.nevents)
            else:
                # define user-specific value here
                cfg_val = 15000

            f.write('\n{} = {}'.format(cfg_key, cfg_val))

        if not just_testing:
            if create_only:
                sample.job = 'crab_%(name)s.py' % sample.__dict__
                os.system('crab submit -c ' + sample.job)
            else:
                os.system('crab submit -c crabConfig.py')
                os.system('rm crabConfig.py')

