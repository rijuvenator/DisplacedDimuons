#!/usr/bin/env python
import ROOT as R
import DisplacedDimuons.Analysis.Analyzer as Analyzer
import DisplacedDimuons.Analysis.Primitives as Primitives

#
# voms-proxy-init --voms cms
#python analyzeD0.py --signalpoint 125 20 1300
#


#define all combinations of d0s
d0Types = []
for ex in Primitives.ImpactParameter.extrapolationDictionary:
    for vert in Primitives.ImpactParameter.vertexDictionary:
        d0_str = vert + "-" 
        if ex == None:
            d0_str += "FULL"
        else:
            d0_str += ex
        d0Types.append([vert, ex, d0_str])

print d0Types



def declareHistograms(self, Params=None):
    #iterate through all combinations of d0 values
    for i, d0_1_t in enumerate(d0Types):
        for j, d0_2_t in enumerate(d0Types):
            if j <= i: continue
            
            d0_1_str = d0_1_t[2]
            d0_2_str = d0_2_t[2]
            self.HistInit('%s-%s'%(d0_1_str, d0_2_str), "%s - %s; d_{0}[cm]; Counts"%(d0_1_str, d0_2_str), 100, 1,-1)
            
    
    
def analyze(self, E, PARAMS=None):
    
    Muons = E.getPrimitives('DSAMUON')
    
    #selections
    if self.TRIGGER:
        if not Selections.passTrigger(E): return
    
    for mu in Muons:    
        for i, d0_1_t in enumerate(d0Types):
            for j, d0_2_t in enumerate(d0Types):
                if j <= i: continue
                d0_1 = mu.d0(d0_1_t[0], d0_1_t[1])
                d0_2 = mu.d0(d0_2_t[0], d0_2_t[1])
                if (abs(d0_1 -d0_2) > 0.1):
                    event = E.getPrimitives('EVENT')
                    print event
                    print mu
            
                d0_1_str = d0_1_t[2]
                d0_2_str = d0_2_t[2]
                self.HISTS['%s-%s'%(d0_1_str,d0_2_str)].Fill(d0_1 - d0_2)
            



#### RUN ANALYSIS ####
if __name__ == '__main__':
    ARGS = Analyzer.PARSER.parse_args()
    Analyzer.setSample(ARGS)
    for METHOD in ('declareHistograms', 'analyze'):
        setattr(Analyzer.Analyzer, METHOD, locals()[METHOD])
    analyzer = Analyzer.Analyzer(
        ARGS        = ARGS,
        BRANCHKEYS  = ('EVENT','GEN', 'DSAMUON'),
    )
    analyzer.writeHistograms('roots/d0ComparisonPlots{}_{{}}.root'.format('_Trig' if ARGS.TRIGGER else ''))
