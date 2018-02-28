import FWCore.ParameterSet.Config as cms

# Some modules necessary to run the PAT Tupler
from Configuration.Geometry.GeometryRecoDB_cff import *
from Configuration.StandardSequences.FrontierConditions_GlobalTag_cff import *
from Configuration.StandardSequences.MagneticField_cff import *

from Configuration.AlCa.GlobalTag import GlobalTag as _GlobalTag
GlobalTag = _GlobalTag(GlobalTag, 'auto:run2_mc')

# Load patDefaultSequence (a cms.Task)
from PhysicsTools.PatAlgos.patSequences_cff import *
