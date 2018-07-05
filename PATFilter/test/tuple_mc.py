#!/usr/bin/env python

import sys, os
import json
from DisplacedDimuons.PATFilter.PATTuple_cfg import cms, process
from DisplacedDimuons.PATFilter.tools import query_yes_no

#process.maxEvents.input = -1
process.maxEvents.input = 500

process.source.fileNames = [
#- Interactive jobs only, for testing
#- official Z+jets sample
#    '/store/mc/RunIISummer16DR80Premix/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/AODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/110000/001AC973-60E2-E611-B768-001E67586A2F.root'
#- 2mu2jets signal
    # 'root://cms-xrd-global.cern.ch//store/user/escalant/HTo2LongLivedTo2mu2jets_MH-1000_MFF-150_CTau-1000mm_TuneCUETP8M1_13TeV_pythia8/crab_HTo2LongLivedTo2mu2jets_MH-1000_MFF-150_CTau-1000mm_TuneCUETP8M1_13TeV_pythia8_May2018-AOD-v0/180513_123637/0000/EXO-RunIISummer17DR80_HTo2LongLivedTo2mu2jets_MH-1000_MFF-150_CTau-1000mm_TuneCUETP8M1_13TeV_pythia8_1.root'
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

def optimize_units_per_job(sample):
    # empirical scale factor: 122.5M events with 15k units per job
    # result in about 8000 crab jobs
    # (we want this large dataset to have ~2000 jobs)
    scale_factor_1kjobs = 8 * 15000.0 / 122547040.0

    thresholds = {
            100000000: 1.0, # aim: 1k jobs
            50000000: 2.0,  # aim: 500 jobs
            40000000: 2.5,  # aim: 400 jobs
            30000000: 3.33, # aim: 300 jobs
            10000000: 10.0, # aim: 100 jobs
            1000000: 100.0, # aim: 10 jobs
            100000: 1000.0, # aim: 1 job 
            }

    # initialize scale_factor (which is ultimately used to scale the number of
    # events such that a given number of crab jobs is created)
    scale_factor = None

    for k in thresholds.keys():
        if sample.nevents > k:
            scale_factor = thresholds[k] * scale_factor_1kjobs
            break

    if scale_factor is None:
        scale_factor = 1.0 # make one crab job with all events

    return int(round(scale_factor * sample.nevents))


if __name__ == '__main__' and 'submit' in sys.argv:

    # load the CRAB configuration
    with open('crab_cfg.json', 'r') as f:
        crab_cfg = json.load(f)['config_mc']

    just_testing = 'testing' in sys.argv or '--testing' in sys.argv
    create_only  = 'create_only' in sys.argv or '--create_only' in sys.argv
    limit_memory = 'limit_memory' in sys.argv or '--limit_memory' in sys.argv
    fix_units_per_job = 'fix_units_per_job' in sys.argv or '--fix_units_per_job' in sys.argv
    dryrun = 'dryrun' in sys.argv or '--dryrun' in sys.argv


    from DisplacedDimuons.PATFilter.MCSamples import samples

    for sample in samples:

        if sample.name != 'Hto2Xto4mu_125_50_50':
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

        # extract 'custom_tag' from the dict such that it can be properly
        # inserted again later on
        sample_dict = sample.__dict__
        sample_dict['custom_tag'] = crab_cfg['custom_tag']

        # fill in all known sample values
        for k in crab_cfg.keys():
            crab_cfg[k] = (crab_cfg[k] % sample_dict)

        # dynamically modify certain elements of crab_cfg 
        if os.environ['USER'] in ['stempl']:
            crab_cfg['config.Site.storageSite'] = "'T2_AT_Vienna'"
        elif 'config.Site.storageSite' not in crab_cfg.keys():
            crab_cfg['config.Site.storageSite'] = "'T2_CH_CERN'"

        if "USER" in crab_cfg['config.Data.inputDataset']:
            crab_cfg['config.Data.inputDBS'] = "'phys03'"
        else:
            crab_cfg['config.Data.inputDBS'] = "'global'"

        if limit_memory:
            crab_cfg['config.JobType.maxMemoryMB'] = "2500"
        else:
            crab_cfg['config.JobType.maxMemoryMB'] = "8000"

        if not fix_units_per_job:
            crab_cfg['config.Data.unitsPerJob'] = \
                    str(optimize_units_per_job(sample))
        else:
            crab_cfg['config.Data.unitsPerJob'] = "15000"

        # define entries that should not be written to the final config file
        discard_keys = ['custom_tag']

        # further preparations for the final output file
        crab_cfg_str = 'from CRABClient.UserUtilities import config, ' \
                'getUsernameFromSiteDB'
        crab_cfg_str += '\nconfig = config()\n'
        crab_cfg_str += '\n'.join(['{} = {}'.format(k,v) for k,v in zip(
            crab_cfg.keys(), crab_cfg.values()) if k not in discard_keys])

        # write the crab config file
        open('crabConfig.py', 'wt').write(crab_cfg_str % sample_dict)
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

            if create_only:
                sample.job = 'crab_%(name)s.py' % sample_dict
                os.system('crab submit -c ' + sample.job + dryrun_str)
            else:
                os.system('crab submit -c crabConfig.py' + dryrun_str)
                os.system('rm crabConfig.py')

