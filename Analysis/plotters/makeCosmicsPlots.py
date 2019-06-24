import sys
import re
import numpy as np
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter


L1RESOLUTIONVARIABLES = ["L1pTres"]
L2RESOLUTIONVARIABLES = ["L2pTres"]

L1T_info = 'L1_SingleMuOpen'
HLT_info = 'HLT_L2Mu10_NoVertex_ppSeed'
# L1T_info = "L1_SingleMuOpen_NotBptxOR_3BX"
# HLT_info = "HLT_L2Mu10_NoVertex_NoBPTX3BX"

lumi = '2016 Cosmics data'
# lumi = '2016 MC signal samples'
dataset_fname = "_Cosmics2016"

RANGES = {
    "pTdiff": (-1.1, 10.0),
    "d0": (0.0, 200),
    "L1pTres": (-1.0, 8.0),
    "L2pTres": (-1.0, 8.0),
    "dimVtxChi2": (0.0, 60.0),
    "dimLxySig": (0.0, 230.0),
    "chi2": (0.0, 30.0),
    "pTSig": (0.0, 2.0),
    "nStations": (0.0, 10.0),
    "nCSCDTHits": (10.0, 60.0),
    "chargeprod": (-1.0, 2.0),
    "charge": (-1.0, 2.0),
}

HISTS = HistogramGetter.getHistograms(
    "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/simulation-validation/Cosmics2016_UGMT-bottomOnly_HLT-ppSeed.root"
)


