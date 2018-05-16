# import ROOT in batch mode
import sys
oldargv = sys.argv[:]
sys.argv = [ '-b-' ]
import ROOT

ROOT.gROOT.SetBatch(True) # tell Root not to open canvases
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
#samplesDir = '/afs/cern.ch/user/s/slava/workspace/private/CMSSW_9_3_5/src/Configuration/GenProduction/python/'
samplesDir = 'root://cms-xrd-global.cern.ch//store/user/escalant/'

samples = Sample()

#samples.AddSample(samplesDir+'EXO-RunIIFall17GS_HTo2LongLivedTo4mu_MH-200_MFF-50_CTau-200mm_TuneCUETP8M1_13TeV_pythia8_1.root', 'M_{H}=200 GeV, M_{X}=50 GeV, c#tau=20 cm', '200_50_CTau_20cm', 2)
samples.AddSample(samplesDir+'HTo2LongLivedTo4mu_MH-200_MFF-50_CTau-20mm_TuneCUETP8M1_13TeV_pythia8/crab_HTo2LongLivedTo4mu_MH-200_MFF-50_CTau-20mm_TuneCUETP8M1_13TeV_pythia8_GS-v1/171220_173544/0000/EXO-RunIIFall17GS_HTo2LongLivedTo4mu_MH-200_MFF-50_CTau-20mm_TuneCUETP8M1_13TeV_pythia8_1.root', 'M_{H}=200 GeV, M_{X}=50 GeV, c#tau=2 cm', '200_50_CTau_2cm', 1)
samples.AddSample(samplesDir+'HTo2LongLivedTo4mu_MH-1000_MFF-350_CTau-350mm_TuneCUETP8M1_13TeV_pythia8/crab_HTo2LongLivedTo4mu_MH-1000_MFF-350_CTau-350mm_TuneCUETP8M1_13TeV_pythia8_GS-v1/171220_173154/0000/EXO-RunIIFall17GS_HTo2LongLivedTo4mu_MH-1000_MFF-350_CTau-350mm_TuneCUETP8M1_13TeV_pythia8_1.root', 'M_{H}=1000 GeV, M_{X}=350 GeV, c#tau=35 cm', '1000_350_CTau_35cm', 2)
samples.AddSample(samplesDir+'HTo2LongLivedTo4mu_MH-125_MFF-20_CTau-1300mm_TuneCUETP8M1_13TeV_pythia8/crab_HTo2LongLivedTo4mu_MH-125_MFF-20_CTau-1300mm_TuneCUETP8M1_13TeV_pythia8_GS-v1/171220_173557/0000/EXO-RunIIFall17GS_HTo2LongLivedTo4mu_MH-125_MFF-20_CTau-1300mm_TuneCUETP8M1_13TeV_pythia8_1.root', 'M_{H}=125 GeV, M_{X}=20 GeV, c#tau=130 cm', '125_20_CTau_130cm', 3)
#samples.AddSample(samplesDir+'HTo2LongLivedTo4mu_MH-1000_MFF-20_CTau-20mm_TuneCUETP8M1_13TeV_pythia8/crab_HTo2LongLivedTo4mu_MH-1000_MFF-20_CTau-20mm_TuneCUETP8M1_13TeV_pythia8_GS-v1/171220_173129/0000/EXO-RunIIFall17GS_HTo2LongLivedTo4mu_MH-1000_MFF-20_CTau-20mm_TuneCUETP8M1_13TeV_pythia8_1.root', 'M_{H}=1000 GeV, M_{X}=20 GeV, c#tau=2 cm', '1000_20_CTau_2cm', 1)
#samples.AddSample(samplesDir+'HTo2LongLivedTo4mu_MH-125_MFF-20_CTau-130mm_TuneCUETP8M1_13TeV_pythia8/crab_HTo2LongLivedTo4mu_MH-125_MFF-20_CTau-130mm_TuneCUETP8M1_13TeV_pythia8_GS-v1/171220_173611/0000/EXO-RunIIFall17GS_HTo2LongLivedTo4mu_MH-125_MFF-20_CTau-130mm_TuneCUETP8M1_13TeV_pythia8_1.root', 'M_{H}=125 GeV, M_{X}=20 GeV, c#tau=13 cm', '125_20_CTau_13cm', 3)
#samples.AddSample(samplesDir+'HTo2LongLivedTo4mu_MH-200_MFF-50_CTau-200mm_TuneCUETP8M1_13TeV_pythia8/crab_HTo2LongLivedTo4mu_MH-200_MFF-50_CTau-200mm_TuneCUETP8M1_13TeV_pythia8_GS-v1/171220_173533/0000/EXO-RunIIFall17GS_HTo2LongLivedTo4mu_MH-200_MFF-50_CTau-200mm_TuneCUETP8M1_13TeV_pythia8_1.root', 'M_{H}=200 GeV, M_{X}=50 GeV, c#tau=20 cm', '200_50_CTau_20cm', 2)
#samples.AddSample(samplesDir+'HTo2LongLivedTo4mu_MH-400_MFF-150_CTau-40mm_TuneCUETP8M1_13TeV_pythia8/crab_HTo2LongLivedTo4mu_MH-400_MFF-150_CTau-40mm_TuneCUETP8M1_13TeV_pythia8_GS-v1/171220_173317/0000/EXO-RunIIFall17GS_HTo2LongLivedTo4mu_MH-400_MFF-150_CTau-40mm_TuneCUETP8M1_13TeV_pythia8_1.root', 'M_{H}=400 GeV, M_{X}=150 GeV, c#tau=4 cm', '400_150_CTau_4cm', 1)
#samples.AddSample(samplesDir+'HTo2LongLivedTo4mu_MH-400_MFF-150_CTau-400mm_TuneCUETP8M1_13TeV_pythia8/crab_HTo2LongLivedTo4mu_MH-400_MFF-150_CTau-400mm_TuneCUETP8M1_13TeV_pythia8_GS-v1/171220_173305/0000/EXO-RunIIFall17GS_HTo2LongLivedTo4mu_MH-400_MFF-150_CTau-400mm_TuneCUETP8M1_13TeV_pythia8_1.root', 'M_{H}=400 GeV, M_{X}=150 GeV, c#tau=40 cm', '400_150_CTau_40cm', 2)
#samples.AddSample(samplesDir+'HTo2LongLivedTo4mu_MH-400_MFF-150_CTau-4000mm_TuneCUETP8M1_13TeV_pythia8/crab_HTo2LongLivedTo4mu_MH-400_MFF-150_CTau-4000mm_TuneCUETP8M1_13TeV_pythia8_GS-v1/171220_173254/0000/EXO-RunIIFall17GS_HTo2LongLivedTo4mu_MH-400_MFF-150_CTau-4000mm_TuneCUETP8M1_13TeV_pythia8_1.root', 'M_{H}=400 GeV, M_{X}=150 GeV, c#tau=400 cm', '400_150_CTau_400cm', 3)
#samples.AddSample(samplesDir+'EXO-RunIIFall17GS_HTo2LongLivedTo4mu_MH-125_MFF-20_CTau-1300mm_TuneCUETP8M1_13TeV_pythia8_1.root', 'M_{H}=125, M_{X}=20, c#tau=130cm', '125_20_CTau_130cm', 3)
#samples.AddSample(samplesDir+'EXO-RunIIFall17GS_HTo2LongLivedTo4mu_MH-400_MFF-150_CTau-40mm_TuneCUETP8M1_13TeV_pythia8_1.root', 'M_{H}=400, M_{X}=150, c#tau=4cm', '400_150_CTau_4cm', 1) # last integer is the color

