#!/usr/bin/env python
import ROOT as R
import DisplacedDimuons.Analysis.Primitives as Primitives

TESTFILE = '../test/test.root'
OUTFILE = 'd0-plots.root'

f = R.TFile.Open(TESTFILE)
t = f.Get('SimpleNTupler/DDTree')
f1 = R.TFile(OUTFILE, "RECREATE")
f.cd()

# test tree
try:
    t.GetEntries()
    print('Successfully got tree...')
except:
    print('Failed to get tree; exiting')
    exit()
    
    


d0Types = [['PV-FullFit','PV',None], ['PV-LineFit', 'PV','LIN'], ['BS-FullFit', 'BS', None], ['BS-LineFit', 'BS', 'LIN']]

#histograms for comparing d0 quantities
hists = {}
counter = 0
for i, d0_t1 in enumerate(d0Types):
    for j, d0_t2 in enumerate(d0Types):
        if j <= i: continue
        
        hists[counter] = R.TH1F("%s_%s"%(d0_t1[0], d0_t2[0]), "%s - %s; d0[units?], Muons"%(d0_t1[0],d0_t2[0]), 100, -1,1)
        counter += 1
        

for e, event in enumerate(t):
    E = Primitives.ETree(t)
        
    Gens     = E.getPrimitives('GEN')
    DSAMuons = E.getPrimitives('DSAMUON')
          
    for mu in DSAMuons:
        counter = 0
        for i, d0_t1 in enumerate(d0Types):
            for j, d0_t2 in enumerate(d0Types):
                if j <= i: continue
                d0_1 = mu.d0(d0_t1[1], d0_t1[2])  
                d0_2 = mu.d0(d0_t2[1],d0_t2[2])
                
                hists[counter].Fill(d0_1-d0_2)

                counter +=1
       # hists.append(R.TH1F("%s_%s"%(d0_1[0], d0_2[0]), "%s - %s; d0[units?], Muons"%(d0_1[0],d0_2[0]), 100, -5,5))
        

print("Writing Histograms")

f1.cd()
for hist in hists:
    hists[hist].SetDirectory(0)
    hists[hist].Write()
    
f1.Close()

   