import re
import ROOT as R
from ROOT import gStyle, gPad
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Utilities import SPStr, SPLumiStr
import DisplacedDimuon.Analysis.HistogramGetter as HistogramGetter

TRIGGER = True
PRINTINTEGRALS = False

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/muonQualityStudies_HTo2XTo2Mu2J_1000_150_1000.root')
#HISTS = HistogramGetter.getHistograms('../analyzers/roots/muonQualityStudies_HTo2XTo2Mu2J_125_20_1300.root')
#f = R.TFile.Open('../analyzers/roots/muonQualityStudies_HTo2XTo2Mu2J_1000_150_1000.root')

# make plots that are per sample
def makePerSamplePlots():
    for ref in HISTS:
        print "ref: ,", ref
        if type(ref) == tuple:
            if ref[0] == '4Mu':
                name = 'HTo2XTo4Mu_'
                latexFS = '4#mu'
            elif ref[0] == '2Mu2J':
                name = 'HTo2XTo2Mu2J_'
                latexFS = '2#mu2j'
            if TRIGGER:
                name = 'Trig-'+name
            name += SPStr(ref[1])
            lumi = SPLumiStr(ref[0], *ref[1])
            legName = HistogramGetter.PLOTCONFIG['HTo2XTo'+ref[0]]['LATEX']
            print "name: ", name, " lumi: ", lumi, " legName: ", legName
        else:
            name = ref
            lumi = HistogramGetter.PLOTCONFIG[ref]['LATEX']
            legName = HistogramGetter.PLOTCONFIG[ref]['LATEX']

        # histo filename
        fname = 'pdfs/muonQualityPlots_{}.pdf'.format(name)

        # canvas
        canvas = R.TCanvas('c', 'canvas', 0, 0, 800, 600)

        gStyle.SetOptStat(111111)
#        gStyle.SetStatW(0.25)        # width of statistics box; default is 0.19
#        gStyle.SetStatH(0.10)        # height of statistics box; default is 0.1
#        gStyle.SetStatFontSize(0.07) # size for stat. box

        # delta R between nearest HLT and DSA muons
        canvas.Clear()
        htit = 'dR_HLT_DSA'
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        pad.Draw()
        pad.Divide(1,2)
        pad.cd(1)
        HISTS[ref][htit].Draw("hist")
        pad.cd(2)
        HISTS[ref][htit].Draw("hist")
        gPad.SetLogy(1)
        canvas.Print(fname+"(", "Title:"+htit)

        # number of unsuccessful and successful HLT-DSA matches
        canvas.Clear()
        htit = 'matches_HLT_DSA'
        HISTS[ref][htit].Draw("hist")
        canvas.Print(fname, "Title:"+htit)

        # N(CSC stations) vs N(DT stations) 
        htit = 'CSC_vs_DT_Stations'
        HISTS[ref][htit].Draw("text")
        canvas.Print(fname, "Title:"+htit)

        # Nhits
        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        pad.Draw()
        pad.Divide(2,2)
        pad.cd(1)
        HISTS[ref]['nMuonHits'].Draw("hist")
        pad.cd(2)
        HISTS[ref]['nDTCSCHits'].Draw("hist")
        pad.cd(3)
        HISTS[ref]['nDTHits'].Draw("hist")
        pad.cd(4)
        HISTS[ref]['nCSCHits'].Draw("hist")
