#!/usr/bin/env python
import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Analysis.PrimitivesPrinter as PrimitivesPrinter
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Selector as Selector
import DisplacedDimuons.Analysis.RootTools as RootTools

#
# voms-proxy-init --voms cms
#python analyze<>.py --signalpoint 125 20 1300
#


def declareHistograms(self, Params=None):
    self.HistInit('DSA p_{T} Spectrum', "DSA p_{T} Spectrum; Lowest p_{T}  in pair [GeV/c]; Dimuons",100 ,0,100)
    
    for tag in ('DSA','PAT','HYBRID'):
        self.HISTS[tag+'-Lxy-Isolation'] = R.TH1D(tag+'-Lxy-Isolation',tag+' Selected Dimuon Lxy Isolation; #Sigma p_T{cone} / p_{#mu#mu}; Dimuons',8, np.logspace(-5, 3, 9) )
        self.HISTS[tag+'-Pmumu-Isolation'] = R.TH1D(tag+'-Pmumu-Isolation',tag+' Selected Dimuon P_{#mu#mu} Isolation; #Sigma p_T{cone} / p_{#mu#mu}; Dimuons',8, np.logspace(-5, 3, 9) )
        self.HISTS[tag+'-DimuonMax-Isolation'] = R.TH1D(tag+'-DimuonMax-Isolation',tag+' Selected Dimuon Max Isolation; #Sigma p_T{cone} / p_{#mu#mu}; Dimuons',8, np.logspace(-5, 3, 9) )
        self.HISTS[tag+'-Mu1-Isolation'] = R.TH1D(tag+'-Mu1-Isolation',tag+'-Mu1-Isolation; #Sigma p_T{cone} / p_{#mu#mu}; Dimuons',8,np.logspace(-5, 3, 9))
        self.HISTS[tag+'-Mu2-Isolation'] = R.TH1D(tag+'-Mu2-Isolation',tag+'-Mu2-Isolation; #Sigma p_T{cone} / p_{#mu#mu}; Dimuons',8,np.logspace(-5, 3, 9))
        self.HISTS[tag+'-SingleMuonMax-Isolation'] = R.TH1D(tag+'-SingleMuonMax-Isolation',tag+'-SingleMuonMax-Isolation; #Sigma p_T{cone} / p_{#mu#mu}; Dimuons', 8,np.logspace(-5, 3, 9))
    

def analyze(self, E, PARAMS=None):
    
    #selections
    if self.TRIGGER:
        if not Selections.passedTrigger(E): return
    
    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3  = E.getPrimitives('DIMUON')
    Event = E.getPrimitives('EVENT')


    #selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, '_Combined_NS_NH_FPTE_HLT_REP_PT_DCA_PC_LXYE_CHI2_VTX_COSA_NPP_TRK_NDT_DPHI', Dimuons3, DSAmuons, PATmuons)
    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, '_Combined_NS_NH_FPTE_HLT_DCA_PC_LXYE_CHI2', Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is None: return
    
    foundDSADimuon = False
    
    for dimuon in selectedDimuons:
        if dimuon.LxySig() < 10.: continue
        #print dimuon
        self.HISTS[dimuon.composition+'-Lxy-Isolation'].Fill(dimuon.isoLxy)
        self.HISTS[dimuon.composition+'-Pmumu-Isolation'].Fill(dimuon.isoPmumu)
        self.HISTS[dimuon.composition+'-DimuonMax-Isolation'].Fill(max(dimuon.isoPmumu,dimuon.isoLxy))
        self.HISTS[dimuon.composition+'-Mu1-Isolation'].Fill(dimuon.mu1.iso)
        self.HISTS[dimuon.composition+'-Mu2-Isolation'].Fill(dimuon.mu2.iso)
        self.HISTS[dimuon.composition+'-SingleMuonMax-Isolation'].Fill(max(dimuon.mu1.iso,dimuon.mu2.iso))
        if dimuon.composition == 'DSA':
            foundDSADimuon = True
            self.HISTS['DSA p_{T} Spectrum'].Fill(min(dimuon.mu1.pt,dimuon.mu2.pt))
        
    #if foundDSADimuon: print Event
    

    
    
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
        BRANCHKEYS  = ('EVENT','DIMUON','DSAMUON','PATMUON','FILTER', 'TRIGGER'),
        FILES = '/afs/cern.ch/user/w/wnash/DisplacedDimuons/Tupler/python/qcdIsolation.root'
        #FILES = '/afs/cern.ch/user/w/wnash/DisplacedDimuons/Tupler/python/signalIsolation.root'
    )
    analyzer.writeHistograms('roots/qcdIsolationPlots.root')
    #analyzer.writeHistograms('roots/signalIsolationPlots.root')
