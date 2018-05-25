CROSS_SECTION = 1 # pb
MASS_HIGGS = 1000 # in GeV 
WIDTH_HIGGS   = 0.01*MASS_HIGGS # Same as default for id=35 (changed to 1% from 2.7%)
MASS_X = 150 # in GeV 
CTAU_X = 1000 # in mm  

import FWCore.ParameterSet.Config as cms

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.Pythia8CUEP8M1Settings_cfi import *
#from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *

generator = cms.EDFilter("Pythia8GeneratorFilter",
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(13000.),
    crossSection = cms.untracked.double(CROSS_SECTION),
    maxEventsToPrint = cms.untracked.int32(10),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
        pythia8CUEP8M1SettingsBlock, # Old PYTHIA tune
#        pythia8CP5SettingsBlock,
        processParameters = cms.vstring(
            "Higgs:useBSM = on",
            "HiggsBSM:all = off",
#            "HiggsBSM:ffbar2H2 = on",
            "HiggsBSM:gg2H2 = on",
            "6000113:new = LL_s LL_sbar 1 0 0",
            "6000113:m0 = %s" % MASS_X,
            "6000113:mWidth = 0.01",
            "6000113:tau0 = %s" % CTAU_X,
            "6000113:isResonance = on",
            "6000113:mayDecay = on",
            "6000113:oneChannel = 1  1.0 100 13 -13",
            "35:m0 = %s" % MASS_HIGGS,
            "35:mWidth = %s" % WIDTH_HIGGS,
            "35:2:bRatio = 0.0",
            "35:3:bRatio = 0.0",
            "35:4:bRatio = 0.0",
            "35:5:bRatio = 0.0",
            "35:7:bRatio = 0.0",
            "35:8:bRatio = 0.0",
# Keep small coupling of H0 to gluons in order to be produced            
#            "35:9:bRatio = 0.0",
            "35:10:bRatio= 0.0",
            "35:12:bRatio= 0.0",
            "35:13:bRatio= 0.0",
            "35:2:meMode = 100",
            "35:3:meMode = 100",
            "35:4:meMode = 100",
            "35:5:meMode = 100",
            "35:7:meMode = 100",
            "35:8:meMode = 100",
#            "35:9:meMode = 100",
            "35:10:meMode= 100",
            "35:12:meMode= 100",
            "35:13:meMode= 100",
            "35:addChannel = 1 1. 100 6000113 6000113",
            "35:onMode = off",
            "35:onIfAny = 6000113"
        ),
        parameterSets = cms.vstring(
            'pythia8CommonSettings',
            'pythia8CUEP8M1Settings',
#            'pythia8CP5Settings',
            'processParameters'
        )
    )
)

#ProductionFilterSequence = cms.Sequence(generator) 
