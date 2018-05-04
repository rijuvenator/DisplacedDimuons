# import ROOT in batch mode
import sys
oldargv = sys.argv[:]
sys.argv = [ '-b-' ]
import ROOT

ROOT.gROOT.SetBatch(True)
sys.argv = oldargv

# load FWLite C++ libraries
ROOT.gSystem.Load("libFWCoreFWLite.so");
ROOT.gSystem.Load("libDataFormatsFWLite.so");
ROOT.FWLiteEnabler.enable()

# load FWlite python libraries
from DataFormats.FWLite import Handle, Events
from math import *

#Utils for Longlived Generator Level studies.
from GenLongLivedUtils import *
from SimpleTools import *


#Samples to process
samplesDir = '/afs/hephy.at/work/a/aescalante/cmssw/SimpleGen/'

samples = Sample()

samples.AddSample(samplesDir+'EXO-RunIIFall17GS_HTo2LongLivedTo4mu_MH-1000_MFF-150_CTau-100mm_TuneCUETP8M1_13TeV_pythia8_1.root', 'M_{H}=1000, M_{X}=150GeV, c#tau=100mm', '1000_150_CTau_100mm', 1)
#samples.AddSample(samplesDir+'EXO-RunIIFall16MiniAODv2_XXTo4Mu_M-3_CTau-10mm_TuneCUETP8M1_13TeV_pythia8.root', 'M=3GeV, c#tau=0.1m', 'M_3GeV_CTau_10mm', 2)
#samples.AddSample(samplesDir+'EXO-RunIIFall16MiniAODv2_XXTo4Mu_M-3_CTau-100mm_TuneCUETP8M1_13TeV_pythia8.root', 'M=3GeV, c#tau=1m', 'M_3GeV_CTau_100mm', 3)
#samples.AddSample(samplesDir+'EXO-RunIIFall16MiniAODv2_XXTo4Mu_M-3_CTau-1000mm_TuneCUETP8M1_13TeV_pythia8.root', 'M=3GeV, c#tau=10m', 'M_3GeV_CTau_1000mm', 4)

#samples.AddSample(samplesDir+'EXO-RunIIFall16MiniAODv2_XXTo4Mu_M-10_CTau-1mm_TuneCUETP8M1_13TeV_pythia8.root', 'M=10GeV, c#tau=0.01m', 'M_10GeV_CTau_1mm', 6)
#samples.AddSample(samplesDir+'EXO-RunIIFall16MiniAODv2_XXTo4Mu_M-10_CTau-10mm_TuneCUETP8M1_13TeV_pythia8.root', 'M=10GeV, c#tau=0.1', 'M_10GeV_CTau_10mm', 8)
#samples.AddSample(samplesDir+'EXO-RunIIFall16MiniAODv2_XXTo4Mu_M-10_CTau-100mm_TuneCUETP8M1_13TeV_pythia8.root', 'M=10GeV, c#tau=1m', 'M_10GeV_CTau_100mm', 38)
#samples.AddSample(samplesDir+'EXO-RunIIFall16MiniAODv2_XXTo4Mu_M-10_CTau-1000mm_TuneCUETP8M1_13TeV_pythia8.root', 'M=10GeV, c#tau=10m', 'M_10GeV_CTau_1000mm', 28)

#samples.AddSample(samplesDir+'EXO-RunIIFall16MiniAODv2_XXTo4Mu_M-50_CTau-1mm_TuneCUETP8M1_13TeV_pythia8.root', 'M=50GeV, c#tau=0.01m', 'M_50GeV_CTau_1mm', 30)
#samples.AddSample(samplesDir+'EXO-RunIIFall16MiniAODv2_XXTo4Mu_M-50_CTau-10mm_TuneCUETP8M1_13TeV_pythia8.root', 'M=50GeV, c#tau=0.1m', 'M_50GeV_CTau_10mm', 9)
#samples.AddSample(samplesDir+'EXO-RunIIFall16MiniAODv2_XXTo4Mu_M-50_CTau-100mm_TuneCUETP8M1_13TeV_pythia8.root', 'M=50GeV, c#tau=1m', 'M_50GeV_CTau_100mm', 46)
#samples.AddSample(samplesDir+'EXO-RunIIFall16MiniAODv2_XXTo4Mu_M-50_CTau-1000mm_TuneCUETP8M1_13TeV_pythia8.root', 'M=50GeV, c#tau=10m', 'M_50GeV_CTau_1000mm', 49)


sampleName = samples.GetSampleName()
legendName = samples.GetLegendName()
histName = samples.GetHistName()

#Handles and collections
#handleMuons = Handle ("std::vector<pat::Muon>")
#labelMuons = ("slimmedMuons")

# IN MINIAOD
#handlePruned  = Handle ("std::vector<reco::GenParticle>")
#labelPruned = ("prunedGenParticles")

# FOR GEN-SIM
handlePruned  = Handle ("std::vector<reco::GenParticle>")
labelPruned = ("genParticles")

#handleTriggerBits = Handle("edm::TriggerResults")
#labelTriggerBits = ("TriggerResults","","HLT")

#handleTriggerObjects = Handle("std::vector<pat::TriggerObjectStandAlone>")
#labelTriggerObject  = ("selectedPatTrigger")


GenLevelStudy = True
if GenLevelStudy == True:
    #1D-Histograms
    mother1Mass = createSimple1DPlot("mother1Mass", "mother1Mass", 40, 0, 100, samples)
    mother2Mass = createSimple1DPlot("mother2Mass", "mother2Mass", 40, 0, 100, samples)
    mother1LorentzBoost = createSimple1DPlot("mother1LorentzBoost", "mother1LorentzBoost", 40, 0, 1000, samples)
    mother2LorentzBoost = createSimple1DPlot("mother2LorentzBoost", "mother2LorentzBoost", 40, 0, 1000, samples)
    mother1Eta = createSimple1DPlot("mother1Eta", "mother1Eta", 40, -3.0, 3.0, samples)
    mother1Phi = createSimple1DPlot("mother1Phi", "mother1Phi", 40, -3.15, 3.15, samples)
    mother2Eta = createSimple1DPlot("mother2Eta", "mother2Eta", 40, -3.0, 3.0, samples)
    mother2Phi = createSimple1DPlot("mother2Phi", "mother2Phi", 40, -3.15, 3.15, samples)

    ptX = createSimple1DPlot("ptX", "ptX", 40, 0, 250, samples)
    pzX = createSimple1DPlot("pzX", "pzX", 40, 0, 250, samples)
    
    etaDaughter1 = createSimple1DPlot("etaDaughter1", "etaDaughter1", 20, -5.0, 5.0, samples)
    etaDaughter2 = createSimple1DPlot("etaDaughter2", "etaDaughter2", 20, -5.0, 5.0, samples)
    etaDaughterPtCut = createSimple1DPlot("etaDaughterPtCut", "etaDaughterPtCut", 20, -5.0, 5.0, samples)
    
    ptDaughter1 = createSimple1DPlot("ptDaughter1", "ptDaughter1", 40, 0, 150, samples)
    ptDaughter2 = createSimple1DPlot("ptDaughter2", "ptDaughter2", 40, 0, 150, samples)
    ptDaughter1Zoom = createSimple1DPlot("ptDaughter1Zoom", "ptDaughter1Zoom", 30, 0, 45, samples)
    ptDaughter2Zoom = createSimple1DPlot("ptDaughter2Zoom", "ptDaughter2Zoom", 30, 0, 45, samples)
    
    ctauLow = createSimple1DPlot("ctauLow", "ctauLow", 50, 0, 5, samples)
    ctau = createSimple1DPlot("ctau", "ctau", 50, 0, 50, samples)
    ctauHigh = createSimple1DPlot("ctauHigh", "ctauHigh", 50, 0, 250, samples)

    lxy = createSimple1DPlot("lxy", "lxy", 100, 0, 700, samples)
    lxyZoom = createSimple1DPlot("lxyZoom", "lxyZoom", 100, 0, 100, samples)
    
    lz = createSimple1DPlot("lz", "lz", 50, 0, 1000, samples)
    lzZoom = createSimple1DPlot("lzZoom", "lzZoom", 50, 0, 200, samples)
    deltaR = createSimple1DPlot("deltaR", "deltaR", 25, 0.0, 2*pi, samples)

