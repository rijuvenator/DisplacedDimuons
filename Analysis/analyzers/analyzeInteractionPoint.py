#!/usr/bin/env python
import ROOT as R
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.Primitives as Primitives

#
# voms-proxy-init --voms cms
#python analyze<>.py --signalpoint 125 20 1300
#



def declareHistograms(self, Params=None):
    
    range = 0.005
    self.HistInit('Beamspot-Vertex-t', 'Beamspot-Vertex; #DeltaX [cm]; #DeltaY [cm]', 100, -range, range, 100, -range, range)
    self.HistInit('Beamspot-Vertex-z', 'Beamspot-Vertex; #DeltaZ [cm]; Events', 200, -20, 20)
    self.HistInit('Beamspot-x', 'Beamspot-x; X_{beamspot} [cm]; Events', 100, -2, 2)
    self.HistInit('Beamspot-y', 'Beamspot-y; Y_{beamspot} [cm]; Events', 100, -2, 2)
    self.HistInit('Beamspot-z', 'Beamspot-z; Z_{beamspot} [cm]; Events', 100, -2, 2)

def analyze(self, E, PARAMS=None):
    
    #selections
    #if self.TRIGGER:
    #    if not Selections.passTrigger(E): return
    

    
    Beamspot = E.getPrimitives('BEAMSPOT')
    Vertex = E.getPrimitives('VERTEX')
    
    self.HISTS['Beamspot-Vertex-t'].Fill(Beamspot.x-Vertex.x, Beamspot.y-Vertex.y)
    self.HISTS['Beamspot-Vertex-z'].Fill(Beamspot.z-Vertex.z)
    self.HISTS['Beamspot-x'].Fill(Beamspot.x)
    self.HISTS['Beamspot-y'].Fill(Beamspot.y)
    self.HISTS['Beamspot-z'].Fill(Beamspot.z)
    
 
    
    #selections
    #if self.TRIGGER:
    #    if not Selections.passTrigger(E): return
    
    
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
        BRANCHKEYS  = ('BEAMSPOT', 'VERTEX'),
    )
    analyzer.writeHistograms('roots/interactionPointComparisonPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
