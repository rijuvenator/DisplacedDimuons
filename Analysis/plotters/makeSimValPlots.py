import sys
import re
from array import array
import numpy as np
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter

MC_filepath = "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/shouldercheck_simulation/hadded_HTo2XTo2Mu2J_reHLT_HLT-CosmicSeed_etaLT0p5_nCSCDTHitsGT12_nStationsGT1_pTSigLT1p0_oneLegMatched_HTo2XTo2Mu2J_reHLT_CosmicSeed_merged.root"
# MC_filepath = "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/simulation-validation/HTo2XTo2Mu2J_reHLT_HLT-CosmicSeed_merged.root"
data_filepath = "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/simulation-validation/Cosmics2016_UGMT-bottomOnly_HLT-CosmicSeed.root"

# MC_filepath = "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/simulation-validation/HTo2XTo2Mu2J_reHLT_HLT-ppSeed_merged.root"
# data_filepath = "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/simulation-validation/Cosmics2016_UGMT-bottomOnly_HLT-ppSeed.root"

# Cosmic or pp-seeded path? (colors are chosen according to this setting)
IS_COSMIC_SEED = True
# IS_COSMIC_SEED = False

# specify legend names
legend_name_MC = "Signal MC"
legend_name_data = "Cosmics data"

# specify which variable to plot ("L1pTresVAR" or "L2pTresVAR")
RESOLUTIONVARIABLE = "L1pTresVAR"

# output file name (w/o file extension), resolution variable name to be filled
# in dynamically
FILENAME_TEMPLATE = "resVsD0_{RESOLUTIONVARIABLE}"

# (sub)set of d0 bins which are to be plotted (they must exist as histograms
# in the cosmicsPlots.py analyzer output file)
d0intervals = []
d0intervals += [(i, i + 5.0) for i in np.arange(0.0, 10.0, 5.0)]
d0intervals += [(i, i + 10.0) for i in np.arange(10.0, 100.0, 10.0)]


def interpolateX(x0, y0, x1, y1, y):
    # Linearly interpolate between (x0,y0) and (x1,y1), return the x value for y
    return (x1 - x0) * (y - y0) / (y1 - y0) + x0


def autoRebin(
    h,
    error_fraction=0.05,
    neighboring_bins=5,
    min_nBins_in_interval=15,
    interval=[-1.0, 0.5],
):
    def criterion(error_fraction=error_fraction):
        peakbin = h.GetMaximumBin()
        leftbin = peakbin - neighboring_bins if peakbin - neighboring_bins >= 1 else 1
        rightbin = (
            peakbin + neighboring_bins
            if peakbin + neighboring_bins <= h.GetNbinsX()
            else h.GetNbinsX()
        )
        for b in range(leftbin, rightbin):
            content = h.GetBinContent(b)
            err = h.GetBinError(b)
            if err > error_fraction * content:
                return False

        else:
            return True

    def nBinsInInterval(interval=interval):
        leftbin = h.FindBin(interval[0])
        rightbin = h.FindBin(interval[1])
        cnt_bins = 0
        for b in range(leftbin, rightbin + 1):
            cnt_bins += 1
        return cnt_bins

    cnt_rebins = 0
    while not criterion() and nBinsInInterval(interval) > min_nBins_in_interval:
        cnt_rebins += 1
        h.Rebin(2)

    return 2 * cnt_rebins


def findFitRange(h, percentage=0.3):
    nbins_to_check = 1
    peakval = h.GetMaximum()
    peakbin = h.GetMaximumBin()

    threshold = percentage * peakval

    # find the lower limit
    for b in range(1, peakbin + 1):
        if h.GetBinContent(b) > threshold:
            # check following bins to make sure this is not a
            # statistical fluctuation
            is_fluctuation = False
            for bb in range(b + 1, b + nbins_to_check):
                if h.GetBinContent(bb) < h.GetBinContent(b):
                    is_fluctuation = True

            if not is_fluctuation:
                if b > 1:
                    range_min = interpolateX(
                        h.GetXaxis().GetBinCenter(b - 1),
                        h.GetBinContent(b - 1),
                        h.GetXaxis().GetBinCenter(b),
                        h.GetBinContent(b),
                        threshold,
                    )
                else:
                    range_min = h.GetXaxis().GetBinLowEdge(b)

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

    return range_min, range_max


