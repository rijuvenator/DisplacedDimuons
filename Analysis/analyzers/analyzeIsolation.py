#!/usr/bin/env python
import ROOT as R
import numpy as np
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Analysis.Selections as Selections
import DisplacedDimuons.Analysis.Selector as Selector
import DisplacedDimuons.Analysis.RootTools as RootTools

#
# voms-proxy-init --voms cms
#python analyze<>.py --signalpoint 125 20 1300
#



def declareHistograms(self, Params=None):
    
    for tag in ('DSA','PAT','HYBRID'):
        self.HISTS[tag+'-Lxy-Isolation'] = R.TH1D(tag+'-Lxy-Isolation',tag+' Selected Dimuon Lxy Isolation; #Sigma p_T{cone} / p_{#mu#mu}; Events',8, np.logspace(-5, 3, 9) )
        self.HISTS[tag+'-Pmumu-Isolation'] = R.TH1D(tag+'-Pmumu-Isolation',tag+' Selected Dimuon P_{#mu#mu} Isolation; #Sigma p_T{cone} / p_{#mu#mu}; Events',8, np.logspace(-5, 3, 9) )

    

def analyze(self, E, PARAMS=None):
    
    #selections
    if self.TRIGGER:
        if not Selections.passTrigger(E): return
    
    DSAmuons = E.getPrimitives('DSAMUON')
    PATmuons = E.getPrimitives('PATMUON')
    Dimuons3  = E.getPrimitives('DIMUON' )


    selectedDimuons, selectedDSAmuons, selectedPATmuons = Selector.SelectObjects(E, '_Combined_NS_NH_FPTE_HLT_REP_PT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_LXYSIG_TRK_NDT_DPHI', Dimuons3, DSAmuons, PATmuons)
    if selectedDimuons is None: return

    
    for dimuon in selectedDimuons:

        self.HISTS[dimuon.composition+'-Lxy-Isolation'].Fill(dimuon.isoLxy)
        self.HISTS[dimuon.composition+'-Pmumu-Isolation'].Fill(dimuon.isoPmumu)
        
    

    
    
# cleanup function for Analyzer class
def end(self, PARAMS=None):
    for tag in ('DSA','PAT','HYBRID'):
        RootTools.addFlows(self.HISTS[tag+'-Lxy-Isolation'])
        RootTools.addFlows(self.HISTS[tag+'-Pmumu-Isolation'])
    pass

#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze', 'end'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('DIMUON','DSAMUON','PATMUON','FILTER', 'TRIGGER'),
        FILES = '/afs/cern.ch/user/w/wnash/DisplacedDimuons/Tupler/python/qcdIsolation.root'
    )
    analyzer.writeHistograms('roots/isolationPlots.root')
