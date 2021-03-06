import sys
import re
import numpy as np
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter

# output_folder = "pdfs/simulation-validation_comparison-plots/"
output_folder = "pdfs/reHLT-validation-plots_Cosmics-vs-NoBPTX_fullStats/"
output_formats = [".pdf", ".root"]

lumi_str = "2016 Cosmics / MC samples"
# lumi_str = "2016 cosmics events"

L1T_info = "Data taken with L1_SingleMuOpen"
HLT_info = "Ref. path: HLT_L2Mu10_NoVertex_[pp|CosmicSeed] (re-HLT)"

# specify a list of patterns to plot, and a corresponding list of strings to exclude
hist_patterns_and_excludes = (
    ("DSA_lowerLeg__L1pTresVAR", ["_0p0alpha", "_0p3alpha", "_2p8alpha"]),
    ("DSA_lowerLeg__L2pTresVAR", ["_0p0alpha", "_0p3alpha", "_2p8alpha"]),
    # ("L2pTresVAR", ["_0p0alpha", "_0p3alpha", "_2p8alpha"]),
    ("__pTVAR",   ["_0p0alpha", "_0p3alpha", "_2p8alpha"]),  # include if pT mean should be on the canvases
    ("__etaVAR",   ["_0p0alpha", "_0p3alpha", "_2p8alpha"]),  # include if eta mean should be on the canvases
    ("__d0VAR",   ["_0p0alpha", "_0p3alpha", "_2p8alpha"]),  # include if d0 mean should be on the canvases
)

