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
        self.HistInit('%s_%istat'%(name, i), '%s_%istat; (DSA P_{T} - Gen P_{T})/Gen P_{T}; Count'%(name,i), 50, -1, 5)
        self.HistInit('%s_%istat_gauss'%(name, i), '%s_%istat_gauss; (DSA(q/p_{T}) - Gen(q/p_{T}))/Gen(q/p_{T}); Count'%(name,i), 50, -5, 5)
    if maxstats > 4:
        self.HistInit('%s_5+stat'%name, '%s_4+stat; (DSA P_{T} - Gen P_{T})/Gen P_{T}; Count'%name, 50, -1, 5)
        self.HistInit('%s_5+stat_gauss'%name, '%s_4+stat_gauss; (DSA(q/p_{T}) - Gen(q/p_{T}))/Gen(q/p_{T}); Count'%name, 50, -5, 5)
     
    self.HistInit('chi2/ndf vs n%sStats'%name,'chi2/ndf vs n%sStats; Stations; #Chi^{2} / ndf'%name, 4, 1,5, 50, 0,3)
    self.HistInit('dPt/Pt vs n%sStats'%name, 'dPt/Pt vs n%sStats; Stations; #sigma_{Pt}/Pt'%name, 4,1,5, 50, 0, 1)

def declareHistograms(self, Params=None):
    
    declareResolutionHists(self,'csc')
    declareResolutionHists(self,'dt')
    declareResolutionHists(self,'csc&dt',8)
    
    
    self.HistInit('cscStations', 'cscStations; Stations; DSA Muons', 9, 0, 9)
    self.HistInit('dtStations', 'dtStations; Stations; DSA Muons', 9, 0, 9)
    self.HistInit('csc&dtStations', 'csc&dtStations; Stations; DSA Muons', 9, 0, 9)
    
    self.HistInit('test','test;#delta p_{T}; Reco Muons', 100, -5,5)
    
    
    

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
        self.HISTS['test'].Fill(reco.pt-dsaMuons[reco.idx].pt)
        ndt = dsaMuons[reco.idx].nDTStations
        ncsc = dsaMuons[reco.idx].nCSCStations
        self.HISTS['cscStations'].Fill(ncsc)
        self.HISTS['dtStations'].Fill(ndt)
        self.HISTS['csc&dtStations'].Fill(ncsc+ndt)  
        if ncsc == 0:
            if ndt != 0:
                if dsaMuons[reco.idx].ndof != 0: self.HISTS['chi2/ndf vs ndtStats'].Fill(ndt, dsaMuons[reco.idx].chi2/dsaMuons[reco.idx].ndof)
                if reco.pt != 0: self.HISTS['dPt/Pt vs ndtStats'].Fill(ndt, reco.ptError/reco.pt)
                if gen.pt != 0: self.HISTS['dt_%istat'%ndt].Fill((reco.pt - gen.pt)/gen.pt)
                if gen.pt != 0: self.HISTS['dt_%istat_gauss'%ndt].Fill((1.*reco.charge/reco.pt - 1.*gen.charge/gen.pt)/(1.*gen.charge/gen.pt))
        else:
            if ndt == 0:
                if dsaMuons[reco.idx].ndof != 0: self.HISTS['chi2/ndf vs ncscStats'].Fill(ncsc, dsaMuons[reco.idx].chi2/dsaMuons[reco.idx].ndof)
                if reco.pt != 0: self.HISTS['dPt/Pt vs ncscStats'].Fill(ncsc, reco.ptError/reco.pt)
                if gen.pt != 0: self.HISTS['csc_%istat'%ncsc].Fill((reco.pt - gen.pt)/gen.pt)
                if gen.pt != 0: self.HISTS['csc_%istat_gauss'%ncsc].Fill((1.*reco.charge/reco.pt - 1.*gen.charge/gen.pt)/(1.*gen.charge/gen.pt))
            else: # csc !=0 & dt !=0
                if gen.pt != 0: 
                    nstat = ndt+ncsc
                    if nstat > 4:
                        self.HISTS['csc&dt_5+stat'].Fill((reco.pt - gen.pt)/gen.pt)
                        self.HISTS['csc&dt_5+stat_gauss'].Fill((1.*reco.charge/reco.pt - 1.*gen.charge/gen.pt)/(1.*gen.charge/gen.pt))
                    else:
                        self.HISTS['csc&dt_%istat'%(ncsc+ndt)].Fill((reco.pt - gen.pt)/gen.pt)
                        self.HISTS['csc&dt_%istat_gauss'%(ncsc+ndt)].Fill((1.*reco.charge/reco.pt - 1.*gen.charge/gen.pt)/(1.*gen.charge/gen.pt))
                    
                    
    

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
    analyzer.writeHistograms('roots/nStationsComparisonPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