#        HISTS[ref]['nRPCHits'].Draw("hist")
        canvas.Print(fname, "Title:total number of hits")

        # Nhits for various Nstations
        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        pad.Draw()
        pad.Divide(2,2)
        for istat in range(1,5):
            pad.cd(istat)
            htit = 'nMuonHits_'+str(istat)+'Stat'
            HISTS[ref][htit].Draw("hist")
        canvas.Print(fname, "Title:muon hits per station")

        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        pad.Draw()
        pad.Divide(2,2)
        for istat in range(1,5):
            pad.cd(istat)
            htit = 'nRPCHits_'+str(istat)+'Stat'
            HISTS[ref][htit].Draw("hist")
        canvas.Print(fname, "Title:RPC hits per station")

        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        pad.Draw()
        pad.Divide(2,2)
        for istat in range(1,5):
            pad.cd(istat)
            htit = 'nCSCHits_vs_nDTHits_'+str(istat)+'Stat'
            HISTS[ref][htit].Draw("text")
        canvas.Print(fname, "Title:CSC hits vs DT hits, per station")

        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        pad.Draw()
        pad.Divide(2,2)
        for istat in range(1,5):
            pad.cd(istat)
            htit = 'nDTCSCHits_'+str(istat)+'Stat'
            HISTS[ref][htit].Draw("hist")
        canvas.Print(fname, "Title:DT+CSC hits per station, lin scale")

        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        gStyle.SetOptLogy(1)
        pad.Draw()
        pad.Divide(2,2)
        for istat in range(1,5):
            pad.cd(istat)
            htit = 'nDTCSCHits_'+str(istat)+'Stat'
            HISTS[ref][htit].Draw("hist")
        gStyle.SetOptLogy(0)
        canvas.Print(fname, "Title:DT+CSC hits per station, log scale")

        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        pad.Draw()
        pad.Divide(2,2)
        for istat in range(1,5):
            pad.cd(istat)
            htit = 'nDTHits_'+str(istat)+'Stat'
            HISTS[ref][htit].Draw("hist")
        canvas.Print(fname, "Title:DT hits per station, lin scale")

        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        gStyle.SetOptLogy(1)
        pad.Draw()
        pad.Divide(2,2)
        for istat in range(1,5):
            pad.cd(istat)
            htit = 'nDTHits_'+str(istat)+'Stat'
            HISTS[ref][htit].Draw("hist")
        gStyle.SetOptLogy(0)
        canvas.Print(fname, "Title:DT hits per station, log scale")

        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        pad.Draw()
        pad.Divide(2,2)
        for istat in range(1,5):
            pad.cd(istat)
            htit = 'nCSCHits_'+str(istat)+'Stat'
            HISTS[ref][htit].Draw("hist")
        canvas.Print(fname, "Title:CSC hits per station, lin scale")

        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        gStyle.SetOptLogy(1)
        pad.Draw()
        pad.Divide(2,2)
        for istat in range(1,5):
            pad.cd(istat)
            htit = 'nCSCHits_'+str(istat)+'Stat'
            HISTS[ref][htit].Draw("hist")
        gStyle.SetOptLogy(0)
        canvas.Print(fname, "Title:CSC hits per station, log scale")

        # pT resolutions for groups of 3 DT+CSC hits
        htot = 17
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'pTres_DTCSChits_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:pT res for groups of 3 hits")

        # pT res for groups of 3 hits, N(stat) > 1
        htot = 8
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'pTres_DTCSChits_Stat234_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:pT res for groups of 3 hits, N(stat) > 1")

        # pT res for 12-19 DTCSC hits, N(stat) > 1
        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        pad.Draw()
        pad.Divide(4,2)
        for ihits in range(12,20):
            pad.cd(ihits-11)
            htit = 'pTres_Stat234_'+str(ihits)+'DTCSChits'
            HISTS[ref][htit].Draw("hist")
        canvas.Print(fname, "Title:pT res for 12-19 DTCSC hits, N(stat) > 1")

        # resolutions in barrel, endcap, and overlap
        htot = 8 # hist8 and hist9 are empty
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'pTres_DThits_barrel_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:pT res for groups of 6 hits, barrel")

        htot = 10
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'pTres_CSChits_endcap_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:pT res for groups of 3 hits, endcap")

        htot = 8 # hist8 and hist9 are empty
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'pTres_DTCSChits_overlap_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:pT res for groups of 6 hits, overlap")

        # 1/pT resolutions for groups of 3 DT+CSC hits
        htot = 17
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'invpTres_DTCSChits_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:1/pT res for groups of 3 hits")

        # 1/pT resolutions for groups of 3 hits, N(stat) > 1
        htot = 8
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'invpTres_DTCSChits_Stat234_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:1/pT res for groups of 3 hits, N(stat) > 1")

        # charge difference for groups of 3 hits
        htot = 17
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'qdif_DTCSChits_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:q dif for groups of 3 hits")

        # charge difference for groups of 3 hits, N(stat) > 1
        htot = 8
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'qdif_DTCSChits_Stat234_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:q dif for groups of 3 hits, N(stat) > 1")

        # charge difference for 12-19 DTCSC hits, N(stat) > 1
        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        pad.Draw()
        pad.Divide(4,2)
        for ihits in range(12,20):
            pad.cd(ihits-11)
            htit = 'qdif_Stat234_'+str(ihits)+'DTCSChits'
            HISTS[ref][htit].Draw("hist")
        canvas.Print(fname, "Title:q dif for 12-19 DTCSC hits, N(stat) > 1")

        # d0 difference for groups of 3 hits
        htot = 17
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'd0dif_DTCSChits_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:d0 dif for groups of 3 hits")

        # d0 difference for groups of 6 hits in barrel, endcap, and overlap
        htot = 8 # hist8 and hist9 are empty
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'd0dif_DThits_barrel_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:d0 dif for groups of 6 hits, barrel")

        htot = 10
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'd0dif_CSChits_endcap_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:d0 dif for groups of 3 hits, endcap")

        htot = 8 # hist8 and hist9 are empty
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'd0dif_DTCSChits_overlap_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:d0 dif for groups of 6 hits, overlap")

        # d0 difference for groups of 3 hits, N(stat) > 1
        htot = 8
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'd0dif_DTCSChits_Stat234_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:d0 dif for groups of 3 hits, N(stat) > 1")

        # sigma(pt)/pt vs chi2/ndof
        canvas.Clear()
        htit = 'dpt_over_pt_vs_chi2_over_ndof'
        HISTS[ref][htit].Draw("")
        canvas.Print(fname, "Title:"+htit)

        # sigma(pT)/pT per station
        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        pad.Draw()
        pad.Divide(2,2)
        for istat in range(1,5):
            pad.cd(istat)
            htit = 'dpt_over_pt_'+str(istat)+'Stat'
            HISTS[ref][htit].Draw("hist")
        canvas.Print(fname, "Title:sigma(pT)/pT per station, lin scale")

        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        gStyle.SetOptLogy(1)
        pad.Draw()
        pad.Divide(2,2)
        for istat in range(1,5):
            pad.cd(istat)
            htit = 'dpt_over_pt_'+str(istat)+'Stat'
            HISTS[ref][htit].Draw("hist")
        gStyle.SetOptLogy(0)
        canvas.Print(fname, "Title:sigma(pT)/pT per station, log scale")

        # sigma(pT)/pT for groups of 3 hits
        htot = 17
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'dpt_over_pt_DTCSChits_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:sigma(pT)/pT for groups of 3 hits")

        # sigma(pT)/pT for groups of 3 hits, N(stat) > 1
        htot = 8
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'dpt_over_pt_DTCSChits_Stat234_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:sigma(pT)/pT for groups of 3 hits, N(stat) > 1")

        # pT resolution in slices of sigma(pT)/pT
        htot = 10
        for ihist in range(0,htot):
            ipad = ihist%10
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(5,2)
            pad.cd(ipad+1)
            htit = 'pTres_for_dpt_over_pt_hist'+str(ihist)
            HISTS[ref][htit].Fit("gaus","Q")