def getPeakPosition(h, strategy="gaussfit", fraction=0.5):
    if strategy == "gaussfit":
        # determining the resolution mean
        fit_xmin, fit_xmax = findFitRange(h)

        func = R.TF1("f" + h.GetName(), "gaus", fit_xmin, fit_xmax)
        func.SetParameters(10.0, -0.1, 0.5)
        R.SetOwnership(func, 0)
        h.Fit("f" + h.GetName(), "RQN")
        res_mean = func.GetParameter(1)
        res_mean_err = func.GetParError(1)
        res_std = func.GetParameter(2)
        res_std_err = func.GetParError(2)
        fit_chisquare = func.GetChisquare()

        return (
            res_mean,
            res_mean_err,
            res_std,
            res_std_err,
            {
                "strategy": "gaussfit",
                "quality": fit_chisquare,
                "fit_xmin": fit_xmin,
                "fit_xmax": fit_xmax,
            },
        )

    elif strategy == "max":
        # finding the maximum of the distribution
        peakval = h.GetMaximum()
        peakbin = h.GetMaximumBin()
        peakpos = h.GetXaxis().GetBinCenter(peakbin)
        rel_pos_left = 0
        rel_pos_right = 0

        # find left bin of "width"
        rel_pos_left = -1.0
        for b in range(peakbin - 1, 0, -1):
            if h.GetBinContent(b) < fraction * peakval:
                # rel_pos_left = b
                rel_pos_left = interpolateX(
                    h.GetXaxis().GetBinCenter(b),
                    h.GetBinContent(b),
                    h.GetXaxis().GetBinCenter(b + 1),
                    h.GetBinContent(b + 1),
                    fraction * peakval,
                )
                break

        # else:
        #     rel_pos_left = 1

        # find right bin of "width"
        rel_pos_right = h.GetBinCenter(h.GetNbinsX())
        for b in range(peakbin + 1, h.GetNbinsX() + 1):
            if h.GetBinContent(b) < fraction * peakval:
                rel_pos_right = interpolateX(
                    h.GetXaxis().GetBinCenter(b - 1),
                    h.GetBinContent(b - 1),
                    h.GetXaxis().GetBinCenter(b),
                    h.GetBinContent(b),
                    fraction * peakval,
                )
                break

        # else:
        #     rel_pos_right = h.GetNbinsX()

        # width = h.GetBinCenter(peakbin + rel_pos_right) - h.GetBinCenter(peakbin - rel_pos_left)
        width = rel_pos_right - rel_pos_left

        return peakpos, 0.0, width, 0.0, {"strategy": "max"}


def getHistNames(data, dataset, *args, **kwargs):
    logic = kwargs.pop("logic", "and")
    exclude_list = kwargs.pop("exclude", None)
    if kwargs:
        raise Exception("Invalid argument(s): {}".format(kwargs))

    exclude = None
    if exclude_list is not None:
        exclude = re.compile("|".join([e for e in exclude_list]))

    results = []
    # for dataset in data
    for key in data[dataset]:
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


def getLabels(var):
    if "L2pTres" in var:
        h_ylabel_value = "#mu[(p_{T}^{L2} - p_{T}^{DSA}) / p_{T}^{DSA}]  #it{(data)}"
        h_ylabel_width = "#sigma[(p_{T}^{L2} - p_{T}^{DSA}) / p_{T}^{DSA}]  #it{(data)}"
        h_ylabel_fraction_in_tail = "fraction in tails above fit limit  #it{(data)}"
        h_ylabel_quality = "fit #chi^{2} / 10  #it{(data)}"
        h_xlabel = "d_{0} [cm]"
        canvas_text = "(p_{T}^{L2} - p_{T}^{DSA}) / p_{T}^{DSA}"
    elif "L1pTres" in var:
        h_ylabel_value = "#mu[(p_{T}^{L1} - p_{T}^{DSA}) / p_{T}^{DSA}]  #it{(data)}"
        h_ylabel_width = "#sigma[(p_{T}^{L1} - p_{T}^{DSA}) / p_{T}^{DSA}]  #it{(data)}"
        h_ylabel_fraction_in_tail = "fraction in tails above fit limit  #it{(data)}"
        h_ylabel_quality = "fit #chi^{2} / 10  #it{(data)}"
        h_xlabel = "d_{0} [cm]"
        canvas_text = "(p_{T}^{L1} - p_{T}^{DSA}) / p_{T}^{DSA}"
    else:
        h_ylabel_value = ""
        h_ylabel_width = ""
        h_ylabel_fraction_in_tail = ""
        h_ylabel_quality = ""
        h_xlabel = "d_{0} [cm]"
        canvas_text = ""

    return (
        h_ylabel_value,
        h_ylabel_width,
        h_ylabel_fraction_in_tail,
        h_ylabel_quality,
        h_xlabel,
        canvas_text,
    )


