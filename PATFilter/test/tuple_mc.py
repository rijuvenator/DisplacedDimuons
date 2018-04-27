#!/usr/bin/env python

import sys, os
from DisplacedDimuons.PATFilter.PATTuple_cfg import cms, process
from crab_cfg import crab_cfg

#process.maxEvents.input = -1
process.maxEvents.input = 500

process.source.fileNames = [
#    'root://cms-xrd-global.cern.ch//store/user/escalant/HTo2LongLivedTo4mu_MH-125_MFF-20_CTau-1300mm_TuneCUETP8M1_13TeV_pythia8/crab_HTo2LongLivedTo4mu_MH-125_MFF-20_CTau-1300mm_TuneCUETP8M1_13TeV_pythia8_AODSIM-ReHLT_V13-v1/180114_222100/0000/displacedMuons_RAW2DIGI_L1Reco_RECO_1.root'
#    'root://cms-xrd-global.cern.ch//store/user/escalant/HTo2LongLivedTo4mu_MH-125_MFF-50_CTau-50mm_TuneCUETP8M1_13TeV_pythia8/crab_HTo2LongLivedTo4mu_MH-125_MFF-50_CTau-50mm_TuneCUETP8M1_13TeV_pythia8_AODSIM-ReHLT_V13-v1/180114_222527/0000/displacedMuons_RAW2DIGI_L1Reco_RECO_1.root'
#    '/store/mc/RunIISummer16DR80Premix/ZToMuMu_NNPDF30_13TeV-powheg_M_50_120/AODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/60000/04925D7B-18D1-E611-8E8E-001E67586A2F.root'
    '/store/mc/RunIISummer16DR80Premix/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/AODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/110000/001AC973-60E2-E611-B768-001E67586A2F.root'
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

if __name__ == '__main__' and hasattr(sys, 'argv') and 'submit' in sys.argv:
    job_control = '''
config.Data.splitting = 'EventAwareLumiBased'        
config.Data.totalUnits = -1
config.Data.unitsPerJob  = 5000
'''

    just_testing = 'testing' in sys.argv
#    create_only = 'create_only' in sys.argv
#- Note for myself: scheduler is no longer checked

    from DisplacedDimuons.PATFilter.MCSamples import samples
    for sample in samples:
        print sample.name

        new_py = open('tuple_mc.py').read()
        new_py += '\nswitchHLTProcessName(process, "%(hlt_process_name)s")\n' % sample.__dict__

        # Keep all events in signal samples in order to study efficiencies, etc.
        if sample.is_signal:
            new_py += '\nprocess.patDefaultSequence.remove(process.hltFilter)\n'
            new_py += '\nprocess.patDefaultSequence.remove(process.dimuonPreselector)\n'

        sample.pset = 'crab/psets/tuple_mc_crab_%(name)s.py' % sample.__dict__
        os.system('mkdir -p crab/psets')
        open(sample.pset,'wt').write(new_py)

        sample.job_control = job_control % sample.__dict__
        #print sample.__dict__
        #sample.job = 'crab_%(name)s.py' % sample.__dict__
        open('crabConfig.py', 'wt').write(crab_cfg % sample.__dict__)
        if not just_testing:
#            if create_only:
#                os.system('crab submit -c ' + sample.job)
#            else:
            os.system('crab submit -c crabConfig.py')
            os.system('rm crabConfig.py')
