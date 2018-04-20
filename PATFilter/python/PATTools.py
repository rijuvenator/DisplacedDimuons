#!/usr/bin/env python

import FWCore.ParameterSet.Config as cms

def redefineMCMatching(process):
    # Default PAT muon/electron-MC matching requires, in addition
    # to deltaR < 0.5, the MC and reconstructed leptons to have
    # the same charge, and (reco pt - gen pt)/gen pt <
    # 0.5. Disable these two cuts.
    for x in (process.muonMatch, process.electronMatch):
        x.checkCharge = False
        x.maxDPtRel = 1e6

def pruneMCLeptons(process, use_sim=False):
    process.load('SUSYBSMAnalysis.Zprime2muAnalysis.PrunedMCLeptons_cfi')
    obj = process.prunedMCLeptons
    
    if use_sim:
        # For muon and electron MC matching, want to be able to match to
        # decays-in-flight produced in SIM (whether by GEANT or FastSim),
        # so make some genParticles out of the simTracks.
        # This works only with RECO, so it will be disabled later for AOD.
        process.load('SUSYBSMAnalysis.Zprime2muAnalysis.GenPlusSim_cfi')
        process.prunedMCLeptons.src = 'genSimLeptons'
        obj = process.genSimLeptons * process.prunedMCLeptons

    for x in (process.muonMatch, process.electronMatch):
        # Switch to use the new GEN+SIM particles created above.
        x.matched = cms.InputTag('prunedMCLeptons')
        
        # Default PAT muon/electron-MC matching requires, in addition
        # to deltaR < 0.5, the MC and reconstructed leptons to have
        # the same charge, and (reco pt - gen pt)/gen pt <
        # 0.5. Disable these two cuts.
        x.checkCharge = False
        x.maxDPtRel = 1e6

    process.patDefaultSequence = cms.Sequence(obj * process.patDefaultSequence._seq)

def addMuonMCClassification(process):
    # Run and embed in the patMuons the classification of muons by
    # their GEANT hits.
    process.load('MuonAnalysis.MuonAssociators.muonClassificationByHits_cfi')
    from MuonAnalysis.MuonAssociators.muonClassificationByHits_cfi import addUserData as addClassByHits
    addClassByHits(process.patMuons,extraInfo=True)
    process.patDefaultSequence = cms.Sequence(process.muonClassificationByHits * process.patDefaultSequence._seq)

def removeMuonMCClassification(process):
    # Some magic to undo the use of MC added above in
    # addMuonMCClassification.
    
    process.patDefaultSequence.remove(process.muonClassificationByHits)

    # Remove the InputTags that were added to the userData of the
    # patMuons for the muonClassification.
    def filter(v, s):
        v2 = []
        for x in v:
            if type(x) == cms.InputTag and x.moduleLabel != s:
                v2.append(x)
        return v2
    
    i = process.patMuons.userData.userInts.src.value()
    f = process.patMuons.userData.userFloats.src.value()
    for s in ['classByHitsGlb', 'classByHitsTM', 'classByHitsTMLSAT', 'classByHitsSta']:
        i = filter(i, s)
        f = filter(f, s)
    process.patMuons.userData.userInts.src = i
    process.patMuons.userData.userFloats.src = f

def removeSimLeptons(process):
    if hasattr(process, 'genSimLeptons'):
        process.patDefaultSequence.remove(process.genSimLeptons)
        if hasattr(process, 'prunedMCLeptons'):
            process.prunedMCLeptons.src = 'genParticles'

def removePrunedMCLeptons(process):
    if hasattr(process, 'prunedMCLeptons'):
        process.patDefaultSequence.remove(process.prunedMCLeptons)

