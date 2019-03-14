import sys
import re
from array import array
import numpy as np
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter


# HISTS = HistogramGetter.getHistograms('../analyzers/test.root')
HISTS = HistogramGetter.getHistograms('../analyzers/roots/simValidation_upperHSmuon_cosmicsPlots_alphaGT2p9_etaLT1p2_nCSCDTHitsGT12_nStationsGT1_pTSigLT1p0_largestAlphaPair_oppositeHS_oneLegMatched_noSimpleHists_NoBPTXRun2016E-07Aug17.root')


def interpolateX(x0,y0,x1,y1,y):
    # Linearly interpolate between (x0,y0) and (x1,y1), return the x value for y
    return (x1-x0)*(y-y0)/(y1-y0)+x0


def findFitRange(h, percentage=0.3):
    nbins_to_check = 1
    peakval = h.GetMaximum()
    peakbin = h.GetMaximumBin()

    threshold = percentage * peakval

    # find the lower limit
    for b in range(1, peakbin+1):
        if h.GetBinContent(b) > threshold:
            # check following bins to make sure this is not a
            # statistical fluctuation
            is_fluctuation = False
            for bb in range(b+1, b+nbins_to_check):
                if h.GetBinContent(bb) < h.GetBinContent(b):
                    is_fluctuation = True

            if not is_fluctuation:
                if b > 1:
                    range_min = interpolateX(
                            h.GetXaxis().GetBinCenter(b-1),
                            h.GetBinContent(b-1),
                            h.GetXaxis().GetBinCenter(b),
                            h.GetBinContent(b),
                            threshold)
                else:
                    range_min = h.GetXaxis().GetBinLowEdge(b)

                break

    else:
        range_min = h.GetXaxis().GetBinLowEdge(1)

    # find the upper limit
    for b in range(peakbin+1, h.GetNbinsX()+1):
        if h.GetBinContent(b) < threshold:
            # check following bins to make sure this is not a
            # statistical fluctuation
            is_fluctuation = False
            for bb in range(b+1, b+nbins_to_check):
                if h.GetBinContent(bb) > h.GetBinContent(b):
                    is_fluctuation = True

            if not is_fluctuation:
                if b < h.GetNbinsX()+1:
                    range_max = interpolateX(
                            h.GetXaxis().GetBinCenter(b-1),
                            h.GetBinContent(b-1),
                            h.GetXaxis().GetBinCenter(b),
                            h.GetBinContent(b),
                            threshold)
                else:
                    range_max = h.GetXaxis().GetBinLowEdge(b+1)

                break

    else:
        range_max = h.GetXaxis().GetBinLowEdge(h.GetNbinsX())

    return range_min, range_max


def getHistNames(dataset, *args, **kwargs):
    logic = kwargs.pop('logic', 'and')
    exclude_list = kwargs.pop('exclude', None)
    if kwargs: raise Exception('Invalid argument(s): {}'.format(kwargs))

    exclude = None
    if exclude_list is not None:
        exclude = re.compile('|'.join([e for e in exclude_list]))

    results = []
    # for dataset in HISTS:
    for key in HISTS[dataset]:
        if exclude is not None and exclude.search(key): continue
        
        is_match = False
        if logic == 'and':
            if all([re.search(a, key) is not None for a in args]):
                is_match = True
            else:
                pass

        elif logic == 'or':
            if any([re.search(a, key) is not None for a in args]):
                is_match = True
            else:
                pass

        else:
            raise Exception('logic must be either \'and\' or \'or\'')

        if is_match: results.append(key)

    return results