def importHistogram(allhists, resolution_variable, includes=None, excludes=None):
    imported_hists = []
    imported_d0hists = []
    for dat in allhists:
        resolution_hists = getHistNames(allhists, dat, *includes, exclude=excludes)

        for key in resolution_hists:
            if not all([d0str in key for d0str in ["__d0GT", "__d0LT"]]):
                continue

            h = allhists[dat][key].Clone()
            RT.addFlows(h)
            imported_hists.append(h)

            d0_histname = key.replace("__{}".format(resolution_variable), "__d0VAR")
            if d0_histname == key:
                raise Exception("Error parsing the name of the d0 histogram")

            d0_h = allhists[dat][d0_histname].Clone()
            RT.addFlows(d0_h)
            imported_d0hists.append(d0_h)

    return imported_hists, imported_d0hists


def extractD0Values(d0str):
    pattern = r"__d0GT(\d+p\d+|\d+)__d0LT(\d+p\d+|\d+)"
    result = re.search(pattern, d0str)
    if result:
        d0min = float(result.group(1).replace("p", "."))
        d0max = float(result.group(2).replace("p", "."))
    else:
        raise Exception("Could not extract d0 values from string: {}".format(d0str))

    return d0min, d0max


def generateGraphData(reshists, d0hists, d0intervals=None, strategy="max"):
    graphdata = {
        "d0_mean": [],
        "d0_min": [],
        "d0_max": [],
        "res_val": [],
        "res_val_err": [],
        "res_width": [],
        "res_width_err": [],
        "fraction_in_tail": [],
        "fraction_in_tail_err": [],
        "quality": [],
        "quality_err": [],
    }

    for h, h_d0 in zip(reshists, d0hists):

        saveHistogram(h, "pdfs/hist_{}".format(h.GetName()))

        # find rebinning for h
        rebin_param = autoRebin(h)
        savePlot(h, "pdfs/{}".format(h.GetName()), x_range=[-1, 5])
        saveHistogram(h, "pdfs/hist_autoRebinned_{}".format(h.GetName()))

        # skip if there are too few entries in the maximum bin
        if h.GetMaximum() < 50.0:
            continue

        # find horizontal coordinates
        d0mean = h_d0.GetMean()
        d0min, d0max = extractD0Values(h.GetName())
        if d0intervals and (d0min, d0max) not in d0intervals:
            print ("[PLOTTER INFO] Skipping d0 bin ({}, {}).".format(d0min, d0max))
            continue

        graphdata["d0_mean"].append(d0mean)
        graphdata["d0_min"].append(d0min)
        graphdata["d0_max"].append(d0max)

        # find vertical coordinates
        peakpos, peakpos_error, peakwidth, peakwidth_error, params = getPeakPosition(
            h, strategy="max"
        )
        graphdata["res_val"].append(peakpos)
        graphdata["res_val_err"].append(peakpos_error)
        graphdata["res_width"].append(peakwidth)
        graphdata["res_width_err"].append(peakwidth_error)
        graphdata["quality_err"].append(0.0)
        graphdata["fraction_in_tail_err"].append(0.0)
        if params["strategy"] == "gaussfit":
            h_content = 0
            h_content_tail = 0
            fit_xmax = params["fit_xmax"]
            fit_xmax_bin = h.FindBin(fit_xmax)
            for b in range(1, h.GetNbinsX() + 1):
                h_content += h.GetBinContent(b)
                if b > fit_xmax_bin:
                    h_content_tail += h.GetBinContent(b)

            graphdata["fraction_in_tail"].append(
                1.0 * h_content_tail / h_content if h_content != 0 else 0.0
            )
            graphdata["quality"].append(params["quality"])

    # sort data in ascending order of d0min
    d0min_list = graphdata["d0_min"]
    for datalist in graphdata:
        graphdata[datalist] = [
            x for _, x in sorted(zip(d0min_list, graphdata[datalist]))
        ]

    return graphdata