def makePerSamplePlots(selection=None):
    rebinning_exceptions = ("pTdiff", "nCSCDTHits")

    h = {}
    p = {}
    for dataset in HISTS:
        if selection is not None:
            selected_hists_names = getHistNames(dataset, *selection)
        else:
            selected_hists_names = HISTS[dataset]

        for key in selected_hists_names:

            # do not plot empty histograms in the interest of plotting time
            if HISTS[dataset][key].GetEntries() == 0:
                continue

            if key not in h:
                h[key] = HISTS[dataset][key].Clone()
            else:
                h[key].Add(HISTS[dataset][key])

    for key in h:
        RT.addFlows(h[key])
        if h[key].GetNbinsX() >= 1000:
            if any(["__" + var + "VAR" in key for var in rebinning_exceptions]):
                print ("Do not rebin {}".format(key))
                pass
            else:
                if "__L1pTresVAR" in key or "__L2pTresVAR" in key:
                    h[key].Rebin(2)
                else:
                    h[key].Rebin(15)
        elif h[key].GetNbinsX() >= 100:
            if any(["__" + var + "VAR" in key for var in rebinning_exceptions]):
                print ("Do not rebin {}".format(key))
                pass
            else:
                h[key].Rebin(5)
        else:
            pass

        if "lowerHemisphere" in key:
            hs_req = "lower hemisphere"
        elif "upperHemisphere" in key:
            hs_req = "upper hemisphere"
        else:
            hs_req = None

        if "oppositeCharges" in key:
            pair_charge_req = "oppositely charged pairs"
        elif "equalCharges" in key:
            pair_charge_req = "equally charged pairs"
        else:
            pair_charge_req = None

        if "posCharge" in key:
            charge_req = "positive muon tracks"
        elif "negCharge" in key:
            charge_req = "negative muon tracks"
        else:
            charge_req = None

        legName = ""
        for req in (hs_req, pair_charge_req, charge_req):
            if req is not None:
                if legName != "":
                    legName += ", "
                legName += req

        p = Plotter.Plot(h[key], legName, "l", "hist")

        for is_logy in (True, False):
            fname = "pdfs/{}{}{}.pdf".format(
                key, dataset_fname, ("_logy" if is_logy else "")
            )

            canvas = Plotter.Canvas(logy=is_logy, lumi=lumi)
            canvas.addMainPlot(p)
            if legName != "":
                canvas.makeLegend(lWidth=0.25, pos="tl", fontscale=0.65)
                canvas.legend.resizeHeight()

            for var in RANGES:
                if "__{}VAR".format(var) in key:
                    canvas.firstPlot.GetXaxis().SetRangeUser(
                        RANGES[var][0], RANGES[var][1]
                    )

            p.SetLineColor(R.kBlue)
            RT.addBinWidth(p)

            # Gauss fit for L2 resolution plots
            if any(
                ["__{}VAR".format(var) in key for var in L1RESOLUTIONVARIABLES]
            ) or any(["__{}VAR".format(var) in key for var in L2RESOLUTIONVARIABLES]):

                # Trigger information for canvas
                pave_triggerinfo = R.TPaveText(0.56, 0.38, 0.88, 0.51, "NDCNB")
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

                fit_xmin, fit_xmax = findFitRange(h[key])
                func = R.TF1("f" + key, "gaus", fit_xmin, fit_xmax)
                func.SetParameters(10.0, -0.1, 0.5)
                func.SetLineStyle(2)
                func.SetLineColor(R.kBlue + 2)
                R.SetOwnership(func, 0)
                h[key].Fit("f" + key, "RQN")
                func.Draw("same")

                pave_gaus = R.TPaveText(0.56, 0.63, 0.88, 0.83, "NDCNB")
                pave_gaus.SetTextAlign(13)
                pave_gaus.SetTextFont(42)
                # pave_gaus.SetTextSize(self.fontsize*.9)
                pave_gaus.SetMargin(0)
                pave_gaus.SetFillStyle(0)
                pave_gaus.SetFillColor(0)
                pave_gaus.SetLineStyle(0)
                pave_gaus.SetLineColor(0)
                pave_gaus.SetBorderSize(0)
                pave_gaus.AddText(0.0, 1.0, "Gaussian fit around maximum:")
                pave_gaus.AddText(
                    0.06, 0.65, "Mean = {:2.3f}".format(func.GetParameter(1))
                )
                pave_gaus.AddText(
                    0.06, 0.45, "Sigma = {:2.3f}".format(func.GetParameter(2))
                )
                pave_gaus.AddText(
                    0.06, 0.25, "#chi^{{2}} = {:2.3f}".format(func.GetChisquare())
                )

                # count the histogram contents to the right of the upper
                # fit limit (to get an estimate for the content in the tail)
                h_content = 0
                h_content_tail = 0
                fit_xmax_bin = h[key].FindBin(fit_xmax)
                for b in range(1, h[key].GetNbinsX() + 1):
                    h_content += h[key].GetBinContent(b)
                    if b > fit_xmax_bin:
                        h_content_tail += h[key].GetBinContent(b)

                pave_gaus.AddText(
                    0.06,
                    0.05,
                    "Entries above {:2.2f} (max. fit range): {:2.1f}%".format(
                        fit_xmax, 100.0 * h_content_tail / h_content
                    ),
                )
                pave_gaus.Draw()

                try:
                    canvas.legend.moveLegend(X=0.393, Y=-0.01)
                except:
                    # continue if there is no legend
                    pass
            else:
                # Trigger information for canvas
                pave_triggerinfo = R.TPaveText(0.4, 0.75, 0.72, 0.88, "NDCNB")
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

                pave = canvas.makeStatsBox(p, color=R.kBlue)

            pave_triggerinfo.Draw()

            # find the corresponding d0 distribution in the given d0 bin
            # and display its mean
            try:
                current_var = re.findall(r"__(.+)VAR", key)
                if len(current_var) == 1:
                    current_var = current_var[0].split("_")[-1]
                    if current_var != "d0" and all(
                        [c in key for c in ("__d0GT", "__d0LT")]
                    ):
                        d0_hist = key.replace("__{}VAR".format(current_var), "__d0VAR")
                        for idataset, dataset in enumerate(HISTS):
                            if idataset == 0:
                                h_d0 = HISTS[dataset][d0_hist].Clone()
                            else:
                                h_d0.Add(HISTS[dataset][d0_hist])

                        d0_mean = h_d0.GetMean()
                        # d0_mean = HISTS[dataset][d0_hist].GetMean()

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

                        pave_d0info = R.TPaveText(0.56, 0.53, 0.88, 0.61, "NDCNB")
                        pave_d0info.SetTextAlign(13)
                        pave_d0info.SetTextFont(42)
                        pave_d0info.SetMargin(0)
                        pave_d0info.SetFillStyle(0)
                        pave_d0info.SetFillColor(0)
                        pave_d0info.SetLineStyle(0)
                        pave_d0info.SetLineColor(0)
                        pave_d0info.SetBorderSize(0)
                        pave_d0info.AddText(
                            0.0, 1.0, "{} cm < d_{{0}} < {} cm".format(d0_min, d0_max)
                        )
                        pave_d0info.AddText(
                            0.0, 0.0, "#LTd_{{0}}#GT = {:4.3f} cm".format(d0_mean)
                        )
                        pave_d0info.Draw()
            except KeyError:
                # not all of the histograms have d0 equivalents (e.g.,
                # 'oppositeCharges' pair histos,...)
                print (
                    "[PLOTTER WARNING] Error processing d0 information "
                    "for {}; will not be printed on canvas".format(key)
                )

            canvas.cleanup(fname)

    return


