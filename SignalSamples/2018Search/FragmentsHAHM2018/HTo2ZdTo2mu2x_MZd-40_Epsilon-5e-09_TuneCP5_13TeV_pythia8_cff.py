CROSS_SECTION = 1 # pb
#MASS_HIGGS = 125 # in GeV (SM Higgs) 
#WIDTH_HIGGS   = 0.027*MASS_HIGGS # Same as default for id=35
MASS_Zd = 40 # in GeV 
WIDTH_Zd = 0.001 # in GeV 
LIFETIME_Zd_inMM = 9937.26474279 # in mm  
EPSILON_Zd =  5e-09

BR_MUMU = 1.462278e-01
BR_EE = 1.462278e-01
BR_TAUTAU = 1.460519e-01

BR_UUBAR = 1.657248e-01
BR_DDBAR = 4.874259e-02
BR_SSBAR = 4.874259e-02

BR_CCBAR = 1.653923e-01
BR_BBBAR = 4.515361e-02

BR_MUNUMUNUBAR = 2.924555e-02
BR_ENUENUBAR = 2.924555e-02
BR_TAUNUTAUNUBAR = 2.924555e-02

import re
EPSILON_Zdmod = str(EPSILON_Zd)
EPSILON_Zdmod = re.sub("\.","p",EPSILON_Zdmod)

import FWCore.ParameterSet.Config as cms
from Configuration.Generator.Pythia8CommonSettings_cfi import *
#from Configuration.Generator.Pythia8CUEP8M1Settings_cfi import * #Old Pythia tune
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *

#gridpackFolder = "/afs/hephy.at/data/aescalante01/gridpacks2016/December2018/"
#gridpackFolder = "/afs/cern.ch/work/e/escalant/public/gridpacks/"
gridpackFolder = "../" 

externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring(gridpackFolder+"HAHM_MS_400_kappa_0p01_MZd_"+str(MASS_Zd)+"_eps_"+EPSILON_Zdmod+"_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz"),
    nEvents = cms.untracked.uint32(10000),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
)

generator = cms.EDFilter("Pythia8HadronizerFilter",
    pythiaPylistVerbosity = cms.untracked.int32(1),
    filterEfficiency = cms.untracked.double(1),
    pythiaHepMCVerbosity = cms.untracked.bool(False),
    comEnergy = cms.double(13000.),
    crossSection = cms.untracked.double(CROSS_SECTION),
    maxEventsToPrint = cms.untracked.int32(10),
    PythiaParameters = cms.PSet(
        pythia8CommonSettingsBlock,
#        pythia8CUEP8M1SettingsBlock, # Old PYTHIA tune
        pythia8CP5SettingsBlock,
        pythia8PSweightsSettingsBlock,
        processParameters = cms.vstring(
            'SLHA:useDecayTable = off', # use pythia8 decay mode instead of decays defined in LH accord
            'LesHouches:setLifetime = 2',
            "1023:new = Zd Zdbar 3 0 0",
            "1023:m0 = %s" % MASS_Zd,
#            "10231:mWidth = %s" % getGammaEpsilon2(MASS_Zd)*EPSILON_Zd*EPSILON_Zd,
            "1023:mWidth = %s" % WIDTH_Zd,
            "1023:tau0 = %s" % LIFETIME_Zd_inMM,
            "1023:isResonance = on",
            "1023:mayDecay = on",
            "1023:oneChannel = 1  %s 100 -2 2" %BR_UUBAR,
            "1023:addChannel = 1  %s 100 -4 4" %BR_CCBAR,
            "1023:addChannel = 1  %s 100 -13 13" %BR_MUMU,
            "1023:addChannel = 1  %s 100 -11 11" %BR_EE,
            "1023:addChannel = 1  %s 100 -15 15" %BR_TAUTAU,
            "1023:addChannel = 1  %s 100 -3 3" %BR_SSBAR,
            "1023:addChannel = 1  %s 100 1 -1" %BR_DDBAR,
            "1023:addChannel = 1  %s 100 -5 5" %BR_BBBAR,
            "1023:addChannel = 1  %s 100 16 -12" %BR_TAUNUTAUNUBAR,
            "1023:addChannel = 1  %s 100 14 -12" %BR_MUNUMUNUBAR,
            "1023:addChannel = 1  %s 100 12 -12" %BR_ENUENUBAR
        ),
        parameterSets = cms.vstring(
            'pythia8CommonSettings',
#            'pythia8CUEP8M1Settings', #Old Pythia Tune
            'pythia8CP5Settings',
            'pythia8PSweightsSettings',
            'processParameters'
        )
    )
)

# -- Require at least one muon in the final state. Muon from taus and HF decays are not considered.
MuFilter = cms.EDFilter("PythiaFilter",
    Status = cms.untracked.int32(0),
    MotherID = cms.untracked.int32(1023),
    MinPt = cms.untracked.double(0.),
    ParticleID = cms.untracked.int32(13),
    MaxEta = cms.untracked.double(10),
    MinEta = cms.untracked.double(-10)
)
ProductionFilterSequence = cms.Sequence(generator*MuFilter) 
