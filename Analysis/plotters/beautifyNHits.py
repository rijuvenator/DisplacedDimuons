#!/usr/bin/env python
import ROOT as r
import glob
import array
import re
import DisplacedDimuons.Analysis.Primitives as Primitives


sample = 'HTo2XTo4Mu'

# TODO:
# could put many pdfs on a single pad
#


colors = [r.kRed, r.kOrange+2, r.kBlue+2,r.kBlack, r.kGreen+2, r.kMagenta+1, r.kYellow-2, r.kViolet+2]

def makePlot(chamberType, f, mH, mX, ct, plotType = ''):
    arr = filename.split('_')
        
    ct = arr[-1].split('.')[0]
    mX = arr[-2]
    mH = arr[-3]
        
    id = "mH=%s mX=%s ct=%3.1f [cm]" % (mH, mX, float(ct) / 10)
    print id
    f = r.TFile(filename)
    
    c = r.TCanvas()
    c.cd()
    c.SetLogy()
    if len(plotType) == 0:
        r.gStyle.SetOptStat(101111)
    else:
        r.gStyle.SetOptStat(111111)
    r.gStyle.SetOptFit()
    
    sampleName = sample + '_' + mH + '_' + mX + '_' + ct
    
    stations = []
    if chamberType == 'csc&dt':
        stations = [1,2,3,4,5]
    else:
        stations = [1,2,3,4]
        
    if len(plotType) != 0:
        plotType +='_'
    
    for i in stations:
        if i == 5:
            h = f.Get('%s_%i+hit_%s%s'%(chamberType,i, plotType, sampleName))
            h.SetName("%i+ %s Stat(s)"%(i,chamberType.upper()))
        else:
            h = f.Get('%s_%ihit_%s%s'%(chamberType,i, plotType,sampleName))
            h.SetName("%i %s Stat(s)"%(i,chamberType.upper()))
        h.SetLineColor(colors[i-1])
                
        h.SetLineWidth(2)
                
        if i == 1:
            h.SetTitle("mH=%s mX=%s ct=%3.1f [cm]" % (mH, mX, float(ct) / 10))
            h.Draw()
            h.SetMaximum(10000)
            h.SetMinimum(0.5)
        else:
            h.Draw('sames')
        
        c.Update()
            
        stats = h.GetListOfFunctions().FindObject("stats")
        stats.SetX1NDC(0.80-0.19*(i/5))
        stats.SetX2NDC(0.99-0.19*(i/5))
        if i != 5:
            stats.SetY1NDC(0.79 - 0.2 * (i-1))
            stats.SetY2NDC(0.99 - 0.2 * (i-1))
        else:
            stats.SetY1NDC(0.69 )
            stats.SetY2NDC(0.89 )
                
        stats.SetTextColor(colors[i-1])
                
        h.SetDirectory(0)
            
        c.Update()
        
    c.Print('%sHits_%s%s.pdf'%(chamberType,sampleName,plotType))
    #return c
    

for k, filename in enumerate(glob.glob('roots/nStationsComparisonPlots_Trig_' + sample + '*.root')):
    arr = filename.split('_')
        
    ct = arr[-1].split('.')[0]
    mX = arr[-2]
    mH = arr[-3]
        
    id = "mH=%s mX=%s ct=%3.1f [cm]" % (mH, mX, float(ct) / 10)
    print id
    f = r.TFile(filename)
    #cscC = makePlot('csc', f, mH, mX, ct)
    for plotType in ['', 'gauss']:
        makePlot('csc', f, mH, mX, ct,plotType)
        #dtC  = makePlot('dt', f, mH, mX, ct)
        makePlot('dt', f, mH, mX, ct, plotType)
        makePlot('csc&dt', f, mH, mX, ct,plotType)
    
#     c = r.TCanvas()
#     c.cd()
#     c.SetLogy()
#     r.gStyle.SetOptStat(101111)
#     r.gStyle.SetOptFit()
#     
#     sampleName = sample + '_' + mH + '_' + mX + '_' + ct
#     
#     for i in [1,2,3,4]:
#         h = f.Get('csc_%ihit_%s'%(i, sampleName))
#         h.SetLineColor(colors[i-1])
#                 
#         h.SetLineWidth(2)
#         h.SetName("%i Hit(s)"%i)
#                 
#         if i == 1:
#             h.SetTitle("mH=%s mX=%s ct=%3.1f [cm]" % (mH, mX, float(ct) / 10))
#             h.Draw()
#             h.SetMaximum(2500)
#             h.SetMinimum(1)
#         else:
#             h.Draw('sames')
#         
#         c.Update()
#             
#         stats = h.GetListOfFunctions().FindObject("stats")
#         stats.SetX1NDC(0.80)
#         stats.SetX2NDC(0.99)
#         stats.SetY1NDC(0.79 - 0.2 * (i-1))
#         stats.SetY2NDC(0.99 - 0.2 * (i-1))
#                 
#         stats.SetTextColor(colors[i-1])
#                 
#         h.SetDirectory(0)
#             
#         # c.Update()
#         
#     c.Print('cscHits_%s.pdf'%sampleName)
