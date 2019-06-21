import os
import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter


# Define all distribution and plot properties here and make sure this function is called first
def initialize_specs():
    PLOT_SPECS = {"lumi_str": "2016 Cosmics data"}

    DISTRIBUTION_SPECS = (
        ### TEMPLATE ###
        #  HistSpecs(
        #     "FILENAME.root",
        #     "(SUB)STRING IDENTIFYING THE DISTRIBUTION TO BE PLOTTED",
        #     <NUM/DEN LABEL> (labelling the distribution as denominator or numerator, e.g., "den1", "num1", "den2", "num2")
        #     histname_exclude = None or [list of strings that are not allowed to be contained in the distribution name],
        #     legend = "LEGEND TEXT",
        #     linecolor = <linecolor> (example: R.kBlue),  # optical attributes are to be defined in the NUMERATOR histograms
        #     rebin=<integer specifying the number of bins to merge during rebinning>,
        #     Xrange=[list containing min and max of x axis range] (example: [-1.0, 5.0])
        # ),
        HistSpecs(
            "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/latest/hadded_Cosmics2016/Cosmics2016_UGMT-base_HLT-CosmicSeed.root",
            "DSA_lowerLeg__pTVAREffDen__d0GT0p0__d0LT10p0",
            label="den1",
            histname_exclude=[],
            legend="0 cm < d_{0} < 10 cm",
            rebin=2,
        ),
        HistSpecs(
            "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/latest/hadded_Cosmics2016/Cosmics2016_UGMT-base_HLT-CosmicSeed.root",
            "DSA_lowerLeg_L2pTGT23p0_L1pTGT0p0__pTVAREffNum__d0GT0p0__d0LT10p0",
            label="num1",
            histname_exclude=[],
            legend="0 cm < d_{0} < 10 cm",
            linecolor=R.kBlue,
            markercolor=R.kBlue,
            Xrange=[-1.0, 50.0],
            rebin=2,
        ),
    )

    _checkSpecs(DISTRIBUTION_SPECS)

    return PLOT_SPECS, DISTRIBUTION_SPECS


def _checkSpecs(DISTRIBUTION_SPECS):
    # only checks the consistency of "labels" at the moment

    labels = [s.getAttribute("label") for s in DISTRIBUTION_SPECS]

    # check whether there are any denominator distributions at all
    if not any(["den" in l for l in labels]):
        raise Exception("No denominator distribution specified")

    # check whether there are any unsupported labels
    for l in labels:
        if not any([s in l for s in ("den", "num")]):
            raise Exception("Unsupported label: {}".format(l))

    # make sure that every denominator has its numerator
    for l in labels:
        if "den" in l:
            excepted_num_key = l.replace("den", "num")
            if excepted_num_key not in labels:
                raise Exception(
                    "Missing numerator definition: {}".format(expected_num_key)
                )

    # make sure that every numerator has its denominator
    for l in labels:
        if "num" in l:
            expected_den_key = l.replace("num", "den")
            if expected_den_key not in labels:
                raise Exception(
                    "Missing denominator definition: {}".format(expected_den_key)
                )


def pairHistSpecs(DISTRIBUTION_SPECS):
    # pair HistSpecs objects according to their labels (i.e., group together
    # "den1" and "num1", "den2" and "num2" etc.)

    paired_specs = {}
    for el in DISTRIBUTION_SPECS:
        label = el.getAttribute("label")
        identifier = label.strip("den").strip("num")
        if identifier not in paired_specs:
            paired_specs[identifier] = {}

        if "den" in label:
            paired_specs[identifier]["den"] = el
        elif "num" in label:
            paired_specs[identifier]["num"] = el
        else:
            raise Exception("Unknown label format: {}".format(label))

    return paired_specs


class HistSpecs:
    def __init__(
        self,
        filepath,
        histname_identifier,
        label,
        histname_exclude=None,
        legend=None,
        linecolor=None,
        linestyle=None,
        markercolor=None,
        markerstyle=None,
        rebin=None,
        Xrange=None,
        Yrange=None,
        histogram=None,
    ):
        self.filepath = filepath
        self.histname_identifier = histname_identifier
        self.label = label.lower()
        self.histname_exclude = histname_exclude
        self.legend = legend
        self.linecolor = linecolor
        self.linestyle = linestyle
        self.markercolor = markercolor
        self.markerstyle = markerstyle
        self.rebin = rebin
        self.Xrange = Xrange
        self.Yrange = Yrange
        self.histogram = histogram

    def getAttribute(self, attr):
        return getattr(self, attr)

    def setAttribute(self, attr, val):
        setattr(self, attr, val)


