from math import *
from RecoUtils import *
from myMathUtils import *
from ResolutionUtils import *

def tellMeMore(p):
    pId = p.pdgId()
    print "\n id =", pId, "mass = ", round(p.mass(), 2), "pT = ", round(p.pt(),2)
    if pId != 21:
        print "  N mothers: ", p.numberOfMothers(), "N daugthers: ", p.numberOfDaughters()
        mom = p.mother()
        while (mom != 0 and mom.pdgId() == pId):
            mom = mom.mother()
        print "  mother id: ", mom.pdgId(), "mother mass:", round(mom.mass(),2)

        findDaughters(p)


# Finds the last muons in a decay chain of a given list of muons.
def findFinalStateMuons(prunedParticles):
    fsmuons = []

    for mu in prunedParticles:
        muon = mu
        print "Last copy?", muon.isLastCopy()
        while (muon.isLastCopy() == False):
            for dau in muon.daughterRefVector():
                # Assume that there is always only one muon in the decay chain
                if dau.pdgId() == muon.pdgId():
                    muon = dau;
                    break;

        if muon.isLastCopy() == False:
            "+++ Final state muon is not found +++"
            break;
        else:
            fsmuons.append(muon)

    return fsmuons


def findDaughters(genParticle):
    daughters = []

    pId = genParticle.pdgId()
    ndau = genParticle.numberOfDaughters()

    daus = genParticle.daughterRefVector()
    for dau1 in daus:
        dau = dau1
        while (dau.pdgId() == pId):
            print "dau pdgId", dau.pdgId(), dau.numberOfDaughters(), round(dau.mass(),2), round(dau.pt(),2)
            if (dau.numberOfDaughters() > 0):
                dau = dau.daughter(0)
            else:
                break
        if (dau.pdgId() != pId):
            daughters.append(dau)
            print "Daughter found: id = ", dau.pdgId(), "mass = ", round(dau.mass(), 2), "pT = ", round(dau.pt(),2)

    return daughters
        

def getDaughters(prunedParticles, mother =35):
    daughtersMother = []
    for p in prunedParticles:
        if abs(p.pdgId()) > 0 and abs(p.pdgId()) < 1000:
            if p.isHardProcess():
                if p.mother(0).pdgId() == mother:
                    daughtersMother.append(p)
                    
    if len(daughtersMother) == 2:        
        return daughtersMother

    else:
        print "WTF!! \n"

def getMothers(prunedParticles, mother1 =-1, mother2=-1):
    mothers = []
    for p in prunedParticles:
        if abs(p.pdgId()) > 0 and abs(p.pdgId()) < 1000:
            if p.isHardProcess():
                tellMeMore(p)
                if p.pdgId() == mother1 or p.pdgId() == mother2:

                    #Check if mother is already in mothers.
                    isNewMother = True
                    for kCandidate in mothers:
                        if kCandidate.pdgId() == p.pdgId():
                            isNewMother = False

                    if isNewMother == True:
                        mothers.append(p)                                    
                    
    if len(mothers) == 1 or len(mothers) == 2:        
        return mothers
    else:
        print "WTF!! \n"


def getMotherMass(prunedParticles, mother):
    mothers = getMothers(prunedParticles, mother)
    return mothers[0].mass()

def getMotherLorentzBoost(prunedParticles, mother):
    mothers = getMothers(prunedParticles, mother)
    
    E_Over_m = mothers[0].energy()/mothers[0].mass()
    gammaV2 = sqrt( mothers[0].pt()*mothers[0].pt()+mothers[0].pz()*mothers[0].pz()+mothers[0].mass()*mothers[0].mass() )/mothers[0].mass()
    
    #print "E_Over_m = "+str(E_Over_m)+"  ,  "+"gammaV2 "+str(gammaV2)
    return mothers[0].energy()/mothers[0].mass()

def getMotherEtaPhi(prunedParticles, mother):
    mothers = getMothers(prunedParticles, mother)
    return mothers[0].eta(), mothers[0].phi()
    
#    dau1 = daughtersMother[0]
#    dau2 = daughtersMother[1]
#    print dau1.phi(), dau2.phi()
#    print deltaPhi(dau1, dau2)
    #    print dau1.pt()*dau2.pt()