# specify ((color, linestyle, markerstyle), file names, description)
file_specs = (
    # # compare GMT modes / JSONs (for lower legs)
    # (
    #     (R.kBlue, 1, None),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-base_HLT-CosmicSeed_lowerLeg.root",
    #     "base GMT mode (cosmic seed, lower leg)",
    # ),
    # (
    #     (R.kBlue, 2, 24),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-bottomOnly_HLT-CosmicSeed_lowerLeg.root",
    #     "bottomOnly GMT mode (cosmic seed, lower leg)",
    # ),
    # (
    #     (R.kRed, 1, None),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-base_HLT-ppSeed_lowerLeg.root",
    #     "base GMT mode (pp seed, lower leg)",
    # ),
    # (
    #     (R.kRed, 2, 24),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-bottomOnly_HLT-ppSeed_lowerLeg.root",
    #     "bottomOnly GMT mode (pp seed, lower leg)",
    # ),
    #
    # # compare legs (for base GMT modes)
    # (
    #     (R.kBlue, 1, None),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-base_HLT-CosmicSeed_lowerLeg.root",
    #     "lower leg (cosmic seed, base GMT mode)",
    # ),
    # (
    #     (R.kBlue, 2, 24),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-base_HLT-CosmicSeed_upperLeg.root",
    #     "upper leg (cosmic seed, base GMT mode)",
    # ),
    # (
    #     (R.kRed, 1, None),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-base_HLT-ppSeed_lowerLeg.root",
    #     "lower leg (pp seed, base GMT mode)",
    # ),
    # (
    #     (R.kRed, 2, 24),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-base_HLT-ppSeed_upperLeg.root",
    #     "upper leg (pp seed, base GMT mode)",
    # ),
    #
    # # validate re-HLT
    # (
    #     (R.kBlue, 1, None),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_L1emulatorFixed_JSONsubset-for-NoBPTX-comparison/Cosmics2016_UGMT-base_HLT-CosmicSeed_lowerLeg.root",
    #     "Cosmics re-HLT samples (cosmic seed, lower leg)",
    # ),
    # (
    #     (R.kBlue, 2, 24),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_L1emulatorFixed_JSONsubset-for-NoBPTX-comparison/NoBPTX2016_HLT-CosmicSeed_lowerLeg.root",
    #     "NoBPTX samples (cosmic seed, lower leg)",
    # ),
    #
    # validate simulation
    (
        (R.kBlue, 2, 24),
        "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-CosmicSeed_Leg_etaLT1p2_nCSCDTHitsGT12_nStationsGT1_pTSigLT1p0_oneLegMatched_HTo2XTo2Mu2J_reHLT_CosmicSeed_125_20_merged.root",
        # "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-CosmicSeed_merged.root",
        "m_{H} = 125 GeV, m_{X} = 20 GeV (MC, cosmic seed)",
    ),
    (
        (R.kBlue, 1, 24),
        "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-CosmicSeed_Leg_etaLT1p2_nCSCDTHitsGT12_nStationsGT1_pTSigLT1p0_oneLegMatched_HTo2XTo2Mu2J_reHLT_CosmicSeed_125_50_merged.root",
        # "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-CosmicSeed_merged.root",
        "m_{H} = 125 GeV, m_{X} = 50 GeV (MC, cosmic seed)",
    ),
    (
        (R.kBlue, 2, 28),
        "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-CosmicSeed_Leg_etaLT1p2_nCSCDTHitsGT12_nStationsGT1_pTSigLT1p0_oneLegMatched_HTo2XTo2Mu2J_reHLT_CosmicSeed_200_20_merged.root",
        # "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-CosmicSeed_merged.root",
        "m_{H} = 200 GeV, m_{X} = 20 GeV (MC, cosmic seed)",
    ),
    (
        (R.kBlue, 2, 28),
        "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-CosmicSeed_Leg_etaLT1p2_nCSCDTHitsGT12_nStationsGT1_pTSigLT1p0_oneLegMatched_HTo2XTo2Mu2J_reHLT_CosmicSeed_200_50_merged.root",
        # "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-CosmicSeed_merged.root",
        "m_{H} = 200 GeV, m_{X} = 50 GeV (MC, cosmic seed)",
    ),
    (
        (R.kBlack, 1, None),
        "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_Cosmics2016/Cosmics2016_UGMT-bottomOnly_HLT-CosmicSeed.root",
        # "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-bottomOnly_HLT-CosmicSeed_lowerLeg.root",
        "Cosmics data (cosmic seed)",
    ),
    #
    # (
    #     (R.kRed, 2, 24),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-ppSeed_Leg_etaLT1p2_nCSCDTHitsGT12_nStationsGT1_pTSigLT1p0_oneLegMatched_HTo2XTo2Mu2J_reHLT_ppSeed_125_20_merged.root",
    #     # "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-ppSeed_merged.root",
    #     "m_{H} = 125 GeV, m_{X} = 20 GeV (MC, pp seed)",
    # ),
    # (
    #     (R.kRed, 1, 24),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-ppSeed_Leg_etaLT1p2_nCSCDTHitsGT12_nStationsGT1_pTSigLT1p0_oneLegMatched_HTo2XTo2Mu2J_reHLT_ppSeed_125_50_merged.root",
    #     # "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-ppSeed_merged.root",
    #     "m_{H} = 125 GeV, m_{X} = 50 GeV (MC, pp seed)",
    # ),
    # (
    #     (R.kRed, 2, 28),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-ppSeed_Leg_etaLT1p2_nCSCDTHitsGT12_nStationsGT1_pTSigLT1p0_oneLegMatched_HTo2XTo2Mu2J_reHLT_ppSeed_200_20_merged.root",
    #     # "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-ppSeed_merged.root",
    #     "m_{H} = 200 GeV, m_{X} = 20 GeV (MC, pp seed)",
    # ),
    # (
    #     (R.kRed, 2, 28),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-ppSeed_Leg_etaLT1p2_nCSCDTHitsGT12_nStationsGT1_pTSigLT1p0_oneLegMatched_HTo2XTo2Mu2J_reHLT_ppSeed_200_50_merged.root",
    #     # "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-ppSeed_merged.root",
    #     "m_{H} = 200 GeV, m_{X} = 50 GeV (MC, pp seed)",
    # ),
    # (
    #     (R.kBlack, 1, None),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_Cosmics2016/Cosmics2016_UGMT-bottomOnly_HLT-ppSeed.root",
    #     # "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-bottomOnly_HLT-ppSeed_lowerLeg.root",
    #     "Cosmics data (pp seed)",
    # ),

    # (
    #     (R.kRed, 2, 24),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-ppSeed_Leg_etaLT1p2_nCSCDTHitsGT12_nStationsGT1_pTSigLT1p0_oneLegMatched_HTo2XTo2Mu2J_reHLT_ppSeed_125_merged.root",
    #     # "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-ppSeed_merged.root",
    #     "m_{H} = 125 GeV MC signal samples (pp seed, lower leg)",
    # ),
    # (
    #     (R.kRed, 10, 28),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-ppSeed_Leg_etaLT1p2_nCSCDTHitsGT12_nStationsGT1_pTSigLT1p0_oneLegMatched_HTo2XTo2Mu2J_reHLT_ppSeed_200_merged.root",
    #     # "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_HTo2XTo2Mu2J_reHLT/HTo2XTo2Mu2J_reHLT_HLT-ppSeed_merged.root",
    #     "m_{H} = 200 GeV MC signal samples (pp seed, lower leg)",
    # ),
    # (
    #     (R.kBlack, 2, 24),
    #     "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/validate_signalMC_with_Cosmics_corrected/hadded_Cosmics2016/Cosmics2016_UGMT-bottomOnly_HLT-ppSeed.root",
    #     # "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-bottomOnly_HLT-CosmicSeed_lowerLeg.root",
    #     "Cosmics data (pp seed, lower leg)",
    # ),
)