def makeTurnOnPlots():

    # these intervals must be equal (or a subset) of the ones defined in the
    # ../analyzers/cosmicsPlots.py script
    d0intervals = [(None, None)]
    # d0intervals += [(i,i+2.5) for i in np.arange(0., 10., 2.5)]
    # d0intervals += [(i,i+5.0) for i in np.arange(0., 20., 5.0)]
    # d0intervals += [(i,i+10.0) for i in np.arange(20., 100., 10.0)]
    d0intervals += [
        (0, 10),
        (10, 50),
        (50, 100),
        (100, 150),
        (150, 250),
        (250, 350),
        (250, 1000),
    ]

    for d0min, d0max in d0intervals:
        hden = {}
        hnum = {}
        p = {}
        g = {}
        for i, dataset in enumerate(HISTS):
            if d0min is None or d0max is None:
                hnums = getHistNames(
                    dataset, "DSA_lowerLeg", "pTVAREffNum", exclude=["d0GT", "d0LT", "alpha"]
                )
                hdens = getHistNames(
                    dataset, "DSA_lowerLeg", "pTVAREffDen", exclude=["d0GT", "d0LT", "alpha"]
                )
            else:
                hnums = getHistNames(
                    dataset,
                    "DSA_lowerLeg__pTVAREffNum",
                    "d0GT" + str(d0min).replace(".", "p"),
                    "d0LT" + str(d0max).replace(".", "p"),
                    exclude=["alpha"],
                )
                hdens = getHistNames(
                    dataset,
                    "DSA_lowerLeg__pTVAREffDen",
                    "d0GT" + str(d0min).replace(".", "p"),
                    "d0LT" + str(d0max).replace(".", "p"),
                    exclude=["alpha"],
                )

            for hname in hnums:
                current_hist = HISTS[dataset][hname].Clone()
                current_hist.SetDirectory(0)
                current_hist.Sumw2()
                RT.addFlows(current_hist)
                if current_hist.GetNbinsX() >= 1000:
                    current_hist.Rebin(15)
                elif current_hist.GetNbinsX() >= 100:
                    current_hist.Rebin(5)
                else:
                    pass

                if i == 0:
                    hnum[hname] = current_hist
                else:
                    hnum[hname].Add(current_hist)

            for hname in hdens:
                current_hist = HISTS[dataset][hname].Clone()
                current_hist.SetDirectory(0)
                current_hist.Sumw2()
                RT.addFlows(current_hist)
                if current_hist.GetNbinsX() >= 1000:
                    current_hist.Rebin(15)
                elif current_hist.GetNbinsX() >= 100:
                    current_hist.Rebin(5)
                else:
                    pass

                if i == 0:
                    hden[hname] = current_hist
                else:
                    hden[hname].Add(current_hist)

        if len(hden) > 1:
            raise NotImplementedError(
                "Too many denumerator histos - not yet implemented"
            )
        elif len(hden) == 0:
            raise Exception("No denominator histogram found")
        hden = hden[hden.keys()[0]]

        for key in hnum:
            canvas = Plotter.Canvas(lumi="NoBPTXRun2016D-07Aug17")

            g[key] = R.TGraphAsymmErrors(hnum[key], hden, "cp")
            g[key].SetNameTitle(
                "g_" + key, ";" + hnum[key].GetXaxis().GetTitle() + ";Efficiency"
            )
            p[key] = Plotter.Plot(g[key], key, "elp", "pe")

            canvas.addMainPlot(p[key])
            p[key].setColor(R.kBlue)
            canvas.makeLegend(pos="br")
            canvas.legend.moveLegend(X=-0.47)
            canvas.legend.moveLegend(Y=0.05)
            canvas.legend.resizeHeight()
            canvas.firstPlot.GetXaxis().SetRangeUser(0.0, 150.0)
            canvas.firstPlot.GetYaxis().SetRangeUser(0.0, 1.1)

            L2pTcut = re.findall(r"_pTGT(\d+)p(\d+)", key)
            if len(L2pTcut) > 1:
                raise Exception(
                    "Ambiguities in L2 pT threshold identification: {}".format(L2pTcut)
                )

            L2pTcut = float(".".join(L2pTcut[0]))
            pTthreshold_str = R.TLatex()
            pTthreshold_str.SetTextSize(0.035)
            pTthreshold_str.DrawLatex(
                100.0, 0.56, "p_{{T}}^{{L2}} > {} GeV".format(L2pTcut)
            )

            if L2pTcut > 0.0:
                L2vline = R.TLine(L2pTcut, 0.0, L2pTcut, 1.0)
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
                100.0, 0.48, "p_{{T}}^{{L1}} > {} GeV".format(L1pTcut)
            )

            if L1pTcut > 0.0:
                L1vline = R.TLine(L1pTcut, 0.0, L1pTcut, 1.0)
                R.SetOwnership(L1vline, 0)
                L1vline.SetLineColor(15)
                L1vline.SetLineStyle(2)
                L1vline.Draw()

            if d0min is not None and d0max is not None:
                selection_str = R.TLatex()
                selection_str.SetTextSize(0.035)
                selection_str.DrawLatex(
                    100.0, 0.4, "{} cm  < d_{{0}} < {} cm".format(d0min, d0max)
                )

            canvas.cleanup("pdfs/TETurnOn_{}.pdf".format(key))


