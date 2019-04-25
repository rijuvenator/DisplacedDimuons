import sys
import re
import numpy as np
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter

lumi_str = "2016 cosmics data"

L1T_info = "Data taken with L1_SingleMuOpen"
HLT_info = "Ref. path: HLT_L2Mu10_NoVertex_[pp|CosmicSeed] (re-HLT)"

# specify a list of patterns to plot, and a corresponding list of strings to exclude
hist_patterns_and_excludes = (
    ("L1pTresVAR", ["_0p0alpha", "_0p3alpha", "_2p8alpha"]),
    ("L2pTresVAR", ["_0p0alpha", "_0p3alpha", "_2p8alpha"]),
)

# specify ((color, linestyle, markerstyle), file names, description)
file_specs = (
    # compare GMT modes / JSONs (for lower legs)
    (
        (R.kBlue, 1, None),
        "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-base_HLT-CosmicSeed_lowerLeg.root",
        "base GMT mode (cosmic seed, lower leg)",
    ),
    (
        (R.kBlue, 2, 24),
        "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-bottomOnly_HLT-CosmicSeed_lowerLeg.root",
        "bottomOnly GMT mode (cosmic seed, lower leg)",
    ),
    (
        (R.kRed, 1, None),
        "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-base_HLT-ppSeed_lowerLeg.root",
        "base GMT mode (pp seed, lower leg)",
    ),
    (
        (R.kRed, 2, 24),
        "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-bottomOnly_HLT-ppSeed_lowerLeg.root",
        "bottomOnly GMT mode (pp seed, lower leg)",
    ),
    #
    # # compare legs (for base GMT modes)
    (
        (R.kBlue, 1, None),
        "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-base_HLT-CosmicSeed_lowerLeg.root",
        "lower leg (cosmic seed, base GMT mode)",
    ),
    (
        (R.kBlue, 2, 24),
        "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-base_HLT-CosmicSeed_upperLeg.root",
        "upper leg (cosmic seed, base GMT mode)",
    ),
    (
        (R.kRed, 1, None),
        "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-base_HLT-ppSeed_lowerLeg.root",
        "lower leg (pp seed, base GMT mode)",
    ),
    (
        (R.kRed, 2, 24),
        "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_reHLT_fixedL1EmulatorBug/Cosmics2016_UGMT-base_HLT-ppSeed_upperLeg.root",
        "upper leg (pp seed, base GMT mode)",
    ),
    #
    # validate re-HLT
    (
        (R.kBlue, 1, None),
        "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_L1emulatorFixed_JSONsubset-for-NoBPTX-comparison/Cosmics2016_UGMT-base_HLT-CosmicSeed_lowerLeg.root",
        "Cosmics re-HLT samples (cosmic seed, lower leg)",
    ),
    (
        (R.kBlue, 2, 24),
        "/afs/cern.ch/work/s/stempl/private/DDM/cosmics-studies/hadded_Cosmics2016_L1emulatorFixed_JSONsubset-for-NoBPTX-comparison/NoBPTX2016_HLT-CosmicSeed_lowerLeg.root",
        "NoBPTX samples (cosmic seed, lower leg)",
    ),
)


def makeSimpleComparisonPlots(hist_patterns_and_excludes):
    p = {f: {"appearance": app, "descr": d, "plots": {}} for app, f, d in file_specs}
    p_norm = {
        f: {"appearance": app, "descr": d, "plots": {}} for app, f, d in file_specs
    }

    hists = collectHistograms(file_specs, hist_patterns_and_excludes)

    # prepare the histograms
    for appearance, f, f_descr in file_specs:
        for key in hists[f]["hists"]:
            RT.addFlows(hists[f]["hists"][key])

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

            h_norm = hists[f]["hists"][key].Clone()
            if h_norm.Integral() > 0:
                h_norm.Scale(1.0 / h_norm.Integral())
            else:
                pass

            p_norm[f]["plots"][key] = Plotter.Plot(
                h_norm, legName + " (normalized)", "l", "hist"
            )

    for plots, suffix in ((p, ""), (p_norm, "_norm")):
        for is_logy in (True, False):
            for key in hists[hists.keys()[0]]["hists"]:
                canvas = Plotter.Canvas(logy=is_logy, lumi=lumi_str)

                cnt_file = -1  # keeps track of the order of processed files
                for f in hists:
                    cnt_file += 1
                    canvas.addMainPlot(plots[f]["plots"][key])
                    RT.addBinWidth(plots[f]["plots"][key])
                    plots[f]["plots"][key].SetLineColor(plots[f]["appearance"][0])
                    plots[f]["plots"][key].SetLineStyle(plots[f]["appearance"][1])
                    if plots[f]["appearance"][2] is not None:
                        plots[f]["plots"][key].SetMarkerStyle(plots[f]["appearance"][2])

                if legName != "":
                    canvas.makeLegend(lWidth=0.3, pos="tr", fontscale=0.77)
                    canvas.legend.resizeHeight()
                    canvas.legend.moveLegend(X=-0.3, Y=-0.2)

                pave_triggerinfo = R.TPaveText(0.28, 0.75, 0.9, 0.9, "NDCNB")
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

                d0min_searchres = re.search(r"__d0GT(\d+p\d+|\d+)", key)
                if d0min_searchres:
                    d0min = d0min_searchres.group(1).replace("p", ".")
                else:
                    d0min = None

                d0max_searchres = re.search(r"__d0LT(\d+p\d+|\d+)", key)
                if d0max_searchres:
                    d0max = d0max_searchres.group(1).replace("p", ".")
                else:
                    d0max = None

                if d0min is not None and d0max is not None:
                    selection_str = R.TLatex()
                    selection_str.SetTextSize(0.035)
                    selection_str.DrawLatexNDC(
                        0.4, 0.73, "{} cm  < d_{{0}} < {} cm".format(d0min, d0max)
                    )

                if "pTresVAR" in key:
                    canvas.firstPlot.GetXaxis().SetRangeUser(-1.0, 5.0)

                if "L1pTresVAR" in key and "norm" in suffix:
                    if is_logy:
                        canvas.firstPlot.GetYaxis().SetRangeUser(1e-3, 0.35)
                    else:
                        canvas.firstPlot.GetYaxis().SetRangeUser(0.0, 0.35)

                if "L2pTresVAR" in key and "norm" in suffix:
                    if is_logy:
                        canvas.firstPlot.GetYaxis().SetRangeUser(1e-3, 0.35)
                    else:
                        canvas.firstPlot.GetYaxis().SetRangeUser(0.0, 0.35)

                fname = "pdfs/reconstruction-comparisons/{}{}{}".format(
                    key, "_logy" if is_logy else "", suffix
                )

                canvas.finishCanvas()
                canvas.save(fname, extList=[".pdf", ".root"])
                canvas.deleteCanvas()

    del hists


def makeTurnOnComparisonPlots():
    turnOn_patterns_and_excludes = (
        ("__pTVAREff", ["_0p0alpha", "_0p3alpha", "_2p8alpha"]),
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
            canvas.legend.moveLegend(X=-0.45, Y=0.13)
            canvas.legend.resizeHeight()
            canvas.firstPlot.GetXaxis().SetRangeUser(0.0, 150.0)
            canvas.firstPlot.GetYaxis().SetRangeUser(0.0, 1.055)

            L2pTcut = re.findall(r"_pTGT(\d+)p(\d+)", key)
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

            fname = "pdfs/reconstruction-comparisons/TETurnOn_{}".format(key)

            canvas.finishCanvas()
            canvas.save(fname, extList=[".pdf", ".root"])
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