def makeSimpleComparisonPlots(hist_patterns_and_excludes):
    p = {f: {"appearance": app, "descr": d, "plots": {}} for app, f, d in file_specs}
    h_d0 = {f: {} for __, f, __ in file_specs}  # stores d0 histograms for a given key
    h_eta = {f: {} for __, f, __ in file_specs}  # stores eta histograms for a given key
    h_pT = {f: {} for __, f, __ in file_specs}  # stores pT histograms for a given key
    p_norm = {
        f: {"appearance": app, "descr": d, "plots": {}} for app, f, d in file_specs
    }

    rebinning_exceptions = ()

    custom_xranges = {
        "pTresVAR": [-1, 5],
        "d0VAR": [0, 400],
    }

    hists = collectHistograms(file_specs, hist_patterns_and_excludes)

    # prepare the histograms
    for appearance, f, f_descr in file_specs:
        for key in hists[f]["hists"]:
            RT.addFlows(hists[f]["hists"][key])

            if not any([e in key for e in rebinning_exceptions]):
                if hists[f]["hists"][key].GetNbinsX() >= 1000:
                    hists[f]["hists"][key].Rebin(5)
                elif hists[f]["hists"][key].GetNbinsX() >= 100:
                    hists[f]["hists"][key].Rebin(2)
                else:
                    pass

            legName = f_descr

            p[f]["plots"][key] = Plotter.Plot(
                hists[f]["hists"][key], legName, "l", "hist"
            )

            # also store the d0 histogram corresponding to the current histogram,
            # if the corresponding d0 histogram is available
            if key not in h_d0[f]:
                d0_key = re.sub(r"__(.+)VAR", "__d0VAR", key)
                if d0_key in hists[f]["hists"]:
                    h_d0[f][key] = hists[f]["hists"][d0_key]

            # store the eta histogram corresponding to the current histogram
            if key not in h_eta[f]:
                eta_key = re.sub(r"__(.+)VAR", "__etaVAR", key)
                if eta_key in hists[f]["hists"]:
                    h_eta[f][key] = hists[f]["hists"][eta_key]

            # store the pT histogram corresponding to the current histogram
            if key not in h_pT[f]:
                pT_key = re.sub(r"__(.+)VAR", "__pTVAR", key)
                if pT_key in hists[f]["hists"]:
                    h_pT[f][key] = hists[f]["hists"][pT_key]

            h_norm = hists[f]["hists"][key].Clone()
            if h_norm.Integral() > 0:
                h_norm.Scale(1.0 / h_norm.Integral())
            else:
                pass

            p_norm[f]["plots"][key] = Plotter.Plot(
                h_norm, legName, "l", "hist"
            )

    for plots, suffix in ((p_norm, "_norm"), (p, "")):
        for is_logy in (False, True):
            for key in hists[hists.keys()[0]]["hists"]:

                canvas = Plotter.Canvas(logy=is_logy, lumi=lumi_str)

                statsboxes = {}  # keep references to stats boxes so they don't vanish

                cnt_file = -1  # keeps track of the number of processed files
                for f in hists:
                    cnt_file += 1
                    canvas.addMainPlot(plots[f]["plots"][key])
                    RT.addBinWidth(plots[f]["plots"][key])
                    plots[f]["plots"][key].SetLineColor(plots[f]["appearance"][0])
                    plots[f]["plots"][key].SetLineStyle(plots[f]["appearance"][1])
                    if plots[f]["appearance"][2] is not None:
                        plots[f]["plots"][key].SetMarkerStyle(plots[f]["appearance"][2])

                    statsboxes[f] = canvas.makeStatsBox(
                            plots[f]["plots"][key],
                            color=plots[f]["appearance"][0],
                            entries=('nentries'))
                    Plotter.MOVE_OBJECT(statsboxes[f], Y=-.04*(len(statsboxes)-1) - 0.1)

                if legName != "":
                    canvas.makeLegend(lWidth=0.3, pos="br", fontscale=0.77)
                    canvas.legend.resizeHeight()
                    canvas.legend.moveLegend(X=-0.25, Y=+0.15)

                # pave_triggerinfo = R.TPaveText(0.28, 0.75, 0.9, 0.9, "NDCNB")
                # pave_triggerinfo.SetTextAlign(13)
                # pave_triggerinfo.SetTextFont(42)
                # # pave_triggerinfo.SetTextSize(self.fontsize*.9)
                # pave_triggerinfo.SetMargin(0)
                # pave_triggerinfo.SetFillStyle(0)
                # pave_triggerinfo.SetFillColor(0)
                # pave_triggerinfo.SetLineStyle(0)
                # pave_triggerinfo.SetLineColor(0)
                # pave_triggerinfo.SetBorderSize(0)
                # pave_triggerinfo.AddText(0.0, 1.0, HLT_info)
                # pave_triggerinfo.AddText(0.0, 0.5, L1T_info)
                # pave_triggerinfo.Draw()

                # d0min_searchres = re.search(r"__d0GT(\d+p\d+|\d+)", key)
                # if d0min_searchres:
                #     d0min = d0min_searchres.group(1).replace("p", ".")
                # else:
                #     d0min = None

                # d0max_searchres = re.search(r"__d0LT(\d+p\d+|\d+)", key)
                # if d0max_searchres:
                #     d0max = d0max_searchres.group(1).replace("p", ".")
                # else:
                #     d0max = None

                # if d0min is not None and d0max is not None:
                #     selection_str = R.TLatex()
                #     selection_str.SetTextSize(0.035)
                #     selection_str.DrawLatexNDC(
                #         0.4, 0.73, "{} cm  < d_{{0}} < {} cm".format(d0min, d0max)
                #     )

                # find the corresponding d0 distribution in the given d0 bin
                # and display its mean
                current_var = re.search(r"__(.+)VAR", key)
                if current_var:
                    current_var = current_var.group(1)
                # current_var = re.findall(r"__(.+)VAR", key)
                # if len(current_var) == 1:
                    # current_var = current_var[0].split("_")[-1]
                    if all([c in key for c in ("__d0GT", "__d0LT")]):
                        cnt_d0infos = 0
                        pave_d0info = {}

                        for f in hists:
                            d0_distribution = h_d0[f][key]
                            d0_hist = key.replace("__{}VAR".format(current_var), "__d0VAR")
                            d0_mean = d0_distribution.GetMean()

                            pT_mean = h_pT[f][key].GetMean()

                            # eta_mean = h_eta[f][key].GetMean()
                            # eta_mean = mean([h_eta[f][key].GetBinContent(i) for i in range(1, h_eta[f][key].GetNbinsX()+1)])
                            eta_absmean = 0.0
                            for i in range(1, h_eta[f][key].GetNbinsX()+1):
                                if h_eta[f][key].GetXaxis().GetBinCenter(i) < 0:
                                    eta_absmean += (-1) * h_eta[f][key].GetXaxis().GetBinCenter(i) * h_eta[f][key].GetBinContent(i)
                                else:
                                    eta_absmean += h_eta[f][key].GetXaxis().GetBinCenter(i) * h_eta[f][key].GetBinContent(i)

                            eta_mean = eta_absmean / h_eta[f][key].GetEntries()

                            d0_min = re.findall(r"__d0GT(\d+)p(\d+)", d0_hist)
                            if len(d0_min) > 0:
                                d0_min = float("{}.{}".format(d0_min[0][0], d0_min[0][1]))
                            else:
                                d0_min = float(re.findall(r"__d0GT(\d+)", d0_hist)[0])

                            d0_max = re.findall(r"__d0LT(\d+)p(\d+)", d0_hist)
                            if len(d0_max) > 0:
                                d0_max = float("{}.{}".format(d0_max[0][0], d0_max[0][1]))
                            else:
                                d0_max = float(re.findall(r"__d0LT(\d+)", d0_hist)[0])

                            d0info_width = 0.15
                            d0info_height = 0.14

                            pave_d0info[f] = R.TPaveText(
                                0.15 + cnt_d0infos * d0info_width,
                                0.75, # + cnt_d0infos * d0info_height,
                                0.15 + (cnt_d0infos+1) * d0info_width,
                                0.75 + d0info_height, # + (cnt_d0infos+1) * d0info_height,
                                "NDCNB"
                            )
                            pave_d0info[f].SetTextAlign(13)
                            pave_d0info[f].SetTextFont(42)
                            pave_d0info[f].SetMargin(0)
                            pave_d0info[f].SetFillStyle(0)
                            pave_d0info[f].SetFillColor(0)
                            pave_d0info[f].SetLineStyle(0)
                            pave_d0info[f].SetLineColor(0)
                            pave_d0info[f].SetBorderSize(0)
                            pave_d0info[f].SetTextColor(hists[f]["appearance"][0])
                            pave_d0info[f].AddText(
                                0.0, 1.0, "{} cm < d_{{0}} < {} cm".format(d0_min, d0_max)
                            )
                            pave_d0info[f].AddText(
                                0.0, .66, "#LTd_{{0}}#GT = {:4.3f} cm".format(d0_mean)
                            )
                            pave_d0info[f].AddText(
                                0.0, .33, "#LTp_{{T}}#GT = {:4.3f} GeV".format(pT_mean)
                            )
                            pave_d0info[f].AddText(
                                0.0, 0.0, "#LT|#eta|#GT = {:4.3f}".format(eta_mean)
                            )
                            pave_d0info[f].Draw()

                            cnt_d0infos += 1
                
                # set custom x axis range if so specified in the variable custom_xranges
                for var in custom_xranges:
                    if var in key:
                        canvas.firstPlot.GetXaxis().SetRangeUser(
                            custom_xranges[var][0],
                            custom_xranges[var][1]
                        )
                        break

                if "norm" in suffix:
                    if is_logy:
                        canvas.firstPlot.GetYaxis().SetRangeUser(1e-3, 0.5)
                    else:
                        canvas.firstPlot.GetYaxis().SetRangeUser(0.0, 0.5)

                if "norm" in suffix:
                    canvas.firstPlot.GetYaxis().SetTitle(
                        "Normalized " + canvas.firstPlot.GetYaxis().GetTitle()
                    )

                fname = "{}/{}{}{}".format(
                    output_folder, key, "_logy" if is_logy else "", suffix
                )

                canvas.finishCanvas()
                canvas.save(fname, extList=output_formats)
                canvas.deleteCanvas()

    del hists


