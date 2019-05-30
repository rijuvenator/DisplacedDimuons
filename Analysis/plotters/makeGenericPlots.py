import os
import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter


# Define all distribution and plot properties here and make sure this function is called first
def initialize_specs():
    PLOT_SPECS = {
        "lumi_str": "2016 Cosmics data",
    }

    DISTRIBUTION_SPECS = (
        ### TEMPLATE ###
        #  HistSpecs(
        #     "FILENAME.root",
        #     "(SUB)STRING IDENTIFYING THE DISTRIBUTION TO BE PLOTTED",
        #     histname_exclude = None or [list of strings that are not allowed to be contained in the distribution name],
        #     legend = "LEGEND TEXT",
        #     linecolor = <linecolor> (example: R.kBlue),
        #     rebin=<integer specifying the number of bins to merge during rebinning>,
        #     Xrange=[list containing min and max of x axis range] (example: [-1.0, 5.0])
        # ),
        HistSpecs(
            "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/simulationValidationPlots_regularD0Binning/hadded_Cosmics2016/Cosmics2016_UGMT-bottomOnly_HLT-CosmicSeed.root",
            "DSA_lowerLeg__L1pTresVAR__d0GT0p0__d0LT10p0",
            histname_exclude = [],
            legend = "0 cm < d_{0} < 10 cm",
            linecolor = R.kBlue,
            rebin=5,
            Xrange=[-1.0, 4.0],
        ),
        HistSpecs(
            "/afs/cern.ch/work/s/stempl/private/DDM/analyzer_roots/simulationValidationPlots_regularD0Binning/hadded_Cosmics2016/Cosmics2016_UGMT-bottomOnly_HLT-CosmicSeed.root",
            "DSA_lowerLeg__L1pTresVAR__d0GT100p0__d0LT110p0",
            histname_exclude = [],
            legend = "100 cm < d_{0} < 110 cm",
            linecolor = R.kRed,
            Xrange=[-1.0, 4.0],
            rebin=5,
        ),
    )

    return PLOT_SPECS, DISTRIBUTION_SPECS


class HistSpecs():
    def __init__(self, filepath, histname_identifier, histname_exclude=None, legend=None, linecolor=None, linestyle=None, markercolor=None, markerstyle=None, rebin=None, Xrange=None, Yrange=None, histogram=None):
        self.filepath = filepath
        self.histname_identifier = histname_identifier
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

        types = (
            (filepath, str), (histname_identifier, str), (histname_exclude, list)
        )
        for o, t in types:
            if not isinstance(o, t):
                raise Exception(
                    "Invalid type of {}: should be {}, but is {}".format(
                        o, t, type(o))
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

        print ("[{}/{}] Reading file {}...".format(
            cnt_files, len(DISTRIBUTION_SPECS), filepath)
        )

        f_allhists = HistogramGetter.getHistograms(filepath)

        histogram = None

        for dataset in f_allhists:
            selected_hists_names = getHistNames(
                f_allhists, dataset, histname_identifier, exclude=histname_exclude
            )
            print ("hist names: {}".format(selected_hists_names))

            if len(selected_hists_names) > 1:
                raise Exception("Ambiguous histogram identifier: {} would select the following {} histograms: {}".format(histname_identifier, len(selected_hists_names), '\n'.join(selected_hists_names)))

            for key in selected_hists_names:
                if histogram is None:
                    histogram = f_allhists[dataset][key].Clone()
                else:
                    histogram.Add(f_allhists[dataset][key])

        if histogram:
            print ("\tImported histogram {}".format(histogram.GetName()))
        else:
            print ("\tNo histograms found.")

        # prepare the histogram
        RT.addFlows(histogram)

        if el.getAttribute("histogram") is not None:
            print ("Warning: Histogram already exists in the HistSpecs object and will be overwritten")

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


def makeSimplePlots(PLOT_SPECS, DISTRIBUTION_SPECS, output_filename, output_folder="pdfs/", logy=False, normalize=False, make_legend=True):
    importHistograms(DISTRIBUTION_SPECS)

    canvas = Plotter.Canvas(logy=logy, lumi=PLOT_SPECS["lumi_str"])

    Xrange_min = None
    Xrange_max = None
    Yrange_min = None
    Yrange_max = None

    for el in DISTRIBUTION_SPECS:
        hist = el.getAttribute("histogram")
        leg = el.getAttribute("legend")
        if leg is None: leg = ''
        if normalize: leg += ' (normalized)'
        linecolor = el.getAttribute("linecolor")
        linestyle = el.getAttribute("linestyle")
        markercolor = el.getAttribute("markercolor")
        markerstyle = el.getAttribute("markerstyle")
        Xrange = el.getAttribute("Xrange")
        Yrange = el.getAttribute("Yrange")
        rebin = el.getAttribute("rebin")

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
        if rebin: hist.Rebin(rebin)

        # normalize histograms, if applicable
        if normalize and hist.Integral() != 0:
            hist.Scale(1./hist.Integral())

        plot = Plotter.Plot(hist, leg, "l", "hist")
        canvas.addMainPlot(plot)

        if linecolor: plot.SetLineColor(linecolor)
        if linestyle: plot.SetLineStyle(linestyle)
        if markercolor: plot.SetMarkerColor(markercolor)
        if markerstyle: plot.SetMarkerStyle(markerstyle)
        RT.addBinWidth(plot)

    # set custom axis ranges if specified in DISTRIBUTION_SPECS
    if logy and Yrange_min <= 0.0: Yrange_min = 1e-3
    if Xrange:
        print('setting x ranges: {}, {}'.format(Xrange_min, Xrange_max))
        canvas.firstPlot.GetXaxis().SetRangeUser(Xrange_min, Xrange_max)
    if Yrange: canvas.firstPlot.GetYaxis().SetRangeUser(Yrange_min, Yrange_max)

    if make_legend:
        canvas.makeLegend(pos="tl", fontscale=0.77)
        canvas.legend.resizeHeight()

    fname = output_folder + "/" + output_filename
    if logy: fname += "_logy"
    if normalize: fname += "_norm"

    canvas.finishCanvas()
    canvas.save(fname, extList=[".pdf", ".root"])
    canvas.deleteCanvas()


if __name__ == '__main__':
    PLOT_SPECS, DISTRIBUTION_SPECS = initialize_specs()

    makeSimplePlots(PLOT_SPECS, DISTRIBUTION_SPECS, "test_genericPlots", logy=False, normalize=True)