#            HISTS[ref][htit].Draw("hist")
            if ipad == 9 or ihist == htot-1:
                canvas.Print(fname, "Title:pT res in slices of sigma(pT)/pT")

        # pT resolution in slices of sigma(pT)/pT, Nhits > 12
        htot = 10
        for ihist in range(0,htot):
            ipad = ihist%10
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(5,2)
            pad.cd(ipad+1)
            htit = 'pTres_for_dpt_over_pt_passed_hist'+str(ihist)
            HISTS[ref][htit].Fit("gaus","Q")
#            HISTS[ref][htit].Draw("hist")
            if ipad == 9 or ihist == htot-1:
                canvas.Print(fname, "Title:pT res in slices of sigma(pT)/pT, Nhits > 12")

        # pT pull in slices of sigma(pT)/pT
        htot = 10
        for ihist in range(0,htot):
            ipad = ihist%10
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(5,2)
            pad.cd(ipad+1)
            htit = 'pTpull_for_dpt_over_pt_hist'+str(ihist)
#            HISTS[ref][htit].Fit("gaus","Q")
            HISTS[ref][htit].Draw("hist")
            if ipad == 9 or ihist == htot-1:
                canvas.Print(fname, "Title:pT pull in slices of sigma(pT)/pT")

        # chi2/ndof per station
        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        pad.Draw()
        pad.Divide(2,2)
        for istat in range(1,5):
            pad.cd(istat)
            htit = 'chi2_over_ndof_'+str(istat)+'Stat'
            HISTS[ref][htit].Draw("hist")
        canvas.Print(fname, "Title:chi2/ndof per station, lin scale")

        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        gStyle.SetOptLogy(1)
        pad.Draw()
        pad.Divide(2,2)
        for istat in range(1,5):
            pad.cd(istat)
            htit = 'chi2_over_ndof_'+str(istat)+'Stat'
            HISTS[ref][htit].Draw("hist")
        gStyle.SetOptLogy(0)
        canvas.Print(fname, "Title:chi2/ndof per station, log scale")

        # chi2/ndof for groups of 3 hits
        htot = 17
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'chi2_over_ndof_DTCSChits_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:chi2/ndof for groups of 3 hits")

        # chi2/ndof for groups of 3 hits, N(stat) > 1
        htot = 8
        for ihist in range(0,htot):
            ipad = ihist%8
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(4,2)
            pad.cd(ipad+1)
            htit = 'chi2_over_ndof_DTCSChits_Stat234_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
            if ipad == 7 or ihist == htot-1:
                canvas.Print(fname, "Title:chi2/ndof for groups of 3 hits, N(stat) > 1")

        # pT resolution in slices of chi2/ndof
        htot = 10
        for ihist in range(0,htot):
            ipad = ihist%10
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(5,2)
            pad.cd(ipad+1)
            htit = 'pTres_for_chi2_over_ndof_hist'+str(ihist)
            HISTS[ref][htit].Fit("gaus","Q")