def makeTurnOnComparisonPlots():
    turnOn_patterns_and_excludes = (
        ("__pTVAREff", ["DSA__pTVAREff", "upperLeg", "_0p0alpha", "_0p3alpha", "_2p8alpha"]),
        # do not list any other tuples here, they will not be processed
    )

    # these intervals must be equal (or a subset) of the ones defined in the
    # ../analyzers/cosmicsPlots.py script
    d0intervals = [(None, None)]
    # d0intervals += [(i,i+2.5) for i in np.arange(0., 10., 2.5)]
    # d0intervals += [(i,i+5.0) for i in np.arange(0., 20., 5.0)]
    # d0intervals += [(i,i+10.0) for i in np.arange(20., 100., 10.0)]
    d0intervals += [
        (0, 10),
        (0, 50),
        (10, 50),
        (50, 100),
        (100, 150),
        (150, 250),
        (250, 350),
        (250, 1000),
    ]

    hists = collectHistograms(file_specs, turnOn_patterns_and_excludes)

    # prepare the histograms
    for app, f, f_descr in file_specs:
        for key in hists[f]["hists"]:
            RT.addFlows(hists[f]["hists"][key])

            if hists[f]["hists"][key].GetNbinsX() >= 1000:
                hists[f]["hists"][key].Rebin(5)
            elif hists[f]["hists"][key].GetNbinsX() >= 100:
                hists[f]["hists"][key].Rebin(5)
            else:
                pass

            legName = f_descr

    for d0min, d0max in d0intervals:
        hden = {f: {} for __, f, __ in file_specs}
        hnum = {f: {} for __, f, __ in file_specs}
        p = {
            f: {"appearance": app, "descr": d, "plots": {}} for app, f, d in file_specs
        }
        g = {
            f: {"appearance": app, "descr": d, "plots": {}} for app, f, d in file_specs
        }

        for app, f, f_descr in file_specs:
            if d0min is None or d0max is None:
                hnums = [
                    h
                    for h in hists[f]["hists"]
                    if turnOn_patterns_and_excludes[0][0] + "Num" in h
                    and not any([d0_str in h for d0_str in ("__d0GT", "__d0LT")])
                ]
                hdens = [
                    h
                    for h in hists[f]["hists"]
                    if turnOn_patterns_and_excludes[0][0] + "Den" in h
                    and not any([d0_str in h for d0_str in ("__d0GT", "__d0LT")])
                ]

            else:
                hnums = [
                    h
                    for h in hists[f]["hists"]
                    if all(
                        [
                            s in h
                            for s in (
                                turnOn_patterns_and_excludes[0][0] + "Num",
                                "__d0GT" + str(d0min).replace(".", "p"),
                                "__d0LT" + str(d0max).replace(".", "p"),
                            )
                        ]
                    )
                ]

                hdens = [
                    h
                    for h in hists[f]["hists"]
                    if all(
                        [
                            s in h
                            for s in (
                                turnOn_patterns_and_excludes[0][0] + "Den",
                                "__d0GT" + str(d0min).replace(".", "p"),
                                "__d0LT" + str(d0max).replace(".", "p"),
                            )
                        ]
                    )
                ]

            for hname in hnums:
                current_hist = hists[f]["hists"][hname].Clone()
                current_hist.SetDirectory(0)
                current_hist.Sumw2()
                RT.addFlows(current_hist)

                if hname not in hnum[f].keys():
                    hnum[f][hname] = current_hist
                else:
                    hnum[f][hname].Add(current_hist)

            for hname in hdens:
                current_hist = hists[f]["hists"][hname].Clone()
                current_hist.SetDirectory(0)
                current_hist.Sumw2()
                RT.addFlows(current_hist)

                if hname not in hden[f].keys():
                    hden[f][hname] = current_hist
                else:
                    hden[f][hname].Add(current_hist)

        if len(hden[f]) > 1:
            raise NotImplementedError(
                "Too many denumerator histos - not yet implemented"
            )
        elif len(hden[f]) == 0:
            raise Exception("No denominator histogram found")

        # works only if consistency checks of the collectHistograms() function
        # pass (i.e., if all files have the same histogram content)
        for key in hnum[file_specs[0][1]]:
            canvas = Plotter.Canvas(lumi=lumi_str)

            cnt_file = 0  # keep track of the order of processed files
            for app, f, f_descr in file_specs:
                try:
                    hden[f] = hden[f][hden[f].keys()[0]]
                except:
                    pass

                g[f][key] = R.TGraphAsymmErrors(hnum[f][key], hden[f], "cp")
                g[f][key].SetNameTitle(
                    "g_" + f + "_" + key,
                    ";" + hnum[f][key].GetXaxis().GetTitle() + ";Efficiency",
                )
                p[f][key] = Plotter.Plot(g[f][key], f_descr, "elp", "pe")

                canvas.addMainPlot(p[f][key])
                p[f][key].setColor(app[0])
                if app[2] is not None:
                    p[f][key].SetMarkerStyle(app[2])

                cnt_file += 1

            canvas.makeLegend(pos="br", fontscale=0.77)
            canvas.legend.moveLegend(X=-0.45, Y=0.08)
            canvas.legend.resizeHeight()
            canvas.firstPlot.GetXaxis().SetRangeUser(0.0, 150.0)
            canvas.firstPlot.GetYaxis().SetRangeUser(0.0, 1.055)

            # L2pTcut = re.findall(r"_pTGT(\d+)p(\d+)", key)
            L2pTcut = re.findall(r"_L2pTGT(\d+)p(\d+)", key)
            if len(L2pTcut) > 1:
                raise Exception(
                    "Ambiguitites in L2 pT threshold "
                    "identification: {}".format(L2pTcut)
                )
            L2pTcut = float(".".join(L2pTcut[0]))
            pTthreshold_str = R.TLatex()
            pTthreshold_str.SetTextSize(0.035)
            pTthreshold_str.DrawLatex(
                100.0, 0.75, "p_{{T}}^{{L2}} > {} GeV".format(L2pTcut)
            )

            if L2pTcut > 0.0:
                L2vline = R.TLine(L2pTcut, 1.0, 150.0, 1.0)
                R.SetOwnership(L2vline, 0)
                L2vline.SetLineColor(15)
                L2vline.SetLineStyle(1)
                L2vline.Draw()

            L1pTcut = re.findall(r"_L1pTGT(\d+)p(\d+)", key)
            if len(L1pTcut) > 1:
                raise Exception(
                    "Ambiguities in L1 pT threshold identification: {}".format(L1pTcut)
                )
            elif len(L1pTcut) == 0:
                raise Exception("No L1 pT threshold identified in {}".format(key))

            L1pTcut = float(".".join(L1pTcut[0]))
            pTthreshold_str = R.TLatex()
            pTthreshold_str.SetTextSize(0.035)
            pTthreshold_str.DrawLatex(
                100.0, 0.66, "p_{{T}}^{{L1}} > {} GeV".format(L1pTcut)
            )

            if L1pTcut > 0.0:
                L1vline = R.TLine(
                    L1pTcut, 1.0, (L2pTcut if L2pTcut > 0.0 else 150.0), 1.0
                )
                R.SetOwnership(L1vline, 0)
                L1vline.SetLineColor(15)
                L1vline.SetLineStyle(3)
                L1vline.Draw()

            if d0min is not None and d0max is not None:
                selection_str = R.TLatex()
                selection_str.SetTextSize(0.035)
                selection_str.DrawLatex(
                    100.0, 0.57, "{} cm  < d_{{0}} < {} cm".format(d0min, d0max)
                )

            pave_triggerinfo = R.TPaveText(0.4, 0.11, 0.92, 0.28, "NDCNB")
            pave_triggerinfo.SetTextAlign(13)
            pave_triggerinfo.SetTextFont(42)
            # pave_triggerinfo.SetTextSize(self.fontsize*.9)
            pave_triggerinfo.SetMargin(0)
            pave_triggerinfo.SetFillStyle(0)
            pave_triggerinfo.SetFillColor(0)
            pave_triggerinfo.SetLineStyle(0)
            pave_triggerinfo.SetLineColor(0)
            pave_triggerinfo.SetBorderSize(0)
            pave_triggerinfo.AddText(0.0, 1.0, HLT_info)
            pave_triggerinfo.AddText(0.0, 0.5, L1T_info)
            pave_triggerinfo.Draw()

            fname = "{}/TETurnOn_{}".format(output_folder, key)

            canvas.finishCanvas()
            canvas.save(fname, extList=output_formats)
            canvas.deleteCanvas()

    del hists