def importHistograms(DISTRIBUTION_SPECS):
    """
    Read and add specified histograms from one or many files.

    Extracts histograms from one or many ROOT files (defined via the argument
    'DISTRIBUTION_SPECS') and adds them to the given HistSpecs objects.

    Parameters
    ----------
    DISTRIBUTION_SPECS : HistSpecs object
        An instance of the HistSpecs class, which defines all the relevant histogram
        properties

    """

    # perform some basic sanity checks
    for el in DISTRIBUTION_SPECS:
        filepath = el.getAttribute("filepath")
        histname_identifier = el.getAttribute("histname_identifier")
        histname_exclude = el.getAttribute("histname_exclude")

        types = ((filepath, str), (histname_identifier, str), (histname_exclude, list))
        for o, t in types:
            if not isinstance(o, t):
                raise Exception(
                    "Invalid type of {}: should be {}, but is {}".format(o, t, type(o))
                )

        if not os.path.exists(filepath):
            raise Exception("No such file: {}".format(filepath))

    # dictionary structure for collecting the relevant distributions
    hists = {}

    cnt_files = 1
    for el in DISTRIBUTION_SPECS:
        filepath = el.getAttribute("filepath")
        histname_identifier = el.getAttribute("histname_identifier")
        histname_exclude = el.getAttribute("histname_exclude")

        print (
            "[{}/{}] Reading file {}...".format(
                cnt_files, len(DISTRIBUTION_SPECS), filepath
            )
        )

        f_allhists = HistogramGetter.getHistograms(filepath)

        histogram = None

        for dataset in f_allhists:
            selected_hists_names = getHistNames(
                f_allhists, dataset, histname_identifier, exclude=histname_exclude
            )

            if len(selected_hists_names) > 1:
                raise Exception(
                    "Ambiguous histogram identifier: {} would select the following {} histograms: {}".format(
                        histname_identifier,
                        len(selected_hists_names),
                        "\n".join(selected_hists_names),
                    )
                )

            for key in selected_hists_names:
                if histogram is None:
                    histogram = f_allhists[dataset][key].Clone()
                    histogram.Sumw2()
                else:
                    temp_hist = f_allhists[dataset][key].Clone()
                    temp_hist.Sumw2()
                    histogram.Add(temp_hist)

        if histogram:
            print ("\tImported histogram {}".format(histogram.GetName()))
        else:
            raise RuntimeError("\tNo histograms found.")

        # prepare the histogram
        RT.addFlows(histogram)

        if el.getAttribute("histogram") is not None:
            print (
                "Warning: Histogram already exists in the HistSpecs object and will be overwritten"
            )

        # add the actual histrogram to the corresponding HistSpecs object
        el.setAttribute("histogram", histogram)

        cnt_files += 1
        del f_allhists


def getHistNames(hists, dataset, *args, **kwargs):
    logic = kwargs.pop("logic", "and")
    exclude_list = kwargs.pop("exclude", None)
    if kwargs:
        raise Exception("Invalid argument(s): {}".format(kwargs))

    exclude = None
    if isinstance(exclude_list, list) and len(exclude_list) == 0:
        exclude_list = None

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