#            HISTS[ref][htit].Draw("hist")
            if ipad == 9 or ihist == htot-1:
                canvas.Print(fname, "Title:pT res in slices of chi2/ndof")

        # pT resolution in slices of chi2/ndof, Nhits > 12
        htot = 10
        for ihist in range(0,htot):
            ipad = ihist%10
            if ipad == 0:
                canvas.Clear()
                pad = R.TPad('pad','pad', 0, 0, 1, 1)
                pad.Draw()
                pad.Divide(5,2)
            pad.cd(ipad+1)
            htit = 'pTres_for_chi2_over_ndof_passed_hist'+str(ihist)
            HISTS[ref][htit].Fit("gaus","Q")
#            HISTS[ref][htit].Draw("hist")
            if ipad == 9 or ihist == htot-1:
                canvas.Print(fname, "Title:pT res in slices of chi2/ndof, Nhits > 12")

        # placeholder for future histograms
        canvas.Clear()
        pad = R.TPad('pad','pad', 0, 0, 1, 1)
        pad.Draw()
        pad.Divide(4,2)
        for ihist in range(16,17):
            pad.cd(ihist-15)
            htit = 'pTres_DTCSChits_hist'+str(ihist)
            HISTS[ref][htit].Draw("hist")
        canvas.Print(fname+")", "Title:placeholder")

if True:
    makePerSamplePlots()