#2D-Histograms
    lz_lxy = createSimple2DPlot("lz_lxy", "lz vs lxy", 350, 0, 1000, 200, 0, 700, samples)
    lz_lxyZoom = createSimple2DPlot("lz_lxyZoom", "lz vs lxy", 200, 0, 200, 100, 0, 100, samples)



TriggerStudy = False
#TriggerFlags = ["HLT_TrkMu15_DoubleTrkMu5NoFiltersNoVtx_v2", "HLT_DoubleMu38NoFiltersNoVtx_v2", "HLT_L2DoubleMu28_NoVertex_2Cha_Angle2p5_Mass10_v2", "DST_DoubleMu3_Mass10_PFScouting_v1", "HLT_L2DoubleMu23_NoVertex_v2"]
TriggerFlags = ["HLT_TrkMu15_DoubleTrkMu5NoFiltersNoVtx_v2", "HLT_DoubleMu38NoFiltersNoVtx_v2", "HLT_L2DoubleMu28_NoVertex_2Cha_Angle2p5_Mass10_v2", "DST_DoubleMu3_Mass10_PFScouting_v1", "HLT_L2DoubleMu23_NoVertex_v2", "HLT_TripleMu_12_10_5_v2", "DST_L1DoubleMu_PFScouting_v1", "HLT_L2Mu10_v1", "HLT_L1SingleMu16_v1", "HLT_DoubleMu23NoFiltersNoVtxDisplaced_v2"]
ptTriggerEffNum =[]
for kTriggerFlags in TriggerFlags:
    ptTriggerEffNum.append(createSimple1DPlot("ptTriggerEffNum_"+kTriggerFlags, "ptTriggerEffNum_"+kTriggerFlags, 30, 0., 70., samples))
ptTriggerEffDen = createSimple1DPlot("ptTriggerEffDen", "ptTriggerEffDen", 30, 0., 70., samples)

#print len(ptTriggerEffNum[1][1]), ptTriggerEffNum[1][1]
#print len(ptTriggerEffNum[1]), ptTriggerEffNum[1]
#print len(ptTriggerEffNum), ptTriggerEffNum

Resolution = False
ReconstructionFlags = ["STA","PFTrack"] # Add as many as you want, as long as they are defined in RecoUtils.py

if Resolution ==  True:
    etaResolution = createSimple1DPlot("etaResolution", "etaResolution", 50, -0.2, 0.2, samples)
    phiResolution = createSimple1DPlot("phiResolution", "phiResolution", 50, -0.2, 0.2, samples)
    ptResolution = createSimple1DPlot("ptResolution", "ptResolution", 15, -0.40, 0.40, samples)
    massResolution = createSimple1DPlot("massResolution", "massResolution", 15, -0.40, 0.40, samples)
    deltaRResolution = createSimple1DPlot("deltaRResolution", "deltaRResolution", 25, -0.2, 0.2, samples)
    deltaEtaResolution = createSimple1DPlot("deltaEtaResolution", "deltaEtaResolution", 25, -0.2, 0.2, samples)
    deltaPhiResolution = createSimple1DPlot("deltaPhiResolution", "deltaPhiResolution", 25, -0.2, 0.2, samples)
    deltaPhiResolutionHighMomentum = createSimple1DPlot("deltaPhiResolutionHighMomentum", "deltaPhiResolutionHighMomentum", 25, -0.2, 0.2, samples)
    deltaEtadeltaPhiResolution = createSimple2DPlot("deltaEtadeltaPhiResolution", "Delta Phi vs #Delta Eta", 25, -0.3, 0.3, 25, -0.3, 0.3, samples)
    nMatchedResolution = createSimple1DPlot("nMatchedResolution", "nMatchedResolution", 6, 0., 5.0, samples)

    recoMassMother1 = createSimple1DPlot("recoMassMother1", "recoMassMother1", 25, 0.0, 80, samples)
    recoMassMother2 = createSimple1DPlot("recoMassMother2", "recoMassMother2", 25, 0.0, 80, samples)

    nReconstructedMothers = createSimple1DPlot("nReconstructedMothers", "nReconstructedMothers", 3, 0., 3, samples)
    nReconstructedMother1 = createSimple1DPlot("nReconstructedMother1", "nReconstructedMother1", 3, 0., 3, samples)
    nReconstructedMother2 = createSimple1DPlot("nReconstructedMother2", "nReconstructedMother2", 3, 0., 3, samples)