sampleName = samples.GetSampleName()
legendName = samples.GetLegendName()
histName = samples.GetHistName()

# FOR GEN-SIM
handlePruned  = Handle ("std::vector<reco::GenParticle>")
labelPruned = ("genParticles")

# Book histograms
h_massHiggs = createSimple1DPlot("h_massHiggs", "M_{H}", 100, 100., 1100., samples)
h_massX     = createSimple1DPlot("h_massX", "M_{X}", 200, 0., 400., samples)
h_lxy       = createSimple1DPlot("h_lxy", "lxy",   100,  0., 1000., samples)
h_dxyMuons  = createSimple1DPlot("", "h_dxyMuons", 100,  0.,   50., samples)
h_dzMuons   = createSimple1DPlot("", "h_dzMuons",  100,  0.,  100., samples)
h_ptMuons   = createSimple1DPlot("", "h_ptMuons",  100,  0.,  250., samples)
h_etaMuons  = createSimple1DPlot("", "h_etaMuons", 100, -4.,    4., samples)
h_dRMuons   = createSimple1DPlot("", "h_dRMuons",  100,  0.,    3., samples)
h_cosalpha  = createSimple1DPlot("", "h_cosalpha", 100, -1.,    1., samples)
h_alpha     = createSimple1DPlot("", "h_alpha",    100,  0.,   6.3, samples)
h_dphi      = createSimple1DPlot("", "h_dphi",     100,  0.,   6.3, samples)
h_lxyVslz   = createSimple2DPlot("h_lxyVslz", "lxy vs lz", 350, 0, 1000, 200, 0, 700, samples)
h_dxyVsptrel = createSimple2DPlot("h_dxyVsptrel", "dxy vs pTrel", 100, 0., 50., 100, 0., 50., samples)
h_mOverTau = createSimple2DPlot("h_mOverTau","m/tau vs L and E",5, 0., 5.,40,0.,400.,samples)