def generateGraph(data, distribution="res_val", error_axes="xy"):
    g_n = int(len(data["d0_min"]))
    g_x = array("d", data["d0_mean"])
    g_y = array("d", data[distribution])
    if "x" in error_axes.lower():
        g_exl = array(
            "d",
            [mean - lowedge for mean, lowedge in zip(data["d0_mean"], data["d0_min"])],
        )
        g_exh = array(
            "d",
            [upedge - mean for mean, upedge in zip(data["d0_mean"], data["d0_max"])],
        )
    else:
        g_exl = array("d", [0.0 for mean in data["d0_mean"]])
        g_exh = array("d", [0.0 for mean in data["d0_mean"]])

    if "y" in error_axes.lower():
        g_eyl = array("d", data[distribution + "_err"])
        g_eyh = array("d", data[distribution + "_err"])
    else:
        g_eyl = array("d", [0.0 for mean in data[distribution]])
        g_eyh = array("d", [0.0 for mean in data[distribution]])

    graph = R.TGraphAsymmErrors(g_n, g_x, g_y, g_exl, g_exh, g_eyl, g_eyh)

    return graph


def savePlot(data, filename, extList=[".pdf", ".root"], lumi="", x_range=None):
    c = Plotter.Canvas(lumi=lumi)
    if isinstance(data, Plotter.Plot):
        plot = data.Clone()
    else:
        plot = Plotter.Plot(data, "", "elp", "pe")

    c.addMainPlot(plot)

    if x_range:
        c.firstPlot.GetXaxis().SetRangeUser(x_range[0], x_range[1])

    c.finishCanvas()
    c.save(filename, extList=extList)
    c.deleteCanvas()


def saveHistogram(hist, filename, rebin=None):
    if not filename.endswith(".root"):
        filename += ".root"
    f = R.TFile.Open(filename, "RECREATE")
    h_clone = hist.Clone()
    if rebin:
        h_clone.Rebin(rebin)

    f.Write()
    f.Close()
    del f