def removeMCUse(process):
    # Remove anything that requires MC truth.
    # from PhysicsTools.PatAlgos.tools.coreTools import removeMCMatching
    # removeMCMatching(process, ['All'])

    from PhysicsTools.PatAlgos.tools.coreTools import runOnData
    runOnData(process)

    # I have no idea why all gen processes also have to be removed by hand...
    process.patDefaultSequence.remove(process.electronMatch)
    process.patDefaultSequence.remove(process.muonMatch)
    process.patDefaultSequence.remove(process.tauMatch)
    process.patDefaultSequence.remove(process.tauGenJets)
    process.patDefaultSequence.remove(process.tauGenJetsSelectorAllHadrons)
    process.patDefaultSequence.remove(process.tauGenJetMatch)
    process.patDefaultSequence.remove(process.photonMatch)
    process.patDefaultSequence.remove(process.patJetPartonMatch)
    process.patDefaultSequence.remove(process.patJetGenJetMatch)
    process.patDefaultSequence.remove(process.patJetPartonsLegacy)
    process.patDefaultSequence.remove(process.patJetPartonAssociationLegacy)
    process.patDefaultSequence.remove(process.patJetFlavourAssociationLegacy)
    process.patDefaultSequence.remove(process.patJetPartons)
    process.patDefaultSequence.remove(process.patJetFlavourAssociation)

    # No longer needed
    # removeMCMatching(process, ['METs'], postfix='PF')
    # removeMuonMCClassification(process)
    # removeSimLeptons(process)
    # removePrunedMCLeptons(process)
    
def switchHLTProcessName(process, name):
    # As the correct trigger process name is different from the
    # default "HLT" for some MC samples, this is a simple tool to
    # switch this in all places that it's needed.
    process.patTrigger.processName = name
    process.patTriggerEvent.processName = name

def AODOnly(process):
    #from PhysicsTools.PatAlgos.tools.coreTools import restrictInputToAOD
    #restrictInputToAOD(process) 
    #removeMuonMCClassification(process) # no need to remove as it was not added
    removeSimLeptons(process)

# Some scraps to aid in debugging that can be put in your top-level
# config (could be turned into functions a la the above):
'''
# At the end of the job, print out a table summarizing the PAT
# candidates seen/made.
process.patDefaultSequence.remove(process.selectedPatCandidateSummary)
process.selectedPatCandidateSummary.perEvent = cms.untracked.bool(True)
process.selectedPatCandidateSummary.dumpItems = cms.untracked.bool(True)
process.patDefaultSequence *= process.selectedPatCandidateSummary

# Print messages tracing through the execution of the
# analyzers/producers (e.g. beginJob/beginRun/analyze/endRun/endJob).
process.Tracer = cms.Service('Tracer')
process.SimpleMemoryCheck = cms.Service('SimpleMemoryCheck')

# To print every event the content (the branch names) of the
# edm::Event.
process.eca = cms.EDAnalyzer('EventContentAnalyzer')
process.peca = cms.Path(process.eca)

# Dump extensive L1 and HLT trigger info (objects, path results).
process.load('L1Trigger.L1ExtraFromDigis.l1extratest_cfi')
process.load('HLTrigger.HLTcore.triggerSummaryAnalyzerAOD_cfi')
#process.triggerSummaryAnalyzerAOD.inputTag = cms.InputTag('hltTriggerSummaryAOD', '', hltProcessName)
process.ptrigAnalyzer = cms.Path(process.l1extratest*process.triggerSummaryAnalyzerAOD)

# Dump the list of genParticles in a format similar to that from
# turning on PYTHIA's verbosity.
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.printTree = cms.EDAnalyzer(
    'ParticleListDrawer',
    maxEventsToPrint = cms.untracked.int32(-1),
    src = cms.InputTag('genParticles'),
    printOnlyHardInteraction = cms.untracked.bool(True),
    useMessageLogger = cms.untracked.bool(True)
    )
process.MessageLogger.categories.append('ParticleListDrawer')
process.ptree = cms.Path(process.printTree)

# Extra options for controlling how CMSSW works.
process.source.noEventSort = cms.untracked.bool(True)
process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')

'''