def makeResolutionVSd0Plots():
    h = {}
    p = {}
    data_resVsd0 = {'d0_mean': [], 'd0_min': [], 'd0_max': [],
            'res_mean': [], 'res_mean_err': [], 'res_std': [], 'res_std_err': [],
            'fraction_in_tail': [], 'fraction_in_tail_err': [],
            'fit_quality': [], 'fit_quality_err': []}

    # (sub)set of d0 bins which are to be plotted (they must exist as histograms
    # in the cosmicsPlots.py analyzer output file)
    d0intervals = []
    # d0intervals += [(i,i+2.5) for i in np.arange(0., 10., 2.5)]
    d0intervals += [(i,i+5.0) for i in np.arange(0., 20., 5.0)]
    d0intervals += [(i,i+10.0) for i in np.arange(20., 100., 10.0)]

    # make sure that all given numbers are actually floats
    d0intervals = [(float(l), float(u)) for l,u in d0intervals]

    resvar = 'L1pTresVAR'

    if 'L2pTres' in resvar:
        h_ylabel_mean = '#mu[(p_{T}^{L2} - p_{T}^{DSA}) / p_{T}^{DSA}]  #it{(data)}'
        h_ylabel_std = '#sigma[(p_{T}^{L2} - p_{T}^{DSA}) / p_{T}^{DSA}]  #it{(data)}'
        h_ylabel_fraction_in_tail = 'fraction in tails above fit limit  #it{(data)}'
        h_ylabel_fitquality = 'fit #chi^{2} / 10  #it{(data)}'
        h_xlabel = 'd_{0} [cm]'
    elif 'L1pTres' in resvar:
        h_ylabel_mean = '#mu[(p_{T}^{L1} - p_{T}^{DSA}) / p_{T}^{DSA}]  #it{(data)}'
        h_ylabel_std = '#sigma[(p_{T}^{L1} - p_{T}^{DSA}) / p_{T}^{DSA}]  #it{(data)}'
        h_ylabel_fraction_in_tail = 'fraction in tails above fit limit  #it{(data)}'
        h_ylabel_fitquality = 'fit #chi^{2} / 10  #it{(data)}'
        h_xlabel = 'd_{0} [cm]'
    else:
        h_ylabel_mean = ''
        h_ylabel_std = ''
        h_ylabel_fraction_in_tail = ''
        h_ylabel_fitquality = ''
        h_xlabel = 'd_{0} [cm]'

    for ref in HISTS:
        p[ref] = {}
        resolution_hists = getHistNames(ref, 'DSA', resvar, exclude=['EffNum','EffDen'])

        for key in resolution_hists:
            if not all([d0str in key for d0str in ['__d0GT','__d0LT']]):
                continue

            h = HISTS[ref][key].Clone()
            RT.addFlows(h)

            # NB: if comparing to distributions created by the cosmicsPlots.py
            # script, make sure that the binning is the same!
            if h.GetNbinsX() >= 1000:
                h.Rebin(10)
            elif h.GetNbinsX() >= 100:
                h.Rebin(5)
            else:
                pass

            # determining the d0 mean (horizontal histogram axis)
            d0_histname = key.replace('__{}'.format(resvar), '__d0VAR')
            if d0_histname == key:
                raise Exception('Error parsing the name of the d0 histogram')

            d0_hist = d0_histname
            d0_mean = HISTS[ref][d0_hist].GetMean()
            d0_min = re.findall(r'__d0GT(\d+)p(\d+)', d0_hist)
            if len(d0_min) > 0:
                d0_min = float('{}.{}'.format(d0_min[0][0], d0_min[0][1]))
            else:
                d0_min = float(re.findall(r'__d0GT(\d+)', d0_hist)[0])

            d0_max = re.findall(r'__d0LT(\d+)p(\d+)', d0_hist)
            if len(d0_max) > 0:
                d0_max = float('{}.{}'.format(d0_max[0][0], d0_max[0][1]))
            else:
                d0_max = float(re.findall(r'__d0LT(\d+)', d0_hist)[0])


            if (d0_min, d0_max) not in d0intervals:
                print('[PLOTTER INFO] Skipping d0 bin ({}, {}).'.format(d0_min, d0_max))
                continue

            # determining the resolution mean (vertical histogram axis)
            fit_xmin, fit_xmax = findFitRange(h)

            func = R.TF1('f'+key, 'gaus', fit_xmin, fit_xmax)
            func.SetParameters(10., -.1, .5)
            R.SetOwnership(func, 0)
            h.Fit('f'+key, 'RQN')
            res_mean = func.GetParameter(1)
            res_mean_err = func.GetParError(1)
            res_std = func.GetParameter(2)
            res_std_err = func.GetParError(2)
            fit_chisquare = func.GetChisquare()

            # count the histogram contents to the right of the upper fit limit
            # to get an estimate for the content in the tails
            h_content = 0
            h_content_tail = 0
            fit_xmax_bin = h.FindBin(fit_xmax)
            for b in range(1, h.GetNbinsX()+1):
                h_content += h.GetBinContent(b)
                if b > fit_xmax_bin:
                    h_content_tail += h.GetBinContent(b)

            # collect all relevant data (so that the final histograms can be
            # created dynamically and accordingly)
            data_resVsd0['d0_mean'].append(d0_mean)
            data_resVsd0['d0_min'].append(float(d0_min))
            data_resVsd0['d0_max'].append(float(d0_max))
            data_resVsd0['res_mean'].append(res_mean)
            data_resVsd0['res_mean_err'].append(res_mean_err)
            data_resVsd0['res_std'].append(res_std)
            data_resVsd0['res_std_err'].append(res_std_err)
            data_resVsd0['fit_quality'].append(fit_chisquare / 10.)
            data_resVsd0['fit_quality_err'].append(0.)  # needed for looping over distributions
            data_resVsd0['fraction_in_tail'].append(1.*h_content_tail/h_content if h_content != 0 else 0.)
            data_resVsd0['fraction_in_tail_err'].append(0.)  # needed for looping over distributions


        # sort data in ascending order of d0_min
        d0_min_list = (data_resVsd0['d0_min'])
        for datalist in data_resVsd0.keys():
            data_resVsd0[datalist] = [x for _,x in sorted(
                zip(d0_min_list, data_resVsd0[datalist]))]


        canvas = Plotter.Canvas(lumi='NoBPTXRun2016E-07Aug17')

        # specifiy distribution properties:
        # (name, ylabel, errors along which axes, marker style)
        distributions = (
                ('res_mean',         h_ylabel_mean,             'XY', R.kMultiply),
                ('res_std',          h_ylabel_std,              'XY', None),
                ('fraction_in_tail', h_ylabel_fraction_in_tail, ''  , None),
                # ('fit_quality',      h_ylabel_fitquality,       ''  , None),
        )

        # find the best y axis range
        yrange_lowerEdges = []
        yrange_upperEdges = []
        for distribution,__,__,__ in distributions:
            max_yrange = max([val+err for val,err in zip(
                data_resVsd0[distribution], data_resVsd0[distribution+'_err'])])
            yrange_upperEdges.append(max_yrange)

            min_yrange = min([val-err for val,err in zip(
                data_resVsd0[distribution], data_resVsd0[distribution+'_err'])])
            yrange_lowerEdges.append(min_yrange)

        max_yrange = max(yrange_upperEdges) * 1.5
        min_yrange = min(yrange_lowerEdges) * 1.05

        # overrule dynamic y range limits, if they are too far off
        if max_yrange > 3.0: max_yrange = 3.0
        if min_yrange < -1.5: min_yrange = -1.5

        color_palette = Plotter.ColorPalette()

        for distribution,name,error_axes,markerstyle in distributions:
            g_n = int(len(data_resVsd0['d0_min']))
            g_x = array('d', data_resVsd0['d0_mean'])
            g_y = array('d', data_resVsd0[distribution])
            if 'x' in error_axes.lower():
                g_exl = array('d', [mean-lowedge for mean,lowedge in zip(
                    data_resVsd0['d0_mean'], data_resVsd0['d0_min'])])
                g_exh = array('d', [upedge-mean for mean,upedge in zip(
                    data_resVsd0['d0_mean'], data_resVsd0['d0_max'])])
            else:
                g_exl = array('d', [0. for mean in data_resVsd0['d0_mean']])
                g_exh = array('d', [0. for mean in data_resVsd0['d0_mean']])

            if 'y' in error_axes.lower():
                g_eyl = array('d', data_resVsd0[distribution+'_err'])
                g_eyh = array('d', data_resVsd0[distribution+'_err'])
            else:
                g_eyl = array('d', [0. for mean in data_resVsd0[distribution]])
                g_eyh = array('d', [0. for mean in data_resVsd0[distribution]])

            g_resVsd0 = R.TGraphAsymmErrors(g_n, g_x, g_y,
                    g_exl, g_exh, g_eyl, g_eyh)
            g_resVsd0.SetTitle(name)
            if markerstyle is not None: g_resVsd0.SetMarkerStyle(markerstyle)
            p[ref][distribution] = Plotter.Plot(g_resVsd0, '', 'elp', 'pe')

            canvas.addMainPlot(p[ref][distribution])

            p[ref][distribution].setColor(color_palette.getNextColor())

        # add horizontal line at zero
        zero_line_horizontal = R.TLine(data_resVsd0['d0_min'][0], 0.,
                data_resVsd0['d0_max'][-1], 0.)
        R.SetOwnership(zero_line_horizontal, 0)
        zero_line_horizontal.SetLineColor(R.kGray)
        zero_line_horizontal.SetLineStyle(2)
        zero_line_horizontal.Draw()

        canvas.firstPlot.SetMinimum(min_yrange)
        canvas.firstPlot.SetMaximum(max_yrange)
        canvas.firstPlot.GetXaxis().SetTitle(h_xlabel)
        canvas.firstPlot.GetYaxis().SetTitle('Fit parameter (see legend)')

        canvas.makeLegend(lWidth=0.43, pos='tr', fontscale=.75)
        canvas.cleanup('pdfs/resVsd0_{}_{}.pdf'.format(resvar, ref))


makeResolutionVSd0Plots()