#    print cosh(dau1.eta()-dau2.eta())-cos(deltaPhi(dau1, dau2))
#    zMass2 = 2*dau1.pt()*dau2.pt()*(cosh(dau1.eta()-dau2.eta())-cos(deltaPhi(dau1, dau2)))
#    if sqrt(zMass2)<51:
#        print sqrt(zMass2)
#    return sqrt(zMass2)


#def getMotherMass(prunedParticles, mother1=35, mother2=36):
#    mother1Mass = []
#    mother2Mass = [] 
#    for p in :
#        if abs(p.pdgId()) > 0 and abs(p.pdgId()) < 1000:
#            if p.isHardProcess():
#                if p.mother(0).pdgId() == mother1:
#                    mother1Mass.append(p.mother(0).mass())
#                if p.mother(0).pdgId() == mother2:
#                    mother2Mass.append(p.mother(0).mass())
#
#    return mother1Mass, mother2Mass


def getMotherMomentum(prunedParticles, mother1=35, mother2=36):
    ptMother = []
    pzMother = [] 
    for p in prunedParticles:
        if abs(p.pdgId()) > 0 and abs(p.pdgId()) < 1000:
            if p.isHardProcess():
                if p.mother(0).pdgId() == mother1 or p.mother(0).pdgId() == mother2:
                    ptMother.append(p.mother(0).pt())
                    pzMother.append(p.mother(0).pz())
                    
    return ptMother, pzMother

def getGenDaughters(prunedParticles, mother1=35, mother2=36, daughter1=-1, daughter2=-1, Inclusive = False):
    daughters = []
    for p in prunedParticles:
        if abs(p.pdgId()) > 0 and abs(p.pdgId()) < 1000:
            if p.isHardProcess():

                if Inclusive == False:
                    if (abs(p.pdgId()) == daughter1 or abs(p.pdgId()) == daughter2) and abs(p.eta())<2.4:
                        daughters.append(p)

                if Inclusive == True:
                    if (abs(p.pdgId()) == daughter1 or abs(p.pdgId()) == daughter2):
                        daughters.append(p)

                    
    return daughters



def getDauDeltaR(prunedParticles, mother1=35, mother2=36):
    dauDeltaR = []
    dau1 = []
    dau2 = []

    for p in prunedParticles:
        if abs(p.pdgId()) > 0 and abs(p.pdgId()) < 1000:
            if p.isHardProcess():
                if p.mother(0).pdgId() == mother1 and p.mother(0).pt()< 50:
                    dau1.append(p)                    
                if p.mother(0).pdgId() == mother2 and p.mother(0).pt()< 50:
                    dau2.append(p)                    


    if len(dau1)>0:    
        dauDeltaR.append(deltaR(dau1[0], dau1[1]))

    if len(dau2)>0:
        dauDeltaR.append(deltaR(dau2[0], dau2[1]))
#    print dauDeltaR
    return dauDeltaR


def getDauLastCopy(prunedParticles, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[0,1000], LzRange=[0,1000], DrRange = [0, 10] ):

    minDeltaRGenThreshold = 10
    minDeltaRMatchedThreshold = 0.20
    DauPdgId = 13
    
    dauLastCopies = [] 

    for p in prunedParticles:        
        if abs(p.pdgId()) != DauPdgId or p.isLastCopy()!= True:
            continue
        if abs(p.eta()) < EtaRange[0] or abs(p.eta()) > EtaRange[1]:
            continue
        if abs(p.pt()) < PtRange[0] or abs(p.pt())> PtRange[1]:            
            continue
        if abs(p.vertex().Rho()) < LxyRange[0] or abs(p.vertex().Rho()) > LxyRange[1]:            
            continue
        if abs(p.vertex().Z()) < LzRange[0] or abs(p.vertex().Z()) > LzRange[1]:            
            continue

        for k in prunedParticles:
            if k.pdgId() == -p.pdgId() and k.isLastCopy():
                if deltaR(p, k) < minDeltaRGenThreshold:
                    minDeltaRGenThreshold = deltaR(p, k)

        if minDeltaRGenThreshold < DrRange[0] or minDeltaRGenThreshold > DrRange[1]:
            continue

        dauLastCopies.append(p)

    return dauLastCopies


def motherParticle(p):
    return p.mother(0)

def getTrueMother(p):
    motherPdgId = p.pdgId()
    while p.mother(0).pdgId() == motherPdgId:
        p = motherParticle(p)
        motherPdgId = p.pdgId()
    return p.mother(0)



    