Efficiencies = False
if Efficiencies ==  True:
    #Denominator    
    lxyMu = createSimple1DPlot("lxyMu", "lxyMu", 100, 0, 700, samples)
    lxyMuZoom = createSimple1DPlot("lxyMuZoom", "lxyMuZoom", 100, 0, 100, samples)
    lzMu = createSimple1DPlot("lzMu", "lzMu", 50, 0, 1000, samples)
    lzMuZoom = createSimple1DPlot("lzMuZoom", "lzMuZoom", 50, 0, 200, samples)
    etaMu = createSimple1DPlot("etaMu", "etaMu", 40, -2.4, 2.4, samples)

    lxyMu_eta_X_Pt_10_Lz_X_dR_l0p5 = createSimple1DPlot("lxyMu_eta_X_Pt_10_Lz_X_dR_l0p5", "lxyMu_eta_X_Pt_10_Lz_X_dR_l0p5", 100, 0, 100, samples)
    lxyMu_eta_X_Pt_10_Lz_X_dR_g0p5 = createSimple1DPlot("lxyMu_eta_X_Pt_10_Lz_X_dR_g0p5", "lxyMu_eta_X_Pt_10_Lz_X_dR_g0p5", 100, 0, 100, samples)

    etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5 = createSimple1DPlot("etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5", "etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5", 40, -2.4, 2.4, samples)
    etaMu_Pt_10_Lxy_X_Lz_X_dR_g0p5 = createSimple1DPlot("etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5", "etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5", 40, -2.4, 2.4, samples)

    etaMu_Pt_10_Lxy_l10_Lz_l46_dR_X = createSimple1DPlot("etaMu_Pt_10_Lxy_l10_Lz_l46_dR_X", "etaMu_Pt_10_Lxy_l10_Lz_l46_dR_X", 40, -2.4, 2.4, samples)
    etaMu_Pt_10_Lxy_g10_Lz_g46_dR_X =  createSimple1DPlot("etaMu_Pt_10_Lxy_g10_Lz_g46_dR_X", "etaMu_Pt_10_Lxy_g10_Lz_g46_dR_X", 40, -2.4, 2.4, samples)

    etaMu_Pt_g50_Lxy_g10_Lz_g46_dR_X = createSimple1DPlot("etaMu_Pt_g50_Lxy_g10_Lz_g46_dR_X", "etaMu_Pt_g50_Lxy_g10_Lz_g46_dR_X", 40, -2.4, 2.4, samples)
    etaMu_Pt_g10l50_Lxy_g10_Lz_g46_dR_X =  createSimple1DPlot("etaMu_Pt_g10l50_Lxy_g10_Lz_g46_dR_X", "etaMu_Pt_g10l50_Lxy_g10_Lz_g46_dR_X", 40, -2.4, 2.4, samples)

    etaMu_Pt_10_Lxy_g10_Lz_g46_dR_l0p5 = createSimple1DPlot("etaMu_Pt_10_Lxy_g10_Lz_g46_dR_l0p5", "etaMu_Pt_10_Lxy_g10_Lz_g46_dR_l0p5", 40, -2.4, 2.4, samples)
    etaMu_Pt_10_Lxy_g10_Lz_g46_dR_g0p5 =  createSimple1DPlot("etaMu_Pt_10_Lxy_g10_Lz_g46_dR_g0p5", "etaMu_Pt_10_Lxy_g10_Lz_g46_dR_g0p5", 40, -2.4, 2.4, samples)


    #STA Nominator
    lxySTAMatched = createSimple1DPlot("lxySTAMatched", "lxySTAMatched", 100, 0, 700, samples)
    lxyZoomSTAMatched = createSimple1DPlot("lxyZoomSTAMatched", "lxyZoomSTAMatched", 100, 0, 100, samples)
    lzSTAMatched = createSimple1DPlot("lzSTAMatched", "lzSTAMatched", 50, 0, 1000, samples)
    lzZoomSTAMatched = createSimple1DPlot("lzZoomSTAMatched", "lzZoomSTAMatched", 50, 0, 200, samples)
    etaSTAMatched = createSimple1DPlot("etaSTAMatched", "etaSTAMatched", 40, -2.4, 2.4, samples)
    
    lxyMu_eta_X_Pt_10_Lz_X_dR_l0p5_STAMatched = createSimple1DPlot("lxyMu_eta_X_Pt_10_Lz_X_dR_l0p5_STAMatched", "lxyMu_eta_X_Pt_10_Lz_X_dR_l0p5_STAMatched", 100, 0, 100, samples)
    lxyMu_eta_X_Pt_10_Lz_X_dR_g0p5_STAMatched = createSimple1DPlot("lxyMu_eta_X_Pt_10_Lz_X_dR_g0p5_STAMatched", "lxyMu_eta_X_Pt_10_Lz_X_dR_g0p5_STAMatched", 100, 0, 100, samples)

    etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5_STAMatched = createSimple1DPlot("etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5_STAMatched", "etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5_STAMatched", 40, -2.4, 2.4, samples)
    etaMu_Pt_10_Lxy_X_Lz_X_dR_g0p5_STAMatched = createSimple1DPlot("etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5_STAMatched", "etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5_STAMatched", 40, -2.4, 2.4, samples)

    etaMu_Pt_10_Lxy_l10_Lz_l46_dR_X_STAMatched = createSimple1DPlot("etaMu_Pt_10_Lxy_l10_Lz_l46_dR_X_STAMatched", "etaMu_Pt_10_Lxy_l10_Lz_l46_dR_X_STAMatched", 40, -2.4, 2.4, samples)
    etaMu_Pt_10_Lxy_g10_Lz_g46_dR_X_STAMatched =  createSimple1DPlot("etaMu_Pt_10_Lxy_g10_Lz_g46_dR_X_STAMatched", "etaMu_Pt_10_Lxy_g10_Lz_g46_dR_X_STAMatched", 40, -2.4, 2.4, samples)

    etaMu_Pt_g50_Lxy_g10_Lz_g46_dR_X_STAMatched = createSimple1DPlot("etaMu_Pt_g50_Lxy_g10_Lz_g46_dR_X_STAMatched", "etaMu_Pt_g50_Lxy_g10_Lz_g46_dR_X_STAMatched", 40, -2.4, 2.4, samples)
    etaMu_Pt_g10l50_Lxy_g10_Lz_g46_dR_X_STAMatched =  createSimple1DPlot("etaMu_Pt_g10l50_Lxy_g10_Lz_g46_dR_X_STAMatched", "etaMu_Pt_g10l50_Lxy_g10_Lz_g46_dR_X_STAMatched", 40, -2.4, 2.4, samples)

    etaMu_Pt_10_Lxy_g10_Lz_g46_dR_l0p5_STAMatched = createSimple1DPlot("etaMu_Pt_10_Lxy_g10_Lz_g46_dR_l0p5_STAMatched", "etaMu_Pt_10_Lxy_g10_Lz_g46_dR_l0p5_STAMatched", 40, -2.4, 2.4, samples)
    etaMu_Pt_10_Lxy_g10_Lz_g46_dR_g0p5_STAMatched =  createSimple1DPlot("etaMu_Pt_10_Lxy_g10_Lz_g46_dR_g0p5_STAMatched", "etaMu_Pt_10_Lxy_g10_Lz_g46_dR_g0p5_STAMatched", 40, -2.4, 2.4, samples)    

    #PF 
    lxyPFMatched = createSimple1DPlot("lxyPFMatched", "lxyPFMatched", 100, 0, 700, samples)
    lxyZoomPFMatched = createSimple1DPlot("lxyZoomPFMatched", "lxyZoomPFMatched", 100, 0, 100, samples)
    lzPFMatched = createSimple1DPlot("lzPFMatched", "lzPFMatched", 50, 0, 1000, samples)
    lzZoomPFMatched = createSimple1DPlot("lzZoomPFMatched", "lzZoomPFMatched", 50, 0, 200, samples)
    etaPFMatched = createSimple1DPlot("etaPFMatched", "etaPFMatched", 40, -2.4, 2.4, samples)

#Run over samples
for index, ksamples in enumerate(sampleName):
    print "SAMPLE: "+ksamples+"\n"
    events = Events(ksamples)    
    for i,event in enumerate(events):   
#       print "\n#Event", i


#        if i > 1000: continue

#        event.getByLabel (labelMuons, handleMuons)
#        muons = handleMuons.product()

        event.getByLabel (labelPruned, handlePruned)
        pruned = handlePruned.product()