def makeEfficiencyPlots(
    PLOT_SPECS,
    DISTRIBUTIONS_SPECS,
    output_filename,
    output_folder="pdfs/",
    logy=False,
    make_legend=True,
):

    importHistograms(DISTRIBUTION_SPECS)

    canvas = Plotter.Canvas(logy=logy, lumi=PLOT_SPECS["lumi_str"])

    Xrange_min = None
    Xrange_max = None
    Yrange_min = None
    Yrange_max = None

    paired_distributions = pairHistSpecs(DISTRIBUTION_SPECS)

    plots = {}

    for identifier in paired_distributions:
        den_specs = paired_distributions[identifier]["den"]

        den_hist = den_specs.getAttribute("histogram")
        den_leg = den_specs.getAttribute("legend")
        if den_leg is None:
            den_leg = ""
        den_rebin = den_specs.getAttribute("rebin")

        num_specs = paired_distributions[identifier]["num"]

        num_hist = num_specs.getAttribute("histogram")
        num_leg = num_specs.getAttribute("legend")
        if num_leg is None:
            num_leg = ""

        num_linecolor = num_specs.getAttribute("linecolor")
        num_linestyle = num_specs.getAttribute("linestyle")
        num_markercolor = num_specs.getAttribute("markercolor")
        num_markerstyle = num_specs.getAttribute("markerstyle")
        num_rebin = num_specs.getAttribute("rebin")

        Xrange = num_specs.getAttribute("Xrange")
        Yrange = num_specs.getAttribute("Yrange")

        if Xrange is not None:
            # find the most inclusive x-axis ranges
            if Xrange_min is not None:
                Xrange_min = Xrange[0] if Xrange[0] < Xrange_min else Xrange_min
            else:
                Xrange_min = Xrange[0]

            if Xrange_max is not None:
                Xrange_max = Xrange[1] if Xrange[1] > Xrange_max else Xrange_max
            else:
                Xrange_max = Xrange[1]

        if Yrange is not None:
            # find the most inclusive y-axis ranges
            if Yrange_min is not None:
                Yrange_min = Yrange[0] if Yrange[0] < Yrange_min else Yrange_min
            else:
                Yrange_min = Yrange[0]

            if Yrange_max is not None:
                Yrange_max = Yrange[1] if Yrange[1] > Yrange_max else Yrange_max
            else:
                Yrange_max = Yrange[1]

        # rebin histograms, if applicable
        if num_rebin and den_rebin and num_rebin == den_rebin:
            num_hist.Rebin(num_rebin)
            den_hist.Rebin(den_rebin)
        elif num_rebin is None and den_rebin is None:
            pass
        else:
            raise Exception(
                "Rebinning inconsistency: numerator and denominator "
                "distributions must be rebinned equally"
            )

        plot_name = num_hist.GetName()

        g = R.TGraphAsymmErrors(num_hist, den_hist, "cp")
        g.SetNameTitle(
            "g_" + plot_name, ";" + num_hist.GetXaxis().GetTitle() + ";Efficiency"
        )
        plots[plot_name] = Plotter.Plot(g, num_leg, "elp", "pe")

        canvas.addMainPlot(plots[plot_name])

        if num_linecolor:
            plots[plot_name].SetLineColor(num_linecolor)
        if num_linestyle:
            plots[plot_name].SetLineStyle(num_linestyle)
        if num_markercolor:
            plots[plot_name].SetMarkerColor(num_markercolor)
        if num_markerstyle:
            plots[plot_name].SetMarkerStyle(num_markerstyle)

    if logy and Yrange_min <= 0.0:
        Yrange_min = 1e-3

    if Xrange:
        print ("setting x ranges: {}, {}".format(Xrange_min, Xrange_max))
        canvas.firstPlot.GetXaxis().SetRangeUser(Xrange_min, Xrange_max)
    if Yrange:
        canvas.firstPlot.GetYaxis().SetRangeUser(Yrange_min, Yrange_max)

    if make_legend:
        canvas.makeLegend(pos="tl", fontscale=0.77)
        canvas.legend.resizeHeight()

    # draw horizontal line at 1
    hline = R.TLine(23.0, 1.0, (150.0 if not Xrange else Xrange_max), 1.0)
    R.SetOwnership(hline, 0)
    hline.SetLineColor(15)
    hline.SetLineStyle(2)
    hline.Draw()

    fname = output_folder + "/" + output_filename
    if logy:
        fname += "_logy"

    canvas.finishCanvas()
    canvas.save(fname, extList=[".pdf", ".root"])
    canvas.deleteCanvas()


if __name__ == "__main__":
    PLOT_SPECS, DISTRIBUTION_SPECS = initialize_specs()

    makeEfficiencyPlots(PLOT_SPECS, DISTRIBUTION_SPECS, "test_genericPlots", logy=False)