def getResolution(RecoMuon, prunedParticles, EtaRange = [0, 2.4],  PtRange=[5,1000], LxyRange=[0,1000], LzRange=[0,1000], DrRange = [0.5, 10], TrackType = 'STA'):
    minDeltaRGenThreshold = 10
    minDeltaRMatchedThreshold = 0.30
    DauPdgId = 13
    verbose = False

    resolutionParam = ResolutionParam()
    
    if verbose == True: print 'Looking for Gen Muon'
    if verbose == True: print EtaRange, PtRange, LxyRange, LzRange, DrRange
    if verbose == True: print RecoMuon.pt(), RecoMuon.eta(), RecoMuon.phi()

    pairReco = []
    pairGen = []
    
    for kRecoMuon in RecoMuon:
        matchedGenMu=[]
        if isTrackType(kRecoMuon, TrackType) == False:
            continue

        if TrackType == 'STA':
            RecoTrack = kRecoMuon.standAloneMuon()
        if TrackType == 'PFTrack':
            RecoTrack = kRecoMuon.muonBestTrack()
                        
        for p in prunedParticles:
            if abs(p.pdgId()) != DauPdgId or p.isLastCopy()!= True:
                continue
            if abs(p.eta()) < EtaRange[0] or abs(p.eta()) > EtaRange[1]:
                continue
            if abs(p.pt()) < PtRange[0] or abs(p.pt())> PtRange[1]:            
                continue
            if abs(p.vertex().Rho()) < LxyRange[0] or abs(p.vertex().Rho()) > LxyRange[1]:            
                continue
            if abs(p.vertex().Z()) < LzRange[0] or abs(p.vertex().Z()) > LzRange[1]:            
                continue
            if p.charge() != RecoTrack.charge():            
                continue
        
            for k in prunedParticles:
                if k.pdgId() == -p.pdgId() and k.isLastCopy():
                    if deltaR(p, k) < minDeltaRGenThreshold:
                        minDeltaRGenThreshold = deltaR(p, k)

            if verbose == True: print "Delta R "+str(minDeltaRGenThreshold)
            if minDeltaRGenThreshold < DrRange[0] or minDeltaRGenThreshold > DrRange[1]:
                continue

            if verbose == True: print "#PdgId : %s  status: %s  pt : %.4s  eta : %.4s   phi : %.4s  " %(p.pdgId(),p.status(),p.pt(),p.eta(),p.phi())
            if verbose == True: print "    -> Delta R %f"%(deltaR(RecoTrack, p))

            if deltaR(RecoTrack, p) <minDeltaRMatchedThreshold:
                minDeltaR = deltaR(RecoTrack, p)
                matchedGenMu.append(p)
                    

        if len(matchedGenMu) > 0:
            pairReco.append(RecoTrack)
            pairGen.append(matchedGenMu[-1])
                
    if verbose == True: print 'found matched muons '+str(len(pairReco))


    if len(pairGen)> 1:
#        print 'test ----- nmuons '+str(len(pairGen))
        for kIndex in range(0, len(pairGen)):
            for jIndex in range(kIndex, len(pairGen)):
                if verbose == True: print kIndex, jIndex
                if getTrueMother(pairGen[kIndex]).pdgId() == getTrueMother(pairGen[jIndex]).pdgId() and pairGen[kIndex].pdgId() !=  pairGen[jIndex].pdgId():
                    if verbose == True: print  kIndex, pairGen[kIndex].charge(), pairGen[kIndex].pdgId(), getTrueMother(pairGen[kIndex]).pdgId(), pairGen[kIndex].eta(), pairGen[kIndex].phi()
                    if verbose == True: print  jIndex, pairGen[jIndex].charge(), pairGen[jIndex].pdgId(), getTrueMother(pairGen[jIndex]).pdgId(), pairGen[jIndex].eta(), pairGen[jIndex].phi()

                    recoMass = sqrt( 2*pairReco[jIndex].pt()*pairReco[kIndex].pt()*(cosh(pairReco[jIndex].eta()-pairReco[kIndex].eta())-cos(deltaPhi(pairReco[jIndex], pairReco[kIndex]))))
                    recoDeltaR = deltaR(pairReco[jIndex], pairReco[kIndex])

                    if getTrueMother(pairGen[kIndex]).pdgId() == getTrueMother(pairGen[jIndex]).pdgId() == 35:
                        resolutionParam.matchedRecoMassMother1.append(recoMass)
                    if getTrueMother(pairGen[kIndex]).pdgId() == getTrueMother(pairGen[jIndex]).pdgId() == 36:                        
                        resolutionParam.matchedRecoMassMother2.append(recoMass)

                    genMass = getTrueMother(pairGen[kIndex]).mass()                                                            
                    resolutionParam.matchedMassResolution.append((recoMass-genMass)/genMass)

                    deltaPhiReco = deltaPhi(pairReco[jIndex],pairReco[kIndex])
                    deltaEtaReco = abs(pairReco[jIndex].eta()-pairReco[kIndex].eta())

                    deltaPhiGen = deltaPhi(pairGen[jIndex],pairGen[kIndex])
                    deltaEtaGen = abs(pairGen[jIndex].eta()-pairGen[kIndex].eta())

                    genDeltaR = deltaR(pairGen[jIndex], pairGen[kIndex])
                    if genDeltaR > 0.5:
                        resolutionParam.matchedDeltaPhiResolution.append(deltaPhiReco-deltaPhiGen)
                        resolutionParam.matchedDeltaEtaResolution.append(deltaEtaReco-deltaEtaGen)                        
                        resolutionParam.matchedDeltaRResolution.append(recoDeltaR-genDeltaR)

                    if recoDeltaR-genDeltaR < 0.2 and verbose == True:
                        print '-----------mother %s ---------' % pairGen[kIndex].pdgId()
                        print 'RECO: pt1:%s pt2:%s eta1: %s, eta2: %s , phi1: %s, phi2: %s, mass: %s deltaR: %s '%  (pairReco[jIndex].pt(), pairReco[kIndex].pt(), pairReco[jIndex].eta(), pairReco[kIndex].eta(), pairReco[jIndex].phi(), pairReco[kIndex].phi(), recoMass, recoDeltaR)
                        print 'GENE: pt1:%s pt2:%s eta1: %s, eta2: %s , phi1: %s, phi2: %s, mass: %s, deltaR: %s, lxy: %s, lz:%s '%  (pairGen[jIndex].pt(), pairGen[kIndex].pt(), pairGen[jIndex].eta(), pairGen[kIndex].eta(), pairGen[jIndex].phi(), pairGen[kIndex].phi(), genMass, genDeltaR, pairGen[kIndex].vertex().Rho(), pairGen[kIndex].vertex().Z())
                        #print 'Global:    Deta-Rec: %s, DPhi-Rec: %s' %  (pairReco[jIndex].eta()-pairReco[kIndex].eta(), deltaPhi(pairReco[jIndex],pairReco[kIndex]) )
                        #print 'Global:    Deta-Rec: %s, DPhi-Rec: %s' %  (pairGen[jIndex].eta()-pairGen[kIndex].eta(), deltaPhi(pairGen[jIndex],pairGen[kIndex]) )
                        #print 'Global:    Diff: %s, Diff: %s' %  ( pairReco[jIndex].eta()-pairReco[kIndex].eta()-pairGen[jIndex].eta()+pairGen[kIndex].eta(), deltaPhi(pairGen[jIndex],pairGen[kIndex])- deltaPhi(pairReco[jIndex],pairReco[kIndex]) )
                        print 'Global:    Deta-Rec: %s, DPhi-Rec: %s' %  (deltaEtaReco, deltaPhiReco )
                        print 'Global:    Deta-Rec: %s, DPhi-Rec: %s' %  (deltaEtaGen, deltaPhiGen )
                        print 'Global:    Diff: %s, Diff: %s DeltaR %s' %  ( deltaEtaReco-deltaEtaGen, deltaPhiReco-deltaPhiGen, recoDeltaR-genDeltaR)
                        
                    
                    
    for kMatchedReco, kMatchedGen in zip(pairReco, pairGen):
        if len(pairGen) >0:
            resolutionParam.matchedEtaResolution.append(kMatchedReco.eta()-kMatchedGen.eta())
            resolutionParam.matchedPhiResolution.append(kMatchedReco.phi()-kMatchedGen.phi())
            resolutionParam.matchedPtResolution.append((kMatchedReco.pt()-kMatchedGen.pt())/kMatchedGen.pt())
                
    return resolutionParam 