def makeResolutionVsD0Plots(
    RESOLUTIONVARIABLE, data_filepath, MC_filepath, d0intervals
):
    HISTS_data = HistogramGetter.getHistograms(data_filepath)
    HISTS_MC = HistogramGetter.getHistograms(MC_filepath)

    # make sure that all given d0 interval limits are actually floats
    d0intervals = [(float(l), float(u)) for l, u in d0intervals]

    h_ylabel_value, h_ylabel_width, h_ylabel_fraction_in_tail, h_ylabel_quality, h_xlabel, canvas_text = getLabels(
        RESOLUTIONVARIABLE
    )

    data_hists, data_d0hists = importHistogram(
        HISTS_data,
        RESOLUTIONVARIABLE,
        includes=["DSA_lowerLeg", RESOLUTIONVARIABLE],
        excludes=["EffNum", "EffDen"],
    )
    MC_hists, MC_d0hists = importHistogram(
        HISTS_MC,
        RESOLUTIONVARIABLE,
        includes=["DSA_lowerLeg", RESOLUTIONVARIABLE],
        excludes=["EffNum", "EffDen"],
    )

    resVsD0_data = generateGraphData(data_hists, data_d0hists, d0intervals=d0intervals)
    resVsD0_MC = generateGraphData(MC_hists, MC_d0hists, d0intervals=d0intervals)

    canvas = Plotter.Canvas(lumi="2016 MC vs. Cosmics data")

    # data distributions and specifications
    graph_data = generateGraph(resVsD0_data, distribution="res_val")
    canvas.addMainPlot(Plotter.Plot(graph_data, legend_name_data, "elp", "pe"))
    graph_data.SetLineColor(R.kBlue if IS_COSMIC_SEED else R.kRed)
    graph_data.SetMarkerColor(R.kBlue if IS_COSMIC_SEED else R.kRed)

    # data width distribution and specifications
    graph_data_width = generateGraph(
        resVsD0_data, distribution="res_width", error_axes=""
    )
    canvas.addMainPlot(
        Plotter.Plot(graph_data_width, legend_name_data + " std. dev.", "elp", "pe")
    )
    # canvas.addMainPlot(Plotter.Plot(graph_data_width, legend_name_data + " FWHM", "elp", "pe"))
    graph_data_width.SetLineColor(R.kBlue if IS_COSMIC_SEED else R.kRed)
    graph_data_width.SetMarkerColor(R.kBlue if IS_COSMIC_SEED else R.kRed)
    graph_data_width.SetMarkerStyle(R.kMultiply)

    # MC distribution and specifications
    graph_MC = generateGraph(resVsD0_MC, distribution="res_val")
    canvas.addMainPlot(Plotter.Plot(graph_MC, legend_name_MC, "elp", "pe"))
    graph_MC.SetLineColor(R.kCyan + 1 if IS_COSMIC_SEED else R.kOrange - 3)
    graph_MC.SetMarkerColor(R.kCyan + 1 if IS_COSMIC_SEED else R.kOrange - 3)

    # MC width distributions and specifications
    graph_MC_width = generateGraph(resVsD0_MC, distribution="res_width", error_axes="")
    canvas.addMainPlot(
        Plotter.Plot(graph_MC_width, legend_name_MC + " std. dev.", "elp", "pe")
    )
    # canvas.addMainPlot(Plotter.Plot(graph_MC_width, legend_name_MC + " FWHM", "elp", "pe"))
    graph_MC_width.SetLineColor(R.kCyan + 1 if IS_COSMIC_SEED else R.kOrange - 3)
    graph_MC_width.SetMarkerColor(R.kCyan + 1 if IS_COSMIC_SEED else R.kOrange - 3)
    graph_MC_width.SetMarkerStyle(R.kMultiply)

    # add horizontal line at zero
    zero_line_horizontal = R.TLine(
        resVsD0_data["d0_min"][0], 0.0, resVsD0_data["d0_max"][-1], 0.0
    )
    R.SetOwnership(zero_line_horizontal, 0)
    zero_line_horizontal.SetLineColor(R.kGray)
    zero_line_horizontal.SetLineStyle(2)
    zero_line_horizontal.Draw()

    # set axis titles
    canvas.firstPlot.GetXaxis().SetTitle(h_xlabel)
    canvas.firstPlot.GetYaxis().SetTitle("Resolution peak parameters")

    # set axis ranges
    if "L2pTres" in RESOLUTIONVARIABLE:
        if IS_COSMIC_SEED:
            canvas.firstPlot.GetYaxis().SetRangeUser(-0.1, 0.3)
        else:
            canvas.firstPlot.GetYaxis().SetRangeUser(-0.6, 1.5)
    elif "L1pTres" in RESOLUTIONVARIABLE:
        canvas.firstPlot.GetYaxis().SetRangeUser(-1.1, 1.5)

    # create legend
    canvas.makeLegend(lWidth=0.37, pos="tr", fontscale=0.85)
    canvas.legend.resizeHeight()

    if canvas_text:
        pavetext = R.TPaveText(0.18, 0.78, 0.5, 0.9, "NDCNB")
        pavetext.SetTextAlign(13)
        pavetext.SetTextFont(42)
        pavetext.SetMargin(0)
        pavetext.SetFillStyle(0)
        pavetext.SetFillColor(0)
        pavetext.SetLineStyle(0)
        pavetext.SetLineColor(0)
        pavetext.SetBorderSize(0)
        pavetext.AddText(
            0.0,
            0.0,
            canvas_text + ",  {} seed".format("cosmic" if IS_COSMIC_SEED else "pp"),
        )
        pavetext.Draw()

    canvas.finishCanvas()
    canvas.save(
        "pdfs/" + FILENAME_TEMPLATE.format(RESOLUTIONVARIABLE=RESOLUTIONVARIABLE),
        extList=[".pdf", ".root"],
    )
    canvas.deleteCanvas()
    # canvas.cleanup("pdfs/new_resVsd0_{}.pdf".format(RESOLUTIONVARIABLE))


makeResolutionVsD0Plots(RESOLUTIONVARIABLE, data_filepath, MC_filepath, d0intervals)