for index, ksamples in enumerate(sampleName):
    print "SAMPLE: "+ksamples+"\n"
    events = Events(ksamples)
    iphis_total     = 0
    iphis_2mu_lt20  = 0
    iphis_2mu_20_24 = 0
    iphis_2mu_lt24  = 0
    iphis_2mu_gt24  = 0
    for i,event in enumerate(events):   
        print "\n --- Event #", i+1
        event.getByLabel (labelPruned, handlePruned)
        genParticles = handlePruned.product()
        for p in genParticles:
            if p.isHardProcess():
                tellMeMore(p)
                if abs(p.pdgId()) == 35: #Plotting something from the Higgs
                    h_massHiggs[index].Fill(p.mass())
                if abs(p.pdgId()) == 6000113: #Plotting something from the X
                    h_massX[index].Fill(p.mass())

                    daus = p.daughterRefVector()
                    if len(daus) != 2:
                        print "+++ phi decayed into", len(daus), "particles +++"
                    else:
                        if (daus[0].pdgId() == 13 and daus[1].pdgId() == -13) or (daus[0].pdgId() == -13 and daus[1].pdgId() == 13):
                            fsmuons = findFinalStateMuons(daus)
                            if len(fsmuons) != 2:
                                print "+++ A pair of final state muons is not found +++"
                                break;

                            print "pTs of final state muons:", round(fsmuons[0].pt(),2), round(fsmuons[1].pt(),2)                            
                            dimu_px = fsmuons[0].px() + fsmuons[1].px()
                            dimu_py = fsmuons[0].py() + fsmuons[1].py()
                            dimu_pt = sqrt(dimu_px**2 + dimu_py**2)
                            for muon in fsmuons:
                                h_ptMuons[index].Fill(muon.pt())
                                h_etaMuons[index].Fill(muon.eta())

                                # dxy and dz w.r.t. (0; 0)
                                dxy = (-muon.vx()*muon.py() + muon.vy()*muon.px())/muon.pt()
                                dz = muon.vz() - (muon.vx()*muon.px() + muon.vy()*muon.py())/muon.pt()*muon.pz()/muon.pt()
                                h_dxyMuons[index].Fill(fabs(dxy))
                                h_dzMuons[index].Fill(fabs(dz))

                                # dxy vs relative pT of a muon in a pair
                                px_rel = muon.px() - dimu_px
                                py_rel = muon.py() - dimu_py
                                pt_rel = sqrt(px_rel**2 + py_rel**2)
                                h_dxyVsptrel[index].Fill(pt_rel, fabs(dxy))

                            # delta R between two muons in a pair
                            dphi = fabs(fsmuons[0].phi() - fsmuons[1].phi())
                            deta = fabs(fsmuons[0].eta() - fsmuons[1].eta())
                            dR = sqrt(dphi**2 + deta**2)
                            h_dRMuons[index].Fill(dR)

                            if( fsmuons[0].vertex().rho() != 0.): h_mOverTau[index].Fill(fsmuons[0].vertex().rho(),fsmuons[1].p() +fsmuons[0].p(),2.*(fsmuons[0].p()+fsmuons[1].p())/fsmuons[0].vertex().rho()) 


                            # count events in various acceptance regions

                            if (fsmuons[0].pt() > 20 and fsmuons[1].pt() > 20):
                                iphis_total += 1
                                if (fabs(fsmuons[0].eta()) < 2.0 and fabs(fsmuons[1].eta()) < 2.0):
                                    iphis_2mu_lt20 += 1
                                elif (fabs(fsmuons[0].eta()) < 2.4 and fabs(fsmuons[1].eta()) < 2.4):
                                    iphis_2mu_lt24 += 1
                                    print " would pass |eta|<2.4 trigger: eta1 = ", fsmuons[0].eta(), "eta2 = ", fsmuons[1].eta()
                                else:
                                    iphis_2mu_gt24 += 1
                                    print " out of acceptance: eta1 = ", fsmuons[0].eta(), "eta2 = ", fsmuons[1].eta()
                                if ((fabs(fsmuons[0].eta()) < 2.0 and fabs(fsmuons[1].eta()) > 2.0 and fabs(fsmuons[1].eta()) < 2.4) or ((fabs(fsmuons[1].eta()) < 2.0 and fabs(fsmuons[0].eta()) > 2.0 and fabs(fsmuons[0].eta()) < 2.4))):
                                    iphis_2mu_20_24 += 1
                                    print " would fit 2.0-2.4 trigger: eta1 = ", fsmuons[0].eta(), "eta2 = ", fsmuons[1].eta()

                            # 3D opening angle between two muons in a pair
                            cosalpha = (fsmuons[0].px()*fsmuons[1].px() + fsmuons[0].py()*fsmuons[1].py() + fsmuons[0].pz()*fsmuons[1].pz())/fsmuons[0].p()/fsmuons[1].p()
                            alpha = acos(cosalpha)
                            h_cosalpha[index].Fill(cosalpha)
                            h_alpha[index].Fill(alpha)

                            # Lxy and delta(phi)
                            if fabs(fsmuons[0].vx() - fsmuons[1].vx()) > 1e-3 or fabs(fsmuons[0].vy() - fsmuons[1].vy()) > 1e-3:
                                print "+++ two daughter muons are not produced at the same vertex +++"
                            else:
                                cosdphi = (fsmuons[0].vx()*dimu_px + fsmuons[0].vy()*dimu_py)/fsmuons[0].vertex().rho()/dimu_pt
                                dphi = acos(cosdphi)
                                print "dimu_pt =", dimu_pt, "cos(dphi) =", cosdphi, "dphi =", dphi
                                h_lxy[index].Fill(fsmuons[0].vertex().rho())
                                h_lxyVslz[index].Fill(fabs(fsmuons[0].vertex().Z()), fsmuons[0].vertex().rho())
                                h_dphi[index].Fill(dphi)
                        else:
                            print "+++ X did not decay into two muons +++"
                            print "+++ id1:", daus[0].pdgId(), "id2:", daus[1].pdgId()


    print "Sample: "+ksamples+"\n phis total:", iphis_total
    print "\n both mus with |eta| < 2.0:", iphis_2mu_lt20
    print "\n 1 mu has |eta| < 2.0; 1 mu has |eta| < 2.4:", iphis_2mu_20_24
    print "\n at least 1 mu has |eta| > 2.0 and both mus have |eta| < 2.4:", iphis_2mu_lt24
    print "\n at least 1 mu has |eta| > 2.4: ", iphis_2mu_gt24

