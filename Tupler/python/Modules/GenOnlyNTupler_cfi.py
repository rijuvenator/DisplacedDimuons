import FWCore.ParameterSet.Config as cms

TFileService = cms.Service('TFileService', fileName = cms.string('output_ntuple_gen_only.root'))

GenOnlyNTupler = cms.EDAnalyzer('GenOnlyNTupler',
	cms.untracked.PSet(
		gens = cms.InputTag('genParticles'),
#		gens = cms.InputTag('prunedGenParticles'),
		GEIP = cms.InputTag('generator'),
	)
)