#        event.getByLabel(labelTriggerBits, handleTriggerBits)
#        triggerBits = handleTriggerBits.product()
#        event.getByLabel(labelTriggerObject, handleTriggerObjects)
#        triggerObjets = handleTriggerObjects.product()

        if GenLevelStudy== True:
            #Get Mother information.
            genMother = getMothers(pruned, mother1=35, mother2=36)        
            for kCandidate in genMother:
                if kCandidate.pdgId() == 35:                
                    mother1Mass[index].Fill(kCandidate.mass())
                    mother1LorentzBoost[index].Fill(kCandidate.energy()/kCandidate.mass())
                    mother1Eta[index].Fill(kCandidate.eta())
                    mother1Phi[index].Fill(kCandidate.phi())
                
                if kCandidate.pdgId() == 36:
                    mother2Mass[index].Fill(kCandidate.mass())
                    mother2LorentzBoost[index].Fill(kCandidate.energy()/kCandidate.mass())
                    mother2Eta[index].Fill(kCandidate.eta())
                    mother2Phi[index].Fill(kCandidate.phi())

                ptX[index].Fill(kCandidate.pt())
                pzX[index].Fill(kCandidate.pz())
        
            #Dauthters decay length
            genDaughter = getGenDaughters(pruned, mother1=35, mother2=36, daughter1=13, daughter2=13)                
            for kCandidate in genDaughter:
                if getTrueMother(kCandidate).pdgId() == 35: 
                    ptDaughter1[index].Fill(kCandidate.pt())
                    ptDaughter1Zoom[index].Fill(kCandidate.pt())
                if getTrueMother(kCandidate).pdgId() == 36: 
                    ptDaughter2[index].Fill(kCandidate.pt())
                    ptDaughter2Zoom[index].Fill(kCandidate.pt())
            
                         
                lxy[index].Fill(abs(kCandidate.vertex().rho()))
                lxyZoom[index].Fill(abs(kCandidate.vertex().rho()))            

                lz[index].Fill(abs(kCandidate.vertex().Z()))
                lzZoom[index].Fill(abs(kCandidate.vertex().Z()))

                lz_lxy[index].Fill(abs(kCandidate.vertex().Z()), abs(kCandidate.vertex().rho()))
                lz_lxyZoom[index].Fill(abs(kCandidate.vertex().Z()), abs(kCandidate.vertex().rho()))

                ctau[index].Fill(kCandidate.vertex().rho()*kCandidate.mother(0).mass()/kCandidate.mother(0).pt())
                ctauLow[index].Fill(kCandidate.vertex().rho()*kCandidate.mother(0).mass()/kCandidate.mother(0).pt())
                ctauHigh[index].Fill(kCandidate.vertex().rho()*kCandidate.mother(0).mass()/kCandidate.mother(0).pt())
            

            #Dauthters psudorapidity inclusive in eta
            genDaughterInclusive = getGenDaughters(pruned, mother1=35, mother2=36, daughter1=13, daughter2=13, Inclusive = True)
            for kCandidate in genDaughterInclusive:
                if getTrueMother(kCandidate).pdgId() == 35: 
                    etaDaughter1[index].Fill(kCandidate.eta())
                if getTrueMother(kCandidate).pdgId() == 36: 
                    etaDaughter2[index].Fill(kCandidate.eta())
                if kCandidate.pt() > 5:
                    etaDaughterPtCut[index].Fill(kCandidate.eta())

            #Dauthers DeltaR
            dauDeltaR = getDauDeltaR(pruned, mother1=35, mother2=36)
            for kCandidateDeltaR in dauDeltaR:
                deltaR[index].Fill(kCandidateDeltaR)        
 


        if TriggerStudy == True:
            minimumValidMuonsForHLTEff = 2
            ValidMuonsForHLTEff = 0
            leadingPtForHLTEff = 0
            for kRecoMuon in muons:
                if kRecoMuon.pt() < 5: continue
                if abs(kRecoMuon.eta())>2.4: continue
                if isTrackType(kRecoMuon, TrackType='STA') == False: continue
                ValidMuonsForHLTEff = ValidMuonsForHLTEff+1

                if kRecoMuon.pt() > leadingPtForHLTEff:
                    leadingPtForHLTEff = kRecoMuon.pt()

            if ValidMuonsForHLTEff >=minimumValidMuonsForHLTEff:
                ptTriggerEffDen[index].Fill(leadingPtForHLTEff)

                # Which fraction of events in the denominator that fullfill the triger
                HLTTriggerNames = event.object().triggerNames(triggerBits)
                for TriggerIndex, kTrigger in enumerate(TriggerFlags):
                    for i in xrange(triggerBits.size()):
                        if triggerBits.accept(i):
                            #print HLTTriggerNames.triggerName(i)
                            if kTrigger == HLTTriggerNames.triggerName(i):
                                ptTriggerEffNum[TriggerIndex][index].Fill(leadingPtForHLTEff)

        # Resolution
        if Resolution ==  True:
            resolutionParam = getResolution(muons, pruned, LxyRange=[10,1000],  LzRange=[0,1000])

            for kCandidate in resolutionParam.getMatchedPtResolution():
                ptResolution[index].Fill(kCandidate)
            for kCandidate in resolutionParam.getMatchedEtaResolution():
                etaResolution[index].Fill(kCandidate)
            for kCandidate in resolutionParam.getMatchedPhiResolution():
                phiResolution[index].Fill(kCandidate)
            for kCandidate in resolutionParam.getMatchedMassResolution():
                massResolution[index].Fill(kCandidate)
            for kCandidate in resolutionParam.getMatchedDeltaRResolution():
                deltaRResolution[index].Fill(kCandidate)

            for kCandidate in resolutionParam.getMatchedEtaResolution():
                deltaEtaResolution[index].Fill(kCandidate)
            for kCandidate in resolutionParam.getMatchedDeltaPhiResolution():
                deltaPhiResolution[index].Fill(kCandidate)

            for kCandidate,jCandidate in zip(resolutionParam.getMatchedDeltaPhiResolution(), resolutionParam.getMatchedPtResolution()):
                if jCandidate >30:
                    deltaPhiResolutionHighMomentum[index].Fill(kCandidate) ## REVISAR ###

            for kCandidate in resolutionParam.getMatchedRecoMassMother1():
                recoMassMother1[index].Fill(kCandidate)
            for kCandidate in resolutionParam.getMatchedRecoMassMother2():
                recoMassMother2[index].Fill(kCandidate)


            for kkCandidate,jjCandidate, hhCandidate in zip(resolutionParam.getMatchedDeltaEtaResolution(), resolutionParam.getMatchedDeltaPhiResolution(), resolutionParam.getMatchedDeltaRResolution()):
                deltaEtadeltaPhiResolution[index].Fill(jjCandidate, kkCandidate)
                
            nMatchedResolution[index].Fill(len(resolutionParam.getMatchedEtaResolution()))
            nReconstructedMothers[index].Fill(len(resolutionParam.getMatchedMassResolution()))
            nReconstructedMother1[index].Fill(len(resolutionParam.getMatchedRecoMassMother1()))
            nReconstructedMother2[index].Fill(len(resolutionParam.getMatchedRecoMassMother2()))

        ## Efficiencies
        if Efficiencies ==  True:

            #Denominators
            for kCandidate in getDauLastCopy(pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[0,1000], LzRange=[0,1000], DrRange = [0, 10]): 
                lxyMu[index].Fill(kCandidate.vertex().Rho())
                lxyMuZoom[index].Fill(kCandidate.vertex().Rho())
                lzMu[index].Fill(abs(kCandidate.vertex().Z()))
                lzMuZoom[index].Fill(kCandidate.vertex().Rho())
                etaMu[index].Fill(kCandidate.eta())

            for kCandidate in getDauLastCopy(pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[0,1000], LzRange=[0,1000], DrRange = [0, 0.5]): 
                lxyMu_eta_X_Pt_10_Lz_X_dR_l0p5[index].Fill(kCandidate.vertex().Rho())
                etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5[index].Fill(kCandidate.eta())
                
            for kCandidate in getDauLastCopy(pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[0,1000], LzRange=[0,1000], DrRange = [0.5, 10.]): 
                lxyMu_eta_X_Pt_10_Lz_X_dR_g0p5[index].Fill(kCandidate.vertex().Rho())
                etaMu_Pt_10_Lxy_X_Lz_X_dR_g0p5[index].Fill(kCandidate.eta())


            for kCandidate in getDauLastCopy(pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[0,10], LzRange=[0,1000], DrRange = [0., 10.]): 
                etaMu_Pt_10_Lxy_l10_Lz_l46_dR_X[index].Fill(kCandidate.eta())

            for kCandidate in getDauLastCopy(pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[10,1000], LzRange=[0,1000], DrRange = [0., 10.]): 
                etaMu_Pt_10_Lxy_g10_Lz_g46_dR_X[index].Fill(kCandidate.eta())


            for kCandidate in getDauLastCopy(pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[10,1000], LzRange=[0,1000], DrRange = [0., 10.]): 
                etaMu_Pt_g50_Lxy_g10_Lz_g46_dR_X[index].Fill(kCandidate.eta())

            for kCandidate in getDauLastCopy(pruned, EtaRange = [0, 2.4],  PtRange=[5,40], LxyRange=[10,1000], LzRange=[0,1000], DrRange = [0., 10.]): 
                etaMu_Pt_g10l50_Lxy_g10_Lz_g46_dR_X[index].Fill(kCandidate.eta())

                
            for kCandidate in getDauLastCopy(pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[10,1000], LzRange=[0,1000], DrRange = [0., 0.5]): 
                etaMu_Pt_10_Lxy_g10_Lz_g46_dR_l0p5[index].Fill(kCandidate.eta())

            for kCandidate in getDauLastCopy(pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[10,1000], LzRange=[0,1000], DrRange = [0.5, 10]): 
                etaMu_Pt_10_Lxy_g10_Lz_g46_dR_g0p5[index].Fill(kCandidate.eta())
                
            #Numerators
            for kMuons in muons:            
                if kMuons.standAloneMuon().isNonnull():
                    if isTrackType(kMuon, TrackType='STA') == False:
                        continue
                    staMuonTrack = kMuons.standAloneMuon()
                
                    genMuonMatched = RecoverGenMuon(staMuonTrack, pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[0,1000], LzRange=[0,1000], DrRange = [0, 10])                
                    if genMuonMatched > 0:
                        lxySTAMatched[index].Fill(genMuonMatched.vertex().Rho())
                        lxyZoomSTAMatched[index].Fill(genMuonMatched.vertex().Rho())
                        lzSTAMatched[index].Fill(abs(genMuonMatched.vertex().Z()))
                        lzZoomSTAMatched[index].Fill(abs(genMuonMatched.vertex().Z()))
                        etaSTAMatched[index].Fill(genMuonMatched.eta())
                
                    genMuonMatched = RecoverGenMuon(staMuonTrack, pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[0,1000], LzRange=[0,1000], DrRange = [0, 0.5])                
                    if genMuonMatched >0:
                        lxyMu_eta_X_Pt_10_Lz_X_dR_l0p5_STAMatched[index].Fill(genMuonMatched.vertex().rho())
                        etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5_STAMatched[index].Fill(genMuonMatched.eta())

                    genMuonMatched = RecoverGenMuon(staMuonTrack, pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[0,1000], LzRange=[0,1000], DrRange = [0.5, 10])                
                    if genMuonMatched >0:
                        lxyMu_eta_X_Pt_10_Lz_X_dR_g0p5_STAMatched[index].Fill(genMuonMatched.vertex().rho())
                        etaMu_Pt_10_Lxy_X_Lz_X_dR_g0p5_STAMatched[index].Fill(genMuonMatched.eta())

                    genMuonMatched = RecoverGenMuon(staMuonTrack, pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[0,10], LzRange=[0,1000], DrRange = [0, 10])                
                    if genMuonMatched >0:
                        etaMu_Pt_10_Lxy_l10_Lz_l46_dR_X_STAMatched[index].Fill(genMuonMatched.eta())

                    genMuonMatched = RecoverGenMuon(staMuonTrack, pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[10,1000], LzRange=[0,1000], DrRange = [0, 10])                
                    if genMuonMatched >0:
                        etaMu_Pt_10_Lxy_g10_Lz_g46_dR_X_STAMatched[index].Fill(genMuonMatched.eta())

                    genMuonMatched = RecoverGenMuon(staMuonTrack, pruned, EtaRange = [0, 2.4],  PtRange=[5,40], LxyRange=[10,1000], LzRange=[0,1000], DrRange = [0, 10])                
                    if genMuonMatched >0:                    
                        etaMu_Pt_g10l50_Lxy_g10_Lz_g46_dR_X_STAMatched[index].Fill(genMuonMatched.eta())

                    genMuonMatched = RecoverGenMuon(staMuonTrack, pruned, EtaRange = [0, 2.4],  PtRange=[40,1000], LxyRange=[10,1000], LzRange=[0,1000], DrRange = [0, 10])                
                    if genMuonMatched >0:                    
                        etaMu_Pt_g50_Lxy_g10_Lz_g46_dR_X_STAMatched[index].Fill(genMuonMatched.eta())

                    genMuonMatched = RecoverGenMuon(staMuonTrack, pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[10,1000], LzRange=[0,1000], DrRange = [0.0, 0.5])                
                    if genMuonMatched >0:
                        etaMu_Pt_10_Lxy_g10_Lz_g46_dR_l0p5_STAMatched[index].Fill(genMuonMatched.eta())

                    genMuonMatched = RecoverGenMuon(staMuonTrack, pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[10,1000], LzRange=[0,1000], DrRange = [0.5, 10])                
                    if genMuonMatched >0:
                        etaMu_Pt_10_Lxy_g10_Lz_g46_dR_g0p5_STAMatched[index].Fill(genMuonMatched.eta())

                if kMuons.muonBestTrack().isNonnull():
                    if isTrackType(kMuon, TrackType='PFTrack') == False:
                        continue
                    pfMuonTrack = kMuons.muonBestTrack()

                    genMuonMatched = RecoverGenMuon(pfMuonTrack, pruned, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[0,1000], LzRange=[0,1000], DrRange = [0, 10])                
                    if genMuonMatched > 0:
                        lxyPFMatched[index].Fill(genMuonMatched.vertex().Rho())
                        lxyZoomPFMatched[index].Fill(genMuonMatched.vertex().Rho())
                        lzPFMatched[index].Fill(abs(genMuonMatched.vertex().Z()))
                        lzZoomPFMatched[index].Fill(abs(genMuonMatched.vertex().Z()))
                        etaPFMatched[index].Fill(genMuonMatched.eta())