#                if abs(p.pdgId()) == 13: #Plotting something from the displaced muons
#                    h_lxy[index].Fill(p.vertex().rho())
#                    h_lxyVslz[index].Fill(fabs(p.vertex().Z()), p.vertex().rho())
#                    h_ptMuons[index].Fill(p.pt())
#                    h_etaMuons[index].Fill(p.eta())

#    h_lxy[index].Fit("expo", "L")


#plotsFolder = '/afs/hephy.at/work/a/aescalante/cmssw/SimpleGen/plots/'
plotsFolder = './plots/'
#makeSimple1DPlot(var, canvas, samples, title, xtitle, ytitle, output, folder, logy=False, showOnly = []):

makeSimple1DPlot(h_massHiggs, 'h_massHiggs', samples, '', 'M_{Higgs}', 'norm.a.u', 'h_massHiggs', plotsFolder, logy=False)
makeSimple1DPlot(h_massX, 'h_massX', samples, '', 'M_{X}', 'norm.a.u', 'h_massX', plotsFolder, logy=False)
makeSimple1DPlot(h_lxy, 'h_lxy', samples, '', 'L_{xy}[cm]', 'norm.a.u', 'h_lxy', plotsFolder, logy=True)
makeSimple2DPlot(h_lxyVslz, 'h_lxyVslz', samples, 'Generated L_{xy}[cm] vs L_{z}[cm]', 'L_{z}[cm]', 'L_{xy}[cm]', 'h_LxyVsLz', plotsFolder)
makeSimple1DPlot(h_ptMuons, 'h_ptMuons', samples, '', 'pT [GeV]', '', 'h_ptMuons', plotsFolder, logy=False)
makeSimple1DPlot(h_etaMuons, 'h_etaMuons', samples, '', 'eta', '', 'h_etaMuons', plotsFolder, logy=False)
makeSimple1DPlot(h_dxyMuons, 'h_dxyMuons', samples, '', 'dxy [cm]', '', 'h_dxyMuons', plotsFolder, logy=False)
makeSimple1DPlot(h_dzMuons,  'h_dzMuons',  samples, '', 'dz [cm]',  '', 'h_dzMuons', plotsFolder, logy=False)
makeSimple2DPlot(h_dxyVsptrel, 'h_dxyVsptrel', samples, 'dxy vs pT(mu,X)', 'pT(mu,X) [GeV]', 'dxy[cm]', 'h_dxyVsptrel', plotsFolder)
makeSimple1DPlot(h_dRMuons,  'h_dRMuons',  samples, '', 'dR',         '', 'h_dRMuons',  plotsFolder, logy=False)
makeSimple1DPlot(h_cosalpha, 'h_cosalpha', samples, '', 'cos(alpha)', '', 'h_cosalpha', plotsFolder, logy=False)
makeSimple1DPlot(h_alpha,    'h_alpha',    samples, '', 'alpha',      '', 'h_alpha',    plotsFolder, logy=False)
makeSimple1DPlot(h_dphi,     'h_dphi',     samples, '', 'dphi',       '', 'h_dphi',     plotsFolder, logy=True)
makeSimple2DPlot(h_mOverTau, 'h_mOverTau', samples,'', 'm/tau', 'L', 'E', 'h_mOverTau', plotsFolder)