def makeCombinedPlots(categories, selection=None, exclude=None, logic="and"):
    rebinning_exceptions = ("nCSCDTHits",)

    h = {}
    p = {}

    # import all relevant histograms
    for dataset in HISTS:
        if selection and exclude:
            selected_hists_names = getHistNames(
                dataset, *selection, exclude=exclude, logic=logic
            )
        elif selection and not exclude:
            selected_hists_names = getHistNames(dataset, *selection, logic=logic)
        elif not selection and exclude:
            selected_hists_names = getHistNames(
                dataset, "", exclude=exclude, logic=logic
            )
        else:
            selected_hists_names = HISTS[dataset]

        for key in selected_hists_names:
            if not any([cat in key for cat, __ in categories]):
                continue

            search_res = re.search(r"__(.+)VAR", key)
            if search_res:
                variable = search_res.group(1)
            else:
                print ("Skipping {} (unidentifiable variable)...".format(key))
                continue

            if variable not in h.keys():
                h[variable] = {}

            for category, __ in categories:
                if not category in key:
                    continue

                if category in h[variable]:
                    h[variable][category].Add(HISTS[dataset][key])
                else:
                    h[variable][category] = HISTS[dataset][key].Clone()

    # prepare the histograms
    for variable in h:
        for category in h[variable]:
            RT.addFlows(h[variable][category])

            if h[variable][category].GetNbinsX() >= 1000:
                if variable in rebinning_exceptions:
                    print ("Do not rebin for variable {}".format(variable))
                    pass
                else:
                    h[variable][category].Rebin(15)

            elif h[variable][category].GetNbinsX() >= 100:
                if variable in rebinning_exceptions:
                    print ("Do not rebin for variable {}".format(variable))
                    pass
                else:
                    h[variable][category].Rebin(5)

            else:
                pass

    # start creating plots
    for variable in h:
        p[variable] = {}

        # find the best vertical axes ranges
        realmin = float("inf")
        realmax = -float("inf")

        for category, category_name in categories:
            p[variable][category] = Plotter.Plot(
                h[variable][category], category_name, "l", "hist"
            )

            key_fname = h[variable][category].GetName()
            key_fname = key_fname.replace(category, "")
            if len(HISTS.keys()) > 1:
                search_res = re.search(r"(_*?NoBPTXRun\d+[A-Z][_-]07Aug17)", key_fname)
                if search_res:
                    key_fname = key_fname.replace(search_res.group(0), "")
                else:
                    print (
                        "Could not identify datset. Dataset name will not be "
                        "stripped from the output file names"
                    )

            if p[variable][category].GetMaximum() > realmax:
                realmax = p[variable][category].GetMaximum()

            if p[variable][category].GetMaximum() < realmin:
                realmin = p[variable][category].GetMinimum()

        for is_logy in (True, False):
            palette = Plotter.ColorPalette([867, 417, 600, 600, 801, 632])
            fname = "pdfs/comb_{}{}.pdf".format(key_fname, ("_logy" if is_logy else ""))
            canvas = Plotter.Canvas(logy=is_logy, lumi="NoBPTXRun2016[D+E]-07Aug17")
            for category, category_name in categories:
                canvas.addMainPlot(p[variable][category])
                p[variable][category].SetLineColor(palette.getNextColor())
                if "goodQuality" in category:
                    p[variable][category].SetLineStyle(2)

                RT.addBinWidth(p[variable][category])

            if variable in RANGES:
                canvas.firstPlot.GetXaxis().SetRangeUser(
                    RANGES[variable][0], RANGES[variable][1]
                )

            canvas.makeLegend(lWidth=0.3, pos="tr", fontscale=0.65)
            canvas.legend.resizeHeight()
            canvas.legend.moveLegend(X=-0.2, Y=-0.13)

            # trigger information for canvas
            pave_triggerinfo = R.TPaveText(0.4, 0.75, 0.72, 0.88, "NDCNB")
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

            if is_logy and realmin == 0:
                realmin = 0.5
            canvas.firstPlot.GetYaxis().SetRangeUser(realmin * 0.8, realmax * 1.2)

            # canvas.cleanup(fname.replace('.pdf','.root'))
            canvas.cleanup(fname)


