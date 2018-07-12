#!/usr/bin/env python
import ROOT as r
import glob
import array
import math
import os

#load stuff from C++ in python
r.gROOT.ProcessLine(".L ../macros/Rebin.C")


OUTPUTDIR = 'pdfs/'

    #make directories
if not os.path.isdir(OUTPUTDIR):
    print("Making directory: %s"%OUTPUTDIR)
    os.system("mkdir %s"%OUTPUTDIR)

SAMPLE = 'HTo2XTo4Mu'

# mass : color
COLORDICT = {1000. : r.kBlack, 
             200.  : r.kBlue,
             125.  : r.kGreen}

# from https://en.wikipedia.org/wiki/Relativistic_Breit%E2%80%93Wigner_distribution
def BW(x,params):
    norm =  params[0]
    Gamma = params[1]
    mass  = params[2]
    gamma = math.sqrt(mass**2*(mass**2 + Gamma**2))
    
    k = 2*math.sqrt(2)*mass*Gamma*gamma / (3.14159*math.sqrt(mass**2 + gamma))
                                      
    return norm*k/((x[0]**2 - mass**2)**2 + (mass*Gamma)**2)
                                    
    
#from: https://github.com/cms-analysis/SUSYBSMAnalysis-Zprime2muAnalysis/blob/master/src/Functions.C
def Relativistic_Lorentzian(x, par):
  # The formula is from "The Z Boson" by C. Caso and A. Gurtu, PDG (2002).
  # Special form of Lorentzian used to fit Z's at LEP.
  # Normalization seems to be OK, but it is not in the PDG, and I cannot
  # derive it analytically (SV, Oct 9, 2003).

  # par[0] = Normalization constant
  # par[1] = FWHM
  # par[2] = mean Z' mass

  s = x[0]*x[0]; #square of dilepton mass
  f = (s*par[0]*par[1]*par[1])/((s-par[2]*par[2])*(s-par[2]*par[2]) + (s*s*par[1]*par[1]/(par[2]*par[2])))
  f *= 2.*s/(3.14159*par[1]*par[2]*par[2]);
  # Alternative expression, giving more symmetric Lorentzian
  # f *= 2./(TMath::Pi()*par[1]);

  return f

 #makes a mass plot with 
def makeMassPlot(f, mH, mX, ct, outputDir=''):
    var = 'massH'
    
    c = r.TCanvas()
    c.cd()
    r.gStyle.SetOptStat(0)
    r.gStyle.SetOptFit()
    l = r.TLegend(0.75,0.87, 0.95, 0.95)
    
    h = f.Get('%s_%s_%2.0f_%s_%s'%(var, SAMPLE, mH, mX,ct))
    h = r.Rebin(h, 3) #shrink bins by 3
    
    #bw mass fit
    # name, function, min, max, nparamters
    bw = r.TF1("bw",BW,mH*0.85,mH*1.15,3)
    bw.SetParameters(1000,10, h.GetMean())
    bw.SetParNames("Norm", "FWHM", "Mass", )
    
    if not COLORDICT.has_key(mH):
        print "Skipping mass plot: Add a new color if you add a new mass!"
        return
    
    h.SetLineColor(COLORDICT[mH])
        
        
    h.GetXaxis().SetRangeUser(0.7*mH, 1.3*mH)
    h.Draw()

    h.Fit(bw, "R")    
    bw.Draw("same")

    l.AddEntry(h, id)
    h.SetDirectory(0)
    
    c.Update()
    

    stats = h.GetListOfFunctions().FindObject("stats")
    stats.SetX1NDC(0.75)
    stats.SetX2NDC(0.95)
    stats.SetY1NDC(0.65)
    stats.SetY2NDC(0.85)
    stats.SetLineColor(r.kBlack)
    if mH == 125.:
        stats.SetLineColor(r.kGreen)
    elif mH == 200.:
        stats.SetLineColor(r.kBlue)
        
    c.Modified()

    
    l.Draw()
    c.Print('%s%s-%2.0f.pdf'%(outputDir,var, mH))
    
    
def maked0Plot(f, mH, mX, ct):
    
    var = 'd0'

    # d0 binning
    d0bins = array.array('d', [0.,1., 10., 30., 100.,1e3, 1e6 ])
    
    #from plot here https://wsi.web.cern.ch/wsi/slides/ForExoInTSG-0529.pdf
    eff = [0.8,0.5, 0.3, 0.01,0,0]
    
    h = f.Get('%s_%s_%2.0f_%s_%s'%(var, SAMPLE, mH, mX,ct))

    h = h.Rebin(len(d0bins)-1, "h", d0bins)
    entries = h.GetEntries()
    efficiencyIntegral = 0.0
    for j in range(1, h.GetNbinsX()+1):
        entriesInBin = h.GetBinContent(j)
        fractionOfEntries = 1.*entriesInBin/entries
        lowEdge = h.GetXaxis().GetBinLowEdge(j)
        highEdge = lowEdge + h.GetXaxis().GetBinWidth(j)

        print "Bin {:2d} ~ [{:8.2f} - {:10.2f}) cm:\t{:6.0f}/{:6.0f} =\t {:6.4f}".format(j,lowEdge, highEdge,\
                                                                     entriesInBin,entries, fractionOfEntries)
        efficiencyIntegral +=eff[j-1]*fractionOfEntries
    print "d0 efficiency is %3.4f"%efficiencyIntegral
        
    if not COLORDICT.has_key(mH):
        print "Skipping mass plot: Add a new color if you add a new mass!"
        return 0
    h.SetLineColor(COLORDICT[mH])
    return h


c_d0 = r.TCanvas()
c_d0.SetLogx()

leg = r.TLegend(0.75,0.77, 0.95, 0.95)

for i,filename in enumerate(glob.glob('../analyzers/roots/GenPlots_'+SAMPLE+'*.root')):
    arr = filename.split('_')
    ct = arr[-1].split('.')[0]
    mX = arr[-2]
    mH = float(arr[-3])
    
    id =  "mH=%2.0f mX=%s ct=%3.1f [cm]"%(mH, mX, float(ct)/10)
    print "\n ---------- %s ----------\n"%id
    
    f = r.TFile(filename)
    
    makeMassPlot(f, mH, mX, ct, OUTPUTDIR)
    
    h_d0 = maked0Plot(f,mH, mX, ct)
    if h_d0 == 0.: #something failed
        continue
    
    c_d0.cd()
    
    if i ==0:
        h_d0.SetMaximum(60000)
        h_d0.Draw()
    else:
        h_d0.Draw("sames")
    
    leg.AddEntry(h_d0, id)
    h_d0.SetDirectory(0)
    
    c_d0.Update()
    

c_d0.cd()
leg.Draw()
c_d0.Print('%sd0.pdf'%OUTPUTDIR)
    
   