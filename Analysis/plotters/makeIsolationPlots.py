#!/usr/bin/env python
import ROOT as r
import glob
import array
import re
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Analysis.Plotter as Plotter

writepath = 'pdf/'


colors = [r.kRed, r.kOrange+2, r.kBlue+2,r.kBlack, r.kGreen+2, r.kMagenta+1, r.kYellow-2, r.kViolet+2]


for filename in ['/afs/cern.ch/user/w/wnash/DisplacedDimuons/Analysis/analyzers/roots/qcdIsolationPlots.root']:

    f = r.TFile(filename)
    
 
    for muonTag in ['DSA', 'PAT', 'HYBRID']:
        can = Plotter.Canvas(lumi=muonTag)

        for i,isolationType in enumerate(['Lxy', 'Pmumu', 'DimuonMax', 'Mu1', 'Mu2', 'SingleMuonMax']):
            #p = makePlot(muonTag, isolationType)
            plotName = muonTag+'-'+isolationType+'-Isolation;1'
            h = f.Get(plotName)
            plot = Plotter.Plot(h,isolationType, legType='l', option='hist')
            plot.legName = '#splitline{#bf{%s}}{#mu: %4.3f E: %3i, U: %2i, O: %2i}'%(plot.legName, plot.GetMean(),plot.GetEntries(), plot.GetBinContent(0),plot.GetBinContent(plot.GetXaxis().GetNbins()+1))
            can.addMainPlot(plot)
            plot.setColor(colors[i])
        can.firstPlot.SetMaximum(50.)
        can.firstPlot.GetXaxis().SetTitle('#Sigma P_{T}^{cone} / P_{T}^{isolated}')
        can.Update()
        can.mainPad.SetLogx(True)
        can.makeLegend(pos='tl')
        can.legend.resizeHeight(2)
        can.cleanup(writepath+muonTag+'-isolation.pdf')
    

 