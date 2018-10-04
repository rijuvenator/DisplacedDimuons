#!/usr/bin/env python
import ROOT as R
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Analysis.Selections as Selections

#
# voms-proxy-init --voms cms
#python analyze<>.py --signalpoint 125 20 1300
#


def declareResolutionHists(self,name, maxstats=4):
    
    for i in range(1, maxstats+1):
        self.HistInit('%s_%istat'%(name, i), '%s_%istat; Muon Station Hits; Count'%(name,i), 60, 0, 60)
    if maxstats > 4:
        self.HistInit('%s_5+stat'%name, '%s_4+stat; Muon Station Hits; Count'%name, 60, 0, 60)
 
def declareHistograms(self, Params=None):
    
    declareResolutionHists(self,'csc')
    declareResolutionHists(self,'dt')
    declareResolutionHists(self,'csc&dt',8)
  
    

def findBestMatches(genReco):
    min_dR = 0.2
    min_reco = None
    min_gen = None
    for gen in genReco:
        for reco in genReco[gen]:
            dR = reco.p4.DeltaR(gen.p4)
            if dR < min_dR:
                min_dR = dR
                min_reco = reco
                min_gen = gen
    
                
    #didn't find any that match       
    if min_dR == 0.2:
        return []
    #if we did, remove it from the list
    genReco.pop(min_gen)
    for gen in genReco:
        for i,reco in enumerate(genReco[gen]):
            if reco == min_reco:
                genReco[gen].pop(i)
                break
            
            
    # look in remaining list 
    remainingPairs = findBestMatches(genReco)
    remainingPairs.append([min_gen,min_reco])
    return remainingPairs
        
            
def matchGenReco(genMuons, recoMuons):
    #make a dictionary of all the differences
    genReco = {}
    for gen in genMuons:
        genReco[gen] = [] # make an array for each dR
        for reco in recoMuons:
            genReco[gen].append(reco)
            
    return reversed(findBestMatches(genReco))
    

def analyze(self, E, PARAMS=None):
    
    dsaMuons = E.getPrimitives('DSAMUON')
    
    recoMuons = []
    diMuons = E.getPrimitives('DIMUON')
    for dimuon in diMuons:
        if(dimuon.Lxy() < 330):
            recoMuons.append(dimuon.mu1)
            recoMuons.append(dimuon.mu2)
    #recoMuons = dsaMuons # to look at un-vertex-fit muons
    
    if(len(recoMuons) == 0): return
    
    
    if '4Mu' in self.NAME:
        mu11, mu12, mu21, mu22, X1, X2, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu11, mu12, mu21, mu22)
        genMuonPairs = ((mu11, mu12), (mu21, mu22))
    elif '2Mu2J' in self.NAME:
        mu1, mu2, j1, j2, X, XP, H, P, extramu = E.getPrimitives('GEN')
        genMuons = (mu1, mu2)
    else:
        print "Haven't implemented these samples"
        return
    
    #selections
    if self.TRIGGER:
        if not Selections.passedTrigger(E): return
        
        
    matches = matchGenReco(genMuons, recoMuons)
    for [gen, reco] in matches:  
        ndtstats = dsaMuons[reco.idx].nDTStations
        ndthits = dsaMuons[reco.idx].nDTHits
        ncscstats = dsaMuons[reco.idx].nCSCStations
        ncschits = dsaMuons[reco.idx].nCSCHits
        if ncscstats == 0:
            if ndtstats != 0:
                if gen.pt != 0: self.HISTS['dt_%istat'%ndtstats].Fill(ndthits)
        else:
            if ndtstats == 0:
                if gen.pt != 0: self.HISTS['csc_%istat'%ncscstats].Fill(ncschits)
            else: # csc !=0 & dt !=0
                if gen.pt != 0: 
                    nstat = ndtstats+ncscstats
                    nhits = ndthits+ncschits
                    if nstat > 4:
                        self.HISTS['csc&dt_5+stat'].Fill(nhits)
                    else:
                        self.HISTS['csc&dt_%istat'%(nstat)].Fill(nhits)
    

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        #BRANCHKEYS  = ('DSAMUON'),
        BRANCHKEYS  = ('DSAMUON', 'GEN','TRIGGER', 'DIMUON'),
    )
    analyzer.writeHistograms('roots/nHitsComparisonPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
