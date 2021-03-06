#!/usr/bin/env python
import ROOT as R
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Analysis.Selections as Selections

#
# voms-proxy-init --voms cms
#python analyzeD0.py --signalpoint 125 20 1300
#

#
# Use dimuon quantities to look at various d0 quantities
# - after common vertex fit "reference" is secondary vertex
#    which is what is used for the gen quantities, allows for an 
#    apples to apples comparison
# - eventually, after ntuples are remade
#    want to redo plots looking at gen quantities extrapolated to the beamspot
#    which gives oranges to oranges for orignal track quantities


#define all combinations of d0s
d0Types = []
for ex in Primitives.ImpactParameter.extrapolationDictionary:
    for vert in Primitives.ImpactParameter.vertexDictionary:
        d0_str ="["+ vert + " " 
        if ex == None:
            d0_str += "FULL"
        else:
            d0_str += ex
        d0_str += "]"
        d0Types.append([vert, ex, d0_str])

print d0Types

def findClosestGenMuon(recoMuon, genMuons):
    closestGen = None
    for genMuon in genMuons:
        deltaR = recoMuon.p4.DeltaR(genMuon.p4)
        if closestGen == None and deltaR < 0.2:
            closestGen = genMuon
        elif closestGen != None and deltaR < recoMuon.p4.DeltaR(closestGen.p4):
            closestGen = genMuon
    return closestGen

#str = '0' or 'z' for d0 or dz
def declareImpactHists(self, str):
    #iterate through all combinations of d0 values
     for i, d_1_t in enumerate(d0Types):
        d_1_str = d_1_t[2]
        self.HistInit('d%s [Gen] - %s'%(str,d_1_str), "[Gen] - %s; d_{%s}[cm]; Counts"%(d_1_str, str),100 ,-5,5)
        self.HistInit('d%s [Gen] vs %s'%(str,d_1_str), "d%s [Gen] vs %s; Gen d_{%s}[cm]; %s d_{%s}[cm]"%(str, d_1_str, str, d_1_str, str), 100, 0, 10, 100, 0, 10)
        #self.HistInit('dz [Gen]-%s'%d0_1_str, "Gen - %s; d_{z}[cm]; Counts"%d0_1_str,100 ,-4,4)
        
        for j, d_2_t in enumerate(d0Types):
            if j <= i: continue
            
            d_2_str = d_2_t[2]
            self.HistInit('d%s %s-%s'%(str,d_1_str, d_2_str), "%s - %s; d_{%s}[cm]; Counts"%(d_1_str, d_2_str, str), 100, -0.015,0.015)
            #self.HistInit('dz %s-%s'%(d0_1_str, d0_2_str), "%s - %s; d_{z}[cm]; Counts"%(d0_1_str, d0_2_str), 100, -0.015,0.015)
            



def declareHistograms(self, Params=None):
    self.HistInit('d0Diff vs radial position', 'd0diffVsRadius; Radius [cm]; d0 [cm]', 100, 0, 400, 100, 0, 20)
    declareImpactHists(self,'0') #make d0 hists
    declareImpactHists(self,'z') #make identical dz hists
    
#str = '0' or 'z' for d0 or dz  
def fillImpactHists(self, mu,closestGen, str):
    for i, d_1_t in enumerate(d0Types):
        d_1_str = d_1_t[2]
        mu_d = 0
        gen_d = 0
        if str == 'z':
            mu_d = mu.dz(d_1_t[0], d_1_t[1])
            if closestGen is not None: gen_d = closestGen.dz()
        elif str == '0':
            mu_d = mu.d0(d_1_t[0], d_1_t[1])
            if closestGen is not None: gen_d = closestGen.d0()
        else:
            print "Error, str %s meaningless"%str
            return
        if closestGen is not None:
            self.HISTS['d%s [Gen] - %s'%(str, d_1_str)].Fill(gen_d - mu_d)
            self.HISTS['d%s [Gen] vs %s'%(str,d_1_str)].Fill(gen_d,mu_d)
        for j, d_2_t in enumerate(d0Types):
            if j <= i: continue
            mu_d2 = 0
            if str == 'z':
                mu_d2 = mu.dz(d_2_t[0],d_2_t[1])
            elif str == '0':
                mu_d2 = mu.d0(d_2_t[0], d_2_t[1])
            else: return
            d_2_str = d_2_t[2]
            self.HISTS['d%s %s-%s'%(str, d_1_str, d_2_str)].Fill(mu_d-mu_d2)
            


def findBestMatches(genReco):
    #thereturn = []
    min_dR = 0.2
    min_reco = None
    min_gen = None
    for gen in genReco:
        for i, reco in enumerate(genReco[gen]):
            dR = reco.p4.DeltaR(gen.p4)
            if dR < min_dR:
                min_dR = dR
                min_reco = reco
                min_gen = gen
    
                
    #didn't find any that match       
    if min_dR == 0.2:
        return []
    #if we did, remove it from the list
    del genReco[min_gen]
    for gen in genReco:
        for i,reco in enumerate(genReco[gen]):
            if reco == min_reco:
                genReco[gen].pop(i)
                break
            
            
    # look in remaining list 
    remainingPairs = findBestMatches(genReco)
    remainingPairs.insert(0, [min_gen,min_reco])
    return remainingPairs
        
            
def matchGenReco(genMuons, recoMuons):
    #make a dictionary of all the differences
    genReco = {}
    for gen in genMuons:
        genReco[gen] = [] # make an array for each dR
        for reco in recoMuons:
            #genReco_dRs[gen].append(reco.p4.DeltaR(gen.p4))
            genReco[gen].append(reco)
            
    #print genReco
    return findBestMatches(genReco)
    
                
            
      
def analyze(self, E, PARAMS=None):
    
    #selections
    if self.TRIGGER:
        if not Selections.passedTrigger(E): return
    
    recoMuons = E.getPrimitives('DSAMUON')
    #Muons = E.getPrimitives('RSAMUON')
    
    #Dimuons = E.getPrimitives("DIMUON")
    if '4Mu' in self.NAME:
         mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
         genMuons = (mu11, mu12, mu21, mu22)
         genMuonPairs = ((mu11, mu12), (mu21, mu22))
    else:
        print "Haven't implemented non-4mu samples"
        return
       
    
    matches = matchGenReco(genMuons, recoMuons)
    for [gen, reco] in matches:
        fillImpactHists(self, reco, gen,'z')
        fillImpactHists(self, reco, gen,'0')
        



#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('EVENT','GEN', 'DSAMUON', 'TRIGGER','DIMUON'),
    )
    analyzer.writeHistograms('roots/d0ComparisonPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
