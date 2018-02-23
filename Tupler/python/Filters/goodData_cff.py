import FWCore.ParameterSet.Config as cms

hltPhysicsDeclared = cms.EDFilter('HLTPhysicsDeclared',
	invert = cms.bool(False),
	L1GtReadoutRecordTag = cms.InputTag('gtDigis')
)
hltPhysicsDeclaredFilter = cms.Path(hltPhysicsDeclared)

primaryVertex = cms.EDFilter('GoodVertexFilter',
	vertexCollection = cms.InputTag('offlinePrimaryVertices'),
	minimumNDOF      = cms.uint32  (4),
	maxAbsZ          = cms.double  (24),
	maxd0            = cms.double  (2)
)
primaryVertexFilter = cms.Path(primaryVertex)