def collectHistograms(file_specs, hist_patterns_and_excludes):

    # structure for storing the histograms
    h = {f: {"appearance": app, "descr": d, "hists": {}} for app, f, d in file_specs}

    # lists of keys for each file (for consistency checks)
    lists_of_keys = {f: [] for __, f, __ in file_specs}

    cnt = 1
    for __, f, __ in file_specs:
        print ("[{}/{}] Reading file {}...".format(cnt, len(file_specs), f))
        cnt += 1

        f_hists = HistogramGetter.getHistograms(f)

        for pattern, exclude in hist_patterns_and_excludes:

            for dataset in f_hists:
                selected_hists_names = getHistNames(
                    f_hists, dataset, pattern, exclude=exclude
                )

                for key in selected_hists_names:
                    if key not in h[f]["hists"]:
                        h[f]["hists"][key] = f_hists[dataset][key].Clone()
                    else:
                        h[f]["hists"][key].Add(f_hists[dataset][key])

                    lists_of_keys[f].append(key)

        print ("\tImported {} histograms".format(len(h[f]["hists"].keys())))

    # check whether all the histograms exist in all the files
    found_inconsistency = False
    for i, f in enumerate(lists_of_keys):
        for j in range(len(lists_of_keys.keys())):
            if i == j:
                continue

            for key in lists_of_keys[f]:
                if key not in lists_of_keys[lists_of_keys.keys()[j]]:
                    print (
                        "[WARNING] Inconsistency in file contents. "
                        "Histogram {} not present in file {}".format(
                            key, lists_of_keys.keys()[j]
                        )
                    )
                    found_inconsistency = True

    if not found_inconsistency:
        print ("[INFO] Consistency checks passed")
    else:
        print ("[WARNING] Consistency checks failed")

    return h


def getHistNames(hists, dataset, *args, **kwargs):
    logic = kwargs.pop("logic", "and")
    exclude_list = kwargs.pop("exclude", None)
    if kwargs:
        raise Exception("Invalid argument(s): {}".format(kwargs))

    exclude = None
    if exclude_list is not None:
        exclude = re.compile("|".join([e for e in exclude_list]))

    results = []
    for key in hists[dataset]:
        if exclude is not None and exclude.search(key):
            continue

        is_match = False
        if logic == "and":
            if all([re.search(a, key) is not None for a in args]):
                is_match = True
            else:
                pass

        elif logic == "or":
            if any([re.search(a, key) is not None for a in args]):
                is_match = True
            else:
                pass

        else:
            raise Exception("logic must be either 'and' or 'or'")

        if is_match:
            results.append(key)

    return results


makeSimpleComparisonPlots(hist_patterns_and_excludes)

makeTurnOnComparisonPlots()
