#!/usr/bin/env python
import ROOT as r
import glob
import array
import DisplacedDimuons.Analysis.Primitives as Primitives


sample = 'HTo2XTo4Mu'



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




for i, d0_1_t in enumerate(d0Types):
    for j, d0_2_t in enumerate(d0Types):
        if j <= i: continue
            
        d0_1_str = d0_1_t[2]
        d0_2_str = d0_2_t[2]
        c = r.TCanvas()
        c.cd()
        r.gStyle.SetOptStat(111111)
        r.gStyle.SetOptFit()

        var = '%s-%s'%(d0_1_str, d0_2_str)



#hists = {}

#l = r.TLegend(0.75,0.77, 0.95, 0.95)
#l = r.TLegend(0.50,0.77, 0.70, 0.95)
 #       h1 = r.TH1F("","", 100, -0.015, 0.015)
 #       h1.Draw("axis")
 #       c.Update()
 #       h1.GetXaxis().SetLimits(-0.015, 0.015)
 #       h1.SetMinimum(1)
 #       h1.SetMaximum(1e7)
        #h1.Fill(0)
        #h1.Draw("axis")
 #       r.gPad.RedrawAxis()
    
    
        for k,filename in enumerate(glob.glob('roots/d0ComparisonPlots_'+sample+'*.root')):
            arr = filename.split('_')
            
            ct = arr[-1].split('.')[0]
            mX = arr[-2]
            mH = arr[-3]
            
            id =  "mH=%s mX=%s ct=%3.1f [cm]"%(mH, mX, float(ct)/10)
            print id
            f = r.TFile(filename)
            
            
            h = f.Get(var+'_'+sample+'_'+mH+'_'+mX+'_'+ct)
        
            
        
            c.SetLogy()
           
    
        
            if mH == '125':
                h.SetLineColor(r.kGreen+1)        
            elif mH == '200':
                h.SetLineColor(r.kRed)
            elif ct == '200':
                h.SetLineColor(r.kBlue+1)
            elif ct == '2':
                h.SetLineColor(r.kBlack)
                
            h.SetLineWidth(2)
            
            
            #h = 
            
    
            #h.GetXaxis().SetRangeUser(-0.015,0.015)
           # h.GetXaxis().SetLimits(-0.015,0.015)
            #h.GetXaxis().SetLimits(-0.015,0.015)  
            #h.Draw("sames")
            if k ==0:
                h.GetXaxis().SetLimits(-0.015,0.015)
                #h.SetMinimum(-0.015)
                #h.SetMaximum(0.015)
                h.Draw()
                #h.GetXaxis().SetRangeUser(-0.015,0.015)
                #h.GetXaxis().SetLimits(-0.015,0.015)
                #c.Update()
                #h.Draw("same")
            else:
            #   continue
                h.Draw("sames")
            #h.GetXaxis().SetRangeUser(-0.015,0.015)
            #h.GetXaxis().SetLimits(-0.015,0.015)
                
            c.Update()
                
            stats = h.GetListOfFunctions().FindObject("stats")
            stats.SetX1NDC(0.80)
            stats.SetX2NDC(0.99)
            stats.SetY1NDC(0.79-0.2*k)
            stats.SetY2NDC(0.99-0.2*k)
            
            if mH == '125':      
                stats.SetTextColor(r.kGreen+1)
            elif mH == '200':
                stats.SetTextColor(r.kRed)
            elif ct == '200':
                stats.SetTextColor(r.kBlue+1)
            elif ct == '2':
                stats.SetTextColor(r.kBlack)
                
            h.SetDirectory(0)
            
            #c.Update()
        
        c.Print(var+'.pdf')