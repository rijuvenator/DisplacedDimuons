import FWCore.ParameterSet.Config as cms

hltPhysicsDeclared = cms.EDFilter('HLTPhysicsDeclared',
                                  invert = cms.bool(False),
                                  L1GtReadoutRecordTag = cms.InputTag('gtDigis')
                                  )

# identical to RecoMET/METFilters/python/primaryVertexFilter_cfi.py; recommended
primaryVertex = cms.EDFilter('GoodVertexFilter',
			     vertexCollection = cms.InputTag('offlinePrimaryVertices'),
			     minimumNDOF = cms.uint32(4),
			     maxAbsZ = cms.double(24),
			     maxd0 = cms.double(2)
			     )
# Identical to RecoMET/METFilters/python/scrapingFilter_cfi.py; no longer recommended?
noscraping = cms.EDFilter('FilterOutScraping',
                          applyfilter = cms.untracked.bool(True),
                          debugOn = cms.untracked.bool(False),
                          numtrack = cms.untracked.uint32(10),
                          thresh = cms.untracked.double(0.25)
                          )