def interpolateX(x0, y0, x1, y1, y):
    # Linearly interpolate between (x0,y0) and (x1,y1), return the x value for y
    return (x1 - x0) * (y - y0) / (y1 - y0) + x0


def findFitRange(h, percentage=0.66, minimal_range=0.4):
    nbins_to_check = 1
    peakval = h.GetMaximum()
    peakbin = h.GetMaximumBin()
    peakcenter = h.GetBinCenter(peakbin)

    threshold = percentage * peakval

    # find the lower limit
    for b in range(peakbin, 0, -1):
        if h.GetBinContent(b) < threshold:
            # check following bins to make sure this is not a
            # statistical fluctuation
            is_fluctuation = False
            for bb in range(b - 1, b - nbins_to_check, -1):
                if h.GetBinContent(bb) > h.GetBinContent(b):
                    is_flucutaion = True

            if not is_fluctuation:
                if b > 1:
                    range_min = interpolateX(
                        h.GetXaxis().GetBinCenter(b),
                        h.GetBinContent(b),
                        h.GetXaxis().GetBinCenter(b + 1),
                        h.GetBinContent(b + 1),
                        threshold,
                    )
                else:
                    range_min = h.GetXaxis().GetBinLowEdge(b + 1)

                break

    else:
        range_min = h.GetXaxis().GetBinLowEdge(1)

    # find the upper limit
    for b in range(peakbin + 1, h.GetNbinsX() + 1):
        if h.GetBinContent(b) < threshold:
            # check following bins to make sure this is not a
            # statistical fluctuation
            is_fluctuation = False
            for bb in range(b + 1, b + nbins_to_check):
                if h.GetBinContent(bb) > h.GetBinContent(b):
                    is_fluctuation = True

            if not is_fluctuation:
                if b < h.GetNbinsX() + 1:
                    range_max = interpolateX(
                        h.GetXaxis().GetBinCenter(b - 1),
                        h.GetBinContent(b - 1),
                        h.GetXaxis().GetBinCenter(b),
                        h.GetBinContent(b),
                        threshold,
                    )
                else:
                    range_max = h.GetXaxis().GetBinLowEdge(b + 1)

                break

    else:
        range_max = h.GetXaxis().GetBinLowEdge(h.GetNbinsX())

    # if the calculated range is below the minimally accepted range,
    # force a symmetric fit interval around the maximum
    if minimal_range and abs(range_max - range_min) < minimal_range:
        temp_min = peakcenter - 0.5 * minimal_range
        if temp_min < h.GetBinLowEdge(1): temp_min = h.GetBinLowEdge(1)

        temp_max = peakcenter + 0.5 * minimal_range
        if temp_max > h.GetBinLowEdge(h.GetNbinsX()+1): temp_max = h.GetBinLowEdge(h.GetNBinsX()+1)

        minbin = h.FindBin(temp_min)
        maxbin = h.FindBin(temp_max)
        range_min = h.GetBinCenter(minbin)
        range_max = h.GetBinCenter(maxbin)

    return range_min, range_max