##Draw and store the plots
plotsFolder = '/afs/hephy.at/work/a/aescalante/cmssw/SimpleAna/GenPlots/'

#Selected Plots
ShowOnlyMassHistogram = ['M_3GeV_CTau_100mm', 'M_10GeV_CTau_100mm', 'M_50GeV_CTau_100mm']
ShowOnlyLifetimeHistogram = ['M_3GeV_CTau_1mm', 'M_3GeV_CTau_10mm', 'M_3GeV_CTau_100mm', 'M_3GeV_CTau_1000mm']

if GenLevelStudy == True:
    #MotherMasses
    makeSimple1DPlot(mother1Mass, 'mother1Mass', samples, 'X mass [GeV]', 'M_{X} [GeV]', 'norm.a.u', 'mother1Mass', plotsFolder, logy=False, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(mother2Mass, 'mother2Mass', samples, 'X mass [GeV]', 'M_{X} [GeV]', 'norm.a.u', 'mother2Mass', plotsFolder, logy=False, showOnly = ShowOnlyMassHistogram)

    #MotherLorentzBoost
    makeSimple1DPlot(mother1LorentzBoost, 'mother1LorentzBoost', samples, 'E/M_{X}', 'E/M_{X}', 'norm.a.u', 'mother1LorentzBoost', plotsFolder, logy=True, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(mother2LorentzBoost, 'mother2LorentzBoost', samples, 'E/M_{X}', 'E/M_{X}', 'norm.a.u', 'mother2LorentzBoost', plotsFolder, logy=True, showOnly = ShowOnlyMassHistogram)

    #MotherEta
    makeSimple1DPlot(mother1Eta, 'mother1Eta', samples, '#eta_{X}', '#eta_{X}', 'norm.a.u', 'mother1eta', plotsFolder, logy=False, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(mother2Eta, 'mother2Eta', samples, '#eta_{X}', '#eta_{X}', 'norm.a.u', 'mother2eta', plotsFolder, logy=False, showOnly = ShowOnlyMassHistogram)

    #MotherPhi
    makeSimple1DPlot(mother1Phi, 'mother1Phi', samples, '#phi_{X}', '#phi_{X}', 'norm.a.u', 'mother1phi', plotsFolder, logy=False, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(mother1Phi, 'mother2Phi', samples, '#phi_{X}', '#phi_{X}', 'norm.a.u', 'mother2phi', plotsFolder, logy=False, showOnly = ShowOnlyMassHistogram)

    #Mother Pt
    makeSimple1DPlot(ptX, 'ptX', samples, 'X transverse momentum [GeV]', 'p_{T}[GeV]', 'norm.a.u', 'ptX', plotsFolder, logy=True, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(pzX, 'pzX', samples, 'X longitudinal momentum [GeV]', 'p_{Z}[GeV]', 'norm.a.u', 'pzX', plotsFolder, logy=True, showOnly = ShowOnlyMassHistogram)

    ## ctau
    makeSimple1DPlot(ctau, 'ctau', samples, 'Generated c#tau', 'ct [cm]', 'norm.a.u', 'ctau', plotsFolder, logy=True, showOnly = ShowOnlyLifetimeHistogram)
    makeSimple1DPlot(ctau, 'ctau', samples, 'Generated c#tau', 'ct [cm]', 'norm.a.u', 'ctauMass', plotsFolder, logy=True, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(ctauLow, 'ctauLow', samples, 'Generated c#tau', 'ct [cm]', 'norm.a.u', 'ctauMassLow', plotsFolder, logy=True, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(ctauHigh, 'ctauHigh', samples, 'Generated c#tau', 'ct [cm]', 'norm.a.u', 'ctauMassHigh', plotsFolder, logy=True, showOnly = ShowOnlyMassHistogram)

    #DeltaR
    makeSimple1DPlot(deltaR, '#Delta R(#mu,#mu)', samples, 'Generated Fermion deltaR, #Delta R_{ff}', '#Delta R_{ff}', 'norm.a.u', 'DeltaR', plotsFolder, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(deltaR, '#Delta R(#mu,#mu)', samples, 'Generated Fermion deltaR, #Delta R_{ff}', '#Delta R_{ff}', 'norm.a.u', 'DeltaRLifetime', plotsFolder, showOnly = ShowOnlyLifetimeHistogram)

    ## Lxy
    makeSimple1DPlot(lxy, 'lxy', samples, 'Generated Transverse decay length, L_{xy}[cm]', 'L_{xy}[cm]', 'norm.a.u', 'GenLxy', plotsFolder, logy=True, showOnly = ShowOnlyLifetimeHistogram)
    makeSimple1DPlot(lxy, 'lxy', samples, 'Generated Transverse decay length, L_{xy}[cm]', 'L_{xy}[cm]', 'norm.a.u', 'GenLxyMass', plotsFolder, logy=True, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(lxyZoom, 'lxyZoom', samples, 'Generated Transverse decay length, L_{xy}[cm]', 'L_{xy}[cm]', 'norm.a.u', 'GenLxyZoom', plotsFolder, logy=True, showOnly = ShowOnlyMassHistogram)

    #lz
    makeSimple1DPlot(lz, 'lz', samples, 'Generated Longitudinal decay length, L_{z}[cm]', 'L_{z}[cm]', 'norm.a.u', 'GenLz', plotsFolder, logy=True, showOnly = ShowOnlyLifetimeHistogram)
    makeSimple1DPlot(lz, 'lz', samples, 'Generated Longitudinal decay length, L_{z}[cm]', 'L_{z}[cm]', 'norm.a.u', 'GenLzMass', plotsFolder, logy=True, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(lzZoom, 'lzZoom', samples, 'Generated Longitudinal decay length, L_{z}[cm]', 'L_{z}[cm]', 'norm.a.u', 'GenLzZoom', plotsFolder, logy=True, showOnly = ShowOnlyMassHistogram)

    #Momentum daughters
    makeSimple1DPlot(ptDaughter1, 'ptDaughter1', samples, 'Transverse momentum of daughters from mother1', 'p_{T}[GeV]', 'norm.a.u', 'ptDaughter1', plotsFolder, logy=True, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(ptDaughter1, 'ptDaughter2', samples, 'Transverse momentum of daughters from mother2', 'p_{T}[GeV]', 'norm.a.u', 'ptDaughter2', plotsFolder, logy=True, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(ptDaughter1Zoom, 'ptDaughter1Zoom', samples, 'Transverse momentum of daughters from mother1', 'p_{T}[GeV]', 'norm.a.u', 'ptDaughter1Zoom', plotsFolder, logy=False, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(ptDaughter1Zoom, 'ptDaughter2Zoom', samples, 'Transverse momentum of daughters from mother2', 'p_{T}[GeV]', 'norm.a.u', 'ptDaughter2Zoom', plotsFolder, logy=False, showOnly = ShowOnlyMassHistogram)

    #eta daughters
    makeSimple1DPlot(etaDaughter1, 'etaDaughter1', samples, '#eta of daughters from mother1', '#eta', 'norm.a.u', 'etaDaughter1', plotsFolder, logy=False, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(etaDaughter1, 'etaDaughter2', samples, '#eta of daughters from mother2', '#eta', 'norm.a.u', 'etaDaughter2', plotsFolder, logy=False, showOnly = ShowOnlyMassHistogram)
    makeSimple1DPlot(etaDaughterPtCut, 'etaDaughterPtCut', samples, '#eta of daughters if p_{T} > 5 GeV', '#eta if p_{T} > 5 GeV', 'norm.a.u', 'etaDaughterPtCut', plotsFolder, logy=False, showOnly = ShowOnlyMassHistogram)

    ## 2D histograms
    makeSimple2DPlot(lz_lxy, 'lz_lxy', samples, 'Generated L_{z}[cm] vs L_{xy}[cm]', 'L_{z}[cm]', 'L_{xy}[cm]', 'GenLzVsLxy', plotsFolder, showOnly = ShowOnlyLifetimeHistogram)
    makeSimple2DPlot(lz_lxy, 'lz_lxy', samples, 'Generated L_{z}[cm] vs L_{xy}[cm]', 'L_{z}[cm]', 'L_{xy}[cm]', 'GenLzVsLxyMass', plotsFolder, showOnly = ShowOnlyMassHistogram, showReversed = False)
    makeSimple2DPlot(lz_lxyZoom, 'lz_lxyZoom', samples, 'Generated L_{z}[cm] vs L_{xy}[cm]', 'L_{z}[cm]', 'L_{xy}[cm]', 'GenLzVsLxyZoom', plotsFolder, showOnly = ShowOnlyLifetimeHistogram)
    



if TriggerStudy == True:
    for TriggerIndex, kTrigger in enumerate(TriggerFlags):
        makeSimple1DPlot(ptTriggerEffNum[TriggerIndex], "ptTriggerEffNum_"+kTrigger, samples, kTrigger, 'p_{T} if '+kTrigger, 'norm.a.u', 'ptTriggerEffNum_'+kTrigger, plotsFolder, logy=True) 
    makeSimple1DPlot(ptTriggerEffDen, "ptTriggerEffDen", samples, 'p_{T} trigger efficiency den', 'p_{T} if '+kTrigger, 'norm.a.u', 'ptTriggerEffDen', plotsFolder, logy=True, showOnly = ShowOnlyMassHistogram) 

#ShowOnlyForResolution = ['M_3GeV_CTau_100mm', 'M_3GeV_CTau_1000mm', 'M_10GeV_CTau_100mm','M_50GeV_CTau_100mm', 'M_50GeV_CTau_1000mm']
#ShowOnlyForResolution = ['M_3GeV_CTau_100mm', 'M_3GeV_CTau_1000mm', 'M_10GeV_CTau_100mm','M_50GeV_CTau_100mm', 'M_50GeV_CTau_1000mm']
#ShowOnlyForResolution = ['M_10GeV_CTau_1mm','M_10GeV_CTau_10mm', 'M_10GeV_CTau_100mm', 'M_10GeV_CTau_1000mm']
ShowOnlyForResolution = ['M_10GeV_CTau_10mm','M_10GeV_CTau_100mm', 'M_10GeV_CTau_1000mm']
ShowOnlyForResolutionExtreme = ['M_50GeV_CTau_10mm', 'M_50GeV_CTau_100mm', 'M_50GeV_CTau_1000mm']
# Resolution
if Resolution ==  True:
    makeSimple1DPlot(etaResolution, 'etaResolution', samples, '#eta resolution (STA)', '#eta resolution',  'norm.a.u', 'etaResolution', plotsFolder, logy=False,  showOnly =ShowOnlyForResolution)
    makeSimple1DPlot(phiResolution, 'phiResolution', samples, '#phi resolution (STA)', '#phi resolution',  'norm.a.u', 'phiResolution', plotsFolder, logy=False, showOnly =ShowOnlyForResolution)
    makeSimple1DPlot(ptResolution, 'ptResolution', samples, 'p_{T} resolution (STA)', 'p_{T} resolution',  'norm.a.u', 'ptResolution', plotsFolder, logy=False, showOnly =ShowOnlyForResolution)
    makeSimple1DPlot(massResolution, 'massResolution', samples, 'mass resolution (STA)', 'mass resolution',  'norm.a.u', 'massResolution', plotsFolder, logy=False, showOnly =ShowOnlyForResolution)

    makeSimple1DPlot(deltaRResolution, 'deltaRResolution', samples, '#Delta R resolution', '#Delta R resolution',  'norm.a.u', 'deltaRResolution', plotsFolder, logy=False, showOnly =ShowOnlyForResolution)
    makeSimple1DPlot(deltaPhiResolution, 'deltaPhiResolution', samples, '#Delta #phi resolution', '#Delta #phi resolution',  'norm.a.u', 'deltaPhiResolution', plotsFolder, logy=False, showOnly =ShowOnlyForResolution)
    makeSimple1DPlot(deltaPhiResolution, 'deltaPhiResolutionHighMomentum', samples, '#Delta #phi resolution', '#Delta #phi resolution',  'norm.a.u', 'deltaPhiResolutionHighMomentum', plotsFolder, logy=False, showOnly =ShowOnlyForResolution)
    makeSimple1DPlot(deltaEtaResolution, 'deltaEtaResolution', samples, '#Delta #eta resolution', '#Delta #eta resolution',  'norm.a.u', 'deltaEtaResolution', plotsFolder, logy=False, showOnly =ShowOnlyForResolution)

    makeSimple2DPlot(deltaEtadeltaPhiResolution, 'deltaEtadeltaPhiResolution', samples, '#Delta #phi vs #Delta #eta resolution','#Delta #phi resolution', '#Delta #eta resolution', 'deltaPhideltaEtaResolution', plotsFolder, showOnly =ShowOnlyForResolutionExtreme, showReversed = False)

    makeSimple1DPlot(recoMassMother1, 'recoMassMother1', samples, 'Reconstructed Invariant Mass, Mother 1', 'Mother 1, recoMass [GeV]',  'norm.a.u', 'recoMassMother1', plotsFolder, logy=False, showOnly =ShowOnlyForResolution)
    makeSimple1DPlot(recoMassMother2, 'recoMassMother2', samples, 'Reconstructed Invariant Mass, Mother 2', 'Mother 2, recoMass [GeV]',  'norm.a.u', 'recoMassMother2', plotsFolder, logy=False, showOnly =ShowOnlyForResolution)

    makeSimple1DPlot(nMatchedResolution, 'nMatchedResolution', samples, 'Number of Matched muons', 'Number of Matched Muons',  'norm.a.u', 'nMatchedResolution', plotsFolder, logy=False, showOnly =ShowOnlyForResolution)
    makeSimple1DPlot(nReconstructedMothers, 'nReconstructedMothers', samples, 'nReconstructedMothers', 'nReconstructedMothers',  'norm.a.u', 'nReconstructedMothers', plotsFolder, logy=False, showOnly =ShowOnlyForResolution)
    makeSimple1DPlot(nReconstructedMother1, 'nReconstructedMother1', samples, 'nReconstructedMother1', 'nReconstructedMother1',  'norm.a.u', 'nReconstructedMother1', plotsFolder, logy=False, showOnly =ShowOnlyForResolution)
    makeSimple1DPlot(nReconstructedMother2, 'nReconstructedMother2', samples, 'nReconstructedMother2', 'nReconstructedMother2',  'norm.a.u', 'nReconstructedMother2', plotsFolder, logy=False, showOnly =ShowOnlyForResolution)
                
if Efficiencies ==  True:

    #Denominator
    makeSimple1DPlot(lxyMu, 'lxyMu', samples, 'Generated Transverse muon decay length, L_{xy}[cm]', 'L_{xy}[cm]',  'norm.a.u', 'lxyMu', plotsFolder, logy=True)
    makeSimple1DPlot(lxyMuZoom, 'lxyMuZoom', samples, 'Generated Transverse muon decay length, L_{xy}[cm]', 'L_{xy}[cm]',  'norm.a.u', 'lxyMuZoom', plotsFolder, logy=True)
    makeSimple1DPlot(lzMu, 'lzMu', samples, 'Generated Longitudinal muon decay length, L_{z}[cm]', 'L_{z}[cm]',  'norm.a.u', 'lzMu', plotsFolder, logy=True)
    makeSimple1DPlot(lzMuZoom, 'lzMuZoom', samples, 'Generated Longitudinal muon decay length, L_{z}[cm]', 'L_{z}[cm]',  'norm.a.u', 'lzMuZoom', plotsFolder, logy=True)
    makeSimple1DPlot(etaMu, 'etaMu', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu', plotsFolder, logy=False)    
    
    makeSimple1DPlot(lxyMu_eta_X_Pt_10_Lz_X_dR_l0p5, 'lxyMu_eta_X_Pt_10_Lz_X_dR_l0p5', samples, 'Generated Transverse muon decay length', 'L_{xy}[cm]',  'norm.a.u', 'lxyMu_eta_X_Pt_10_Lz_X_dR_l0p5', plotsFolder, logy=True)
    makeSimple1DPlot(lxyMu_eta_X_Pt_10_Lz_X_dR_g0p5, 'lxyMu_eta_X_Pt_10_Lz_X_dR_g0p5', samples, 'Generated Transverse muon decay length', 'L_{xy}[cm]',  'norm.a.u', 'lxyMu_eta_X_Pt_10_Lz_X_dR_g0p5', plotsFolder, logy=True)

    makeSimple1DPlot(etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5, 'etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5', plotsFolder, logy=False)
    makeSimple1DPlot(etaMu_Pt_10_Lxy_X_Lz_X_dR_g0p5, 'etaMu_Pt_10_Lxy_X_Lz_X_dR_g0p5', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_10_Lxy_X_Lz_X_dR_g0p5', plotsFolder, logy=False)

    makeSimple1DPlot(etaMu_Pt_10_Lxy_l10_Lz_l46_dR_X, 'etaMu_Pt_10_Lxy_l10_Lz_l46_dR_X', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_10_Lxy_l10_Lz_l46_dR_X', plotsFolder, logy=False)
    makeSimple1DPlot(etaMu_Pt_10_Lxy_g10_Lz_g46_dR_X, 'etaMu_Pt_10_Lxy_g10_Lz_g46_dR_X', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_10_Lxy_g10_Lz_g46_dR_X', plotsFolder, logy=False)

    makeSimple1DPlot(etaMu_Pt_g50_Lxy_g10_Lz_g46_dR_X, 'etaMu_Pt_g50_Lxy_g10_Lz_g46_dR_X', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_g50_Lxy_g10_Lz_g46_dR_X', plotsFolder, logy=False)
    makeSimple1DPlot(etaMu_Pt_g10l50_Lxy_g10_Lz_g46_dR_X, 'etaMu_Pt_g10l50_Lxy_g10_Lz_g46_dR_X', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_g10l50_Lxy_g10_Lz_g46_dR_X', plotsFolder, logy=False)

    makeSimple1DPlot(etaMu_Pt_10_Lxy_g10_Lz_g46_dR_l0p5, 'etaMu_Pt_10_Lxy_g10_Lz_g46_dR_l0p5', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_10_Lxy_g10_Lz_g46_dR_l0p5', plotsFolder, logy=False)
    makeSimple1DPlot(etaMu_Pt_10_Lxy_g10_Lz_g46_dR_g0p5, 'etaMu_Pt_10_Lxy_g10_Lz_g46_dR_g0p5', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_10_Lxy_g10_Lz_g46_dR_g0p5', plotsFolder, logy=False)

    #STA Numerator
    makeSimple1DPlot(lxySTAMatched, 'lxySTAMatched', samples, 'Generated Transverse muon decay length', 'L_{xy}[cm]',  'norm.a.u', 'lxySTAMatched', plotsFolder, logy=True)
    makeSimple1DPlot(lxyZoomSTAMatched, 'lxyZoomSTAMatched', samples, 'Generated Transverse muon decay length', 'L_{xy}[cm]',  'norm.a.u', 'lxyZoomSTAMatched', plotsFolder, logy=True)
    makeSimple1DPlot(lzSTAMatched, 'lzSTAMatched', samples, 'Generated Longitudinal muon decay length', 'L_{z}[cm]',  'norm.a.u', 'lzSTAMatched', plotsFolder, logy=True)
    makeSimple1DPlot(lzZoomSTAMatched, 'lzZoomSTAMatched', samples, 'Generated Longitudinal muon decay length', 'L_{z}[cm]',  'norm.a.u', 'lzZoomSTAMatched', plotsFolder, logy=True)
    makeSimple1DPlot(etaSTAMatched, 'etaSTAMatched', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaSTAMatched', plotsFolder, logy=False)

    makeSimple1DPlot(lxyMu_eta_X_Pt_10_Lz_X_dR_l0p5_STAMatched, 'lxyMu_eta_X_Pt_10_Lz_X_dR_l0p5_STAMatched', samples, 'Generated Transverse muon decay length', 'L_{xy}[cm]',  'norm.a.u', 'lxyMu_eta_X_Pt_10_Lz_X_dR_l0p5_STAMatched', plotsFolder, logy=True)
    makeSimple1DPlot(lxyMu_eta_X_Pt_10_Lz_X_dR_g0p5_STAMatched, 'lxyMu_eta_X_Pt_10_Lz_X_dR_g0p5_STAMatched', samples, 'Generated Transverse muon decay length', 'L_{xy}[cm]',  'norm.a.u', 'lxyMu_eta_X_Pt_10_Lz_X_dR_g0p5_STAMatched', plotsFolder, logy=True)

    makeSimple1DPlot(etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5_STAMatched, 'etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5_STAMatched', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_10_Lxy_X_Lz_X_dR_l0p5_STAMatched', plotsFolder, logy=False)
    makeSimple1DPlot(etaMu_Pt_10_Lxy_X_Lz_X_dR_g0p5_STAMatched, 'etaMu_Pt_10_Lxy_X_Lz_X_dR_g0p5_STAMatched', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_10_Lxy_X_Lz_X_dR_g0p5_STAMatched', plotsFolder, logy=False)

    makeSimple1DPlot(etaMu_Pt_10_Lxy_l10_Lz_l46_dR_X_STAMatched, 'etaMu_Pt_10_Lxy_l10_Lz_l46_dR_X_STAMatched', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_10_Lxy_l10_Lz_l46_dR_X_STAMatched', plotsFolder, logy=False)
    makeSimple1DPlot(etaMu_Pt_10_Lxy_g10_Lz_g46_dR_X_STAMatched, 'etaMu_Pt_10_Lxy_g10_Lz_g46_dR_X_STAMatched', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_10_Lxy_g10_Lz_g46_dR_X_STAMatched', plotsFolder, logy=False)

    makeSimple1DPlot(etaMu_Pt_g50_Lxy_g10_Lz_g46_dR_X_STAMatched, 'etaMu_Pt_g50_Lxy_g10_Lz_g46_dR_X_STAMatched', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_g50_Lxy_g10_Lz_g46_dR_X_STAMatched', plotsFolder, logy=False)
    makeSimple1DPlot(etaMu_Pt_g10l50_Lxy_g10_Lz_g46_dR_X_STAMatched, 'etaMu_Pt_g10l50_Lxy_g10_Lz_g46_dR_X_STAMatched', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_g10l50_Lxy_g10_Lz_g46_dR_X_STAMatched', plotsFolder, logy=False)

    makeSimple1DPlot(etaMu_Pt_10_Lxy_g10_Lz_g46_dR_l0p5_STAMatched, 'etaMu_Pt_10_Lxy_g10_Lz_g46_dR_l0p5_STAMatched', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_10_Lxy_g10_Lz_g46_dR_l0p5_STAMatched', plotsFolder, logy=False)
    makeSimple1DPlot(etaMu_Pt_10_Lxy_g10_Lz_g46_dR_g0p5_STAMatched, 'etaMu_Pt_10_Lxy_g10_Lz_g46_dR_g0p5_STAMatched', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaMu_Pt_10_Lxy_g10_Lz_g46_dR_g0p5_STAMatched', plotsFolder, logy=False)


    #PF Numerator
    makeSimple1DPlot(lxyPFMatched, 'lxyPFMatched', samples, 'Generated Transverse muon decay length', 'L_{xy}[cm]',  'norm.a.u', 'lxyPFMatched', plotsFolder, logy=True)
    makeSimple1DPlot(lxyZoomPFMatched, 'lxyZoomPFMatched', samples, 'Generated Transverse muon decay length', 'L_{xy}[cm]',  'norm.a.u', 'lxyZoomPFMatched', plotsFolder, logy=True)
    makeSimple1DPlot(lzPFMatched, 'lzPFMatched', samples, 'Generated Longitudinal muon decay length', 'L_{z}[cm]',  'norm.a.u', 'lzPFMatched', plotsFolder, logy=True)
    makeSimple1DPlot(lzZoomPFMatched, 'lzZoomPFMatched', samples, 'Generated Longitudinal muon decay length', 'L_{z}[cm]',  'norm.a.u', 'lzZoomPFMatched', plotsFolder, logy=True)
    makeSimple1DPlot(etaPFMatched, 'etaPFMatched', samples, 'Generated #eta of muon', '#eta',  'norm.a.u', 'etaPFMatched', plotsFolder, logy=False)
