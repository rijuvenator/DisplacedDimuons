import ROOT

class Sample:
    'Sample information class'
    def __init__(self):
        self.sampleName = []
        self.sampleLegendName = []        
        self.histName = []
        self.histColor = []
        
    def AddSample(self, sampleName, legendName, histName, histColor):
        self.sampleName.append(sampleName)
        self.sampleLegendName.append(legendName)
        self.histName.append(histName)
        self.histColor.append(histColor)

    def GetSampleName(self):
        return self.sampleName

    def GetLegendName(self):
        return self.sampleLegendName

    def GetHistName(self):
        return self.histName

    def GetHistColor(self):
        return self.histColor
    
    def nSamples(self):
        return len(self.sampleName)
    


def createSimple1DPlot(var, title, nbins, inibin, endbin, samples):
    hist1D = []
    colors = [1,2,3,4,6,7,8,9,28,30,38,49,46]
    for index, ksamples in enumerate(samples.GetSampleName()):
        hist1D.append(ROOT.TH1F(var, title, nbins, inibin, endbin))
        hist1D[index].SetDirectory(0)
        hist1D[index].Sumw2()
        hist1D[index].SetLineColor(samples.GetHistColor()[index])

    return hist1D

def createSimple2DPlot(var, title, nbinsX, inibinX, endbinX, nbinsY, inibinY, endbinY, samples):
    hist2D = []
    colors = [1,2,3,4,6,7,8,9,28,30,38,49,46]
    for index, ksamples in enumerate(samples.GetSampleName()):
        hist2D.append(ROOT.TH2F(var, title, nbinsX, inibinX, endbinX, nbinsY, inibinY, endbinY))
        hist2D[index].SetDirectory(0)
        hist2D[index].SetMarkerColor(samples.GetHistColor()[index])
        hist2D[index].SetLineColor(samples.GetHistColor()[index])
        hist2D[index].SetMarkerStyle(20)
        hist2D[index].SetMarkerSize(0.6)

    return hist2D
    
    

def makeSimple1DPlot(var, canvas, samples, title, xtitle, ytitle, output, folder, logy=False, showOnly = []):

    file = ROOT.TFile(folder+output+"-hist.root","recreate");
    file.cd()
    template = []
    
#    ROOT.gStyle.SetOptStat(0);
    ROOT.gStyle.SetOptStat(111111);

#    leg = ROOT.TLegend(0.65,0.55,.90,.90)
    leg = ROOT.TLegend(0.40,0.70,.90,.90)
    leg.SetFillColor(0);

    Canvas = ROOT.TCanvas(canvas, title, 10, 10, 700, 500)
    Canvas.cd()

    plotted = False
    for index, hist in enumerate(var):
        #needed to store the templates
        template.append(hist.Clone())
        template[index].SetName(samples.GetHistName()[index]);

        ##hist
#        normHist = 1
#        if hist.Integral()> 0:
#            hist.Scale(normHist/hist.Integral())
        if len(showOnly) >0:
            if samples.GetHistName()[index] not in showOnly:
                continue

        if plotted == True: 
            hist.Draw("hist same")

        if plotted == False: 
            Minimum = hist.GetMinimum()
            Maximum = hist.GetMaximum()

            if (Minimum >0.) and logy==False: hist.SetMinimum(.0)
            if (Minimum >0.01) and logy==True: hist.SetMinimum(0.01)
            if (Maximum >0.) and logy==False: hist.SetMaximum(1.3*hist.GetMaximum())
#            if (Maximum >0.) and logy==True: hist.SetMaximum(1.3*hist.GetMaximum())
#if (Maximum >0.) and logy==False: hist.SetMaximum(1.)
#            if (Maximum >0.) and logy==True: hist.SetMaximum(1.3)
            
            hist.Draw("hist")
            hist.SetTitle(title)
#            var[index].GetXaxis()
            Xaxis = hist.GetXaxis()
            Xaxis.SetTitle(xtitle)
            Yaxis = hist.GetYaxis()
            Yaxis.SetTitle(ytitle)
            plotted = True

        leg.AddEntry(var[index], samples.GetLegendName()[index], "l")

        print "sample:", samples.GetLegendName()[index], "histo:", output, "mean:", hist.GetMean()

#    leg.Draw()
    if logy == True:
        Canvas.SetLogy(1)

    Canvas.SaveAs(folder+output+".pdf")
    Canvas.SaveAs(folder+output+".png")
    Canvas.SaveAs(folder+output+".eps")
    Canvas.SaveAs(folder+output+".root")
    file.Write()
    file.Close()
    
def makeSimple2DPlot(var, canvas, samples, title, xtitle, ytitle, output, folder, showOnly = [], showReversed= True):

    file = ROOT.TFile(folder+output+"-2Dhist.root","recreate");
    file.cd()
    template = []
    
    ROOT.gStyle.SetOptStat(0);

#    leg = ROOT.TLegend(0.65,0.55,.90,.90)
    leg = ROOT.TLegend(0.50,0.65,.90,.90)
    leg.SetFillColor(0);

    Canvas = ROOT.TCanvas(canvas, title, 10, 10, 700, 500 )
    Canvas.cd()

    plotted = False
    for index, hist in enumerate(var):
        #needed to store the templates
        template.append(hist.Clone())
        template[index].SetName(samples.GetHistName()[index]);
        if len(showOnly) >0:
            if samples.GetHistName()[index] not in showOnly:
                continue                                        

        if plotted == True: 
            hist.Draw("hist same")

        if plotted == False:
            hist.Draw("hist")
            hist.SetTitle(title)

            Xaxis = hist.GetXaxis()
            Xaxis.SetTitle(xtitle)
            Yaxis = hist.GetYaxis()
            Yaxis.SetTitle(ytitle)
            plotted = True

        leg.AddEntry(var[index], samples.GetLegendName()[index], "p")


    ## Make plot cleaner. Illustration only.
    if showReversed==True:
        for index in range(samples.nSamples()-1, -1, -1):
            if len(showOnly) >0:
                if samples.GetHistName()[index] not in showOnly:
                    continue
                var[index].Draw("hist same")
        
    ########################
    leg.Draw()

    Canvas.SaveAs(folder+output+".pdf")
    Canvas.SaveAs(folder+output+".png")
    Canvas.SaveAs(folder+output+".eps")
    Canvas.SaveAs(folder+output+".root")
    file.Write()
    file.Close()

