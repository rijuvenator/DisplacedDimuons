#!/usr/bin/env python
import ROOT as R
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Analysis.Selections as Selections

#
# voms-proxy-init --voms cms
#python analyze<>.py --signalpoint 125 20 1300
#



def declareHistograms(self, Params=None):
    
    self.HistInit('Lxy-Isolation', 'Lxy Isolation; #Sigma p_T{cone} / p_{#mu#mu}; Events', 100, 0, 0.05)
    self.HistInit('Lxy-Isolation-Selected', 'Selected Dimuon Lxy Isolation; #Sigma p_T{cone} / p_{#mu#mu}; Events', 100, 0, 0.05)
    self.HistInit('Pmumu-Isolation', 'P_{#mu#mu} Isolation; #Sigma p_T{cone} / p_{#mu#mu}; Events', 100, 0, 0.05)
    self.HistInit('Pmumu-Isolation-Selected', 'Selected Dimuon P_{#mu#mu} Isolation; #Sigma p_T{cone} / p_{#mu#mu}; Events', 100, 0, 0.05)
    

def analyze(self, E, PARAMS=None):
    
    #selections
    if self.TRIGGER:
        if not Selections.passTrigger(E): return
    
    DSAmuons = E.getPrimitives('DSAMUON')
    Dimuons  = E.getPrimitives('DIMUON' )

    DSASelections    = [Selections.MuonSelection(muon) for muon in DSAmuons]
    DimuonSelections = [Selections.DimuonSelection(dimuon) for dimuon in Dimuons ]
    selectedDSAmuons = [mu for idx,mu in enumerate(DSAmuons) if DSASelections[idx]]
    selectedDimuons  = [dim for idx,dim in enumerate(Dimuons) if DimuonSelections[idx].allExcept('LxySig', 'deltaPhi') and DSASelections[dim.idx1] and DSASelections[dim.idx2]]

    
    for dimuon in Dimuons:
        #print dimuon
        self.HISTS['Lxy-Isolation'].Fill(dimuon.isoLxy)
        self.HISTS['Pmumu-Isolation'].Fill(dimuon.isoPmumu)
        
    for dimuon in selectedDimuons:
        self.HISTS['Lxy-Isolation-Selected'].Fill(dimuon.isoLxy)
        self.HISTS['Pmumu-Isolation-Selected'].Fill(dimuon.isoPmumu)
    

    
    
# cleanup function for Analyzer class
def end(self, PARAMS=None):
    pass

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze', 'end'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DIMUON','DSAMUON'),
        FILES = '/afs/cern.ch/user/w/wnash/DisplacedDimuons/Tupler/python/qcdIsolation.root'
    )
    analyzer.writeHistograms('roots/isolationPlots.root')