def getHistNames(dataset, *args, **kwargs):
    logic = kwargs.pop("logic", "and")
    exclude_list = kwargs.pop("exclude", None)
    if kwargs:
        raise Exception("Invalid argument(s): {}".format(kwargs))

    exclude = None
    if exclude_list is not None:
        exclude = re.compile("|".join([e for e in exclude_list]))

    results = []
    # for dataset in HISTS:
    for key in HISTS[dataset]:
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


alpha_categories = (
    ("__0p0alpha0p3", "0 < #alpha < 0.3"),
    ("__0p3alpha2p8", "0.3 < #alpha < 2.8"),
    ("__2p8alphaPi", "2.8 < #alpha < #pi"),
    ("__goodQuality_2p8alphaPi", "2.8 < #alpha < #pi (#chi^{2}/ndof < 4)"),
    ("__SSpairs_2p8alphaPi", "2.8 < #alpha < #pi (same-sign pairs)"),
    (
        "__noOppositeMuonMatch_0p0alpha2p8",
        "0 < #alpha < 2.8 (no match with opposite muon)",
    ),
)

makeCombinedPlots(
    alpha_categories,
    selection=[
        "DSA__alphaVAR",
        "DSA__chargeVAR",
        "DSA__nStationsVAR",
        "DSA__dNStationsVAR",
        "DSA__nCSCDTHitsVAR",
        "DSA__dNCSCDTHitsVAR",
        "DSA__pSigVAR",
        "DSA__pTVAR",
        "DSA__dimVtxChi2",
        "DSA__dimCosAlpha",
        "DSA__dimLxySig",
        "DSA__chi2VAR",
        "DSA__massVAR",
        "DSA__chargeprodVAR",
        "DSA__dimLxyVAR",
        "DSA__pTdiffVAR",
        "DSA__pairPTVAR",
        "DSA__dEtaVAR",
        "DSA__dPhiVAR",
        "DSA__dD0VAR",
        "DSA__dChi2VAR",
        "DSA__pTSigVAR",
    ],
    logic="or",
    exclude=["__d0GT", "__d0LT", "Eff", "_noSelections"],
)

# makePerSamplePlots()
# makePerSamplePlots(['DSA__dimLxyVAR'])
# makePerSamplePlots(['DSA__dimMassVAR'])
# makePerSamplePlots(['DSA__alphaVAR'])
# makePerSamplePlots(['DSA__dimCosAlphaVAR'])
# makePerSamplePlots(['DSA__dimLxySigVAR'])
# makePerSamplePlots(['DSA__dimVtxChi2VAR'])
# makePerSamplePlots(['Hemisphere__pTVAR'])
# makePerSamplePlots(['DSA__pTVAR'])
# makePerSamplePlots(['dimuonMultiplicity'])
# makePerSamplePlots(['DSA__nStationsVAR'])
# makePerSamplePlots(['DSA__nCSCDTHitsVAR'])
# makePerSamplePlots(['DSA__pTSigVAR'])

# makePerSamplePlots(['DSA','L1pTres'])
# makePerSamplePlots(['DSA','L2pTres'])
makePerSamplePlots(["DSAmuonMultiplicity"])


# makeTurnOnPlots()
