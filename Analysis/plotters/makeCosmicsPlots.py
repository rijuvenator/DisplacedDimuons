import sys
import re
import numpy as np
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter


L1RESOLUTIONVARIABLES = ['L1pTres']
L2RESOLUTIONVARIABLES = ['L2pTres']

# L1T_info = 'L1_SingleMuOpen'
# HLT_info = 'HLT_L2Mu10_NoVertex_pp'
L1T_info = 'L1_SingleMuOpen_NotBptxOR_3BX'
HLT_info = 'HLT_L2Mu10_NoVertex_NoBPTX3BX'

RANGES = {
    'pTdiff': (-1.1, 10.),
    'd0'    : (0., 500),
    # 'L1pTres': (-1., 5.),
    # 'L2pTres': (-1., 5.),
    'dimVtxChi2': (0., 60.),
    'dimLxySig': (0., 230.),
    'chi2': (0., 30.),
    'pTSig': (0., 2.),
    'nStations': (0., 10.),
    'nCSCDTHits': (10., 60.),
    'chargeprod': (-1.,2.),
    'charge': (-1.,2.),
}

HISTS = HistogramGetter.getHistograms('../analyzers/roots/check-muonMult_NoBPTX2016_HLT-CosmicSeed_lowerLeg_nCSCDTHitsGT12_nStationsGT1_pTGT20p0_pTSigLT1p0_vtxChiSquLT50p0_pairL1pT5p0AND12p0_bothLegsMatched_requireDimVtx_noTurnOnHists.root')


def makePerSamplePlots(selection=None):
    rebinning_exceptions = ('pTdiff','nCSCDTHits')

    h = {}
    p = {}
    for dataset in HISTS:
        if selection is not None:
            selected_hists_names = getHistNames(dataset, *selection)
        else:
            selected_hists_names = HISTS[dataset]

        for key in selected_hists_names:

            # do not plot empty histograms in the interest of plotting time
            if HISTS[dataset][key].GetEntries() == 0: continue

            if key not in h:
                h[key] = HISTS[dataset][key].Clone()
            else:
                h[key].Add(HISTS[dataset][key])

    for key in h:
        RT.addFlows(h[key])
        if h[key].GetNbinsX() >= 1000:
            if any(['__'+var+'VAR' in key for var in rebinning_exceptions]):
                print('Do not rebin {}'.format(key))
                pass
            else:
                h[key].Rebin(15)
        elif h[key].GetNbinsX() >= 100:
            if any(['__'+var+'VAR' in key for var in rebinning_exceptions]):
                print('Do not rebin {}'.format(key))
                pass
            else:
                h[key].Rebin(5)
        else:
            pass

        if 'lowerHemisphere' in key:
            hs_req = 'lower hemisphere'
        elif 'upperHemisphere' in key:
            hs_req = 'upper hemisphere'
        else:
            hs_req = None

        if 'oppositeCharges' in key:
            pair_charge_req = 'oppositely charged pairs'
        elif 'equalCharges' in key:
            pair_charge_req = 'equally charged pairs'
        else:
            pair_charge_req = None

        if 'posCharge' in key:
            charge_req = 'positive muon tracks'
        elif 'negCharge' in key:
            charge_req = 'negative muon tracks'
        else:
            charge_req = None

        legName = ''
        for req in (hs_req, pair_charge_req, charge_req):
            if req is not None:
                if legName != '': legName += ', '
                legName += req

        p = Plotter.Plot(h[key], legName, 'l', 'hist')

        for is_logy in (True, False):
            if len(HISTS.keys()) > 1:
                lumi = 'NoBPTXRun2016[D+E]-07Aug17'
                dataset_fname = ''
            else:
                search_res = re.search(r'NoBPTXRun2016([A-Z])', HISTS.keys()[0])
                if search_res:
                    era = search_res.group(1)
                else:
                    raise Exception('NoBPTXRun2016[A-Z] identified not found '
                            'in {}'.format(key))

                lumi = 'NoBPTXRun2016{}-07Aug17'.format(era)
                dataset_fname = '_NoBPTXRun2016{}-07Aug17'.format(era)

            fname = 'pdfs/{}{}{}.pdf'.format(key, dataset_fname,
                    ('_logy' if is_logy else ''))

            canvas = Plotter.Canvas(logy=is_logy, lumi=lumi)
            canvas.addMainPlot(p)
            if legName != '':
                canvas.makeLegend(lWidth=.25, pos='tl', fontscale=0.65)
                # canvas.legend.moveLegend()
                canvas.legend.resizeHeight()

            for var in RANGES:
                if '__{}VAR'.format(var) in key:
                    canvas.firstPlot.GetXaxis().SetRangeUser(RANGES[var][0],
                            RANGES[var][1])

            p.SetLineColor(R.kBlue)
            RT.addBinWidth(p)

            # Gauss fit for L2 resolution plots
            if any(['__{}VAR'.format(var) in key for var in L1RESOLUTIONVARIABLES]) or \
                    any(['__{}VAR'.format(var) in key for var in L2RESOLUTIONVARIABLES]):

                # Trigger information for canvas
                pave_triggerinfo = R.TPaveText(.56, .38, .88, .51, 'NDCNB')
                pave_triggerinfo.SetTextAlign(13)
                pave_triggerinfo.SetTextFont(42)
                # pave_triggerinfo.SetTextSize(self.fontsize*.9)
                pave_triggerinfo.SetMargin(0)
                pave_triggerinfo.SetFillStyle(0)
                pave_triggerinfo.SetFillColor(0)
                pave_triggerinfo.SetLineStyle(0)
                pave_triggerinfo.SetLineColor(0)
                pave_triggerinfo.SetBorderSize(0)
                pave_triggerinfo.AddText(0., 1., HLT_info)
                pave_triggerinfo.AddText(0., .5, L1T_info)
                pave_triggerinfo.Draw()

                fit_xmin, fit_xmax = findFitRange(h[key])
                func = R.TF1('f'+key, 'gaus', fit_xmin, fit_xmax)
                func.SetParameters(10., -.1, .5)
                func.SetLineStyle(2)
                func.SetLineColor(R.kBlue+2)
                R.SetOwnership(func,0)
                h[key].Fit('f'+key, 'RQN')
                func.Draw("same")

                pave_gaus = R.TPaveText(.56, .63, .88, .83, 'NDCNB')
                pave_gaus.SetTextAlign(13)
                pave_gaus.SetTextFont(42)
                # pave_gaus.SetTextSize(self.fontsize*.9)
                pave_gaus.SetMargin(0)
                pave_gaus.SetFillStyle(0)
                pave_gaus.SetFillColor(0)
                pave_gaus.SetLineStyle(0)
                pave_gaus.SetLineColor(0)
                pave_gaus.SetBorderSize(0)
                pave_gaus.AddText(0., 1., 'Gaussian fit around maximum:')
                pave_gaus.AddText(.06, .65, 'Mean = {:2.3f}'.format(func.GetParameter(1)))
                pave_gaus.AddText(.06, .45, 'Sigma = {:2.3f}'.format(func.GetParameter(2)))
                pave_gaus.AddText(.06, .25, '#chi^{{2}} = {:2.3f}'.format(func.GetChisquare()))

                # count the histogram contents to the right of the upper
                # fit limit (to get an estimate for the content in the tail)
                h_content = 0
                h_content_tail = 0
                fit_xmax_bin = h[key].FindBin(fit_xmax)
                for b in range(1, h[key].GetNbinsX()+1):
                    h_content += h[key].GetBinContent(b)
                    if b > fit_xmax_bin:
                        h_content_tail += h[key].GetBinContent(b)

                pave_gaus.AddText(.06, .05, 'Entries above {:2.2f} (max. fit range): {:2.1f}%'.format(fit_xmax, 100.*h_content_tail/h_content))
                pave_gaus.Draw()

                canvas.legend.moveLegend(X=.393, Y=-.01)
            else:
                # Trigger information for canvas
                pave_triggerinfo = R.TPaveText(.4, .75, .72, .88, 'NDCNB')
                pave_triggerinfo.SetTextAlign(13)
                pave_triggerinfo.SetTextFont(42)
                # pave_triggerinfo.SetTextSize(self.fontsize*.9)
                pave_triggerinfo.SetMargin(0)
                pave_triggerinfo.SetFillStyle(0)
                pave_triggerinfo.SetFillColor(0)
                pave_triggerinfo.SetLineStyle(0)
                pave_triggerinfo.SetLineColor(0)
                pave_triggerinfo.SetBorderSize(0)
                pave_triggerinfo.AddText(0., 1., HLT_info)
                pave_triggerinfo.AddText(0., .5, L1T_info)
                pave_triggerinfo.Draw()
     
                pave = canvas.makeStatsBox(p, color=R.kBlue)

            pave_triggerinfo.Draw()


            # find the corresponding d0 distribution in the given d0 bin
            # and display its mean
            try:
                current_var = re.findall(r'__(.+)VAR', key)
                if len(current_var) == 1:
                    current_var = current_var[0].split('_')[-1]
                    if current_var != 'd0' and all([c in key for c in ('__d0GT','__d0LT')]):
                        d0_hist = key.replace('__{}VAR'.format(current_var), '__d0VAR')
                        for idataset,dataset in enumerate(HISTS):
                            if idataset == 0:
                                h_d0 = HISTS[dataset][d0_hist].Clone()
                            else:
                                h_d0.Add(HISTS[dataset][d0_hist])

                        d0_mean = h_d0.GetMean()
                        # d0_mean = HISTS[dataset][d0_hist].GetMean()

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

                        pave_d0info = R.TPaveText(.56, .53, .88, .61, 'NDCNB')
                        pave_d0info.SetTextAlign(13)
                        pave_d0info.SetTextFont(42)
                        pave_d0info.SetMargin(0)
                        pave_d0info.SetFillStyle(0)
                        pave_d0info.SetFillColor(0)
                        pave_d0info.SetLineStyle(0)
                        pave_d0info.SetLineColor(0)
                        pave_d0info.SetBorderSize(0)
                        pave_d0info.AddText(0., 1., 
                                '{} cm < d_{{0}} < {} cm'.format(d0_min, d0_max))
                        pave_d0info.AddText(0., 0., '#LTd_{{0}}#GT = {:4.3f} cm'.format(d0_mean))
                        pave_d0info.Draw()
            except KeyError:
                # not all of the histograms have d0 equivalents (e.g.,
                # 'oppositeCharges' pair histos,...)
                print('[PLOTTER WARNING] Error processing d0 information '
                        'for {}; will not be printed on canvas'.format(key))

            canvas.cleanup(fname)

    return


def makeTurnOnPlots():

    # these intervals must be equal (or a subset) of the ones defined in the
    # ../analyzers/cosmicsPlots.py script
    d0intervals = [(None,None)]
    # d0intervals += [(i,i+2.5) for i in np.arange(0., 10., 2.5)]
    # d0intervals += [(i,i+5.0) for i in np.arange(0., 20., 5.0)]
    # d0intervals += [(i,i+10.0) for i in np.arange(20., 100., 10.0)]
    d0intervals += ([(0,10),(10,50),(50,100),(100,150),(150,250),(250,350),(250,1000)])

    for d0min,d0max in d0intervals:
        hden = {}
        hnum = {}
        p = {}
        g = {}
        for i,dataset in enumerate(HISTS):
            if d0min is None or d0max is None:
                hnums = getHistNames(dataset, 'DSA','pTVAREffNum', exclude=['d0GT','d0LT','alpha'])
                hdens = getHistNames(dataset, 'DSA','pTVAREffDen', exclude=['d0GT','d0LT','alpha'])
            else:
                hnums = getHistNames(dataset, 'DSA','pTVAREffNum',
                        'd0GT'+str(d0min).replace('.','p'),
                        'd0LT'+str(d0max).replace('.','p'), exclude=['alpha'])
                hdens = getHistNames(dataset, 'DSA','pTVAREffDen',
                    'd0GT'+str(d0min).replace('.','p'),
                    'd0LT'+str(d0max).replace('.','p'), exclude=['alpha'])

            for hname in hnums:
                current_hist = HISTS[dataset][hname].Clone()
                current_hist.SetDirectory(0)
                current_hist.Sumw2()
                RT.addFlows(current_hist)
                if current_hist.GetNbinsX() >= 1000: current_hist.Rebin(10)
                elif current_hist.GetNbinsX() >= 100: current_hist.Rebin(5)
                else: pass

                if i==0:
                    hnum[hname] = current_hist
                else:
                    hnum[hname].Add(current_hist)

            for hname in hdens:
                current_hist = HISTS[dataset][hname].Clone()
                current_hist.SetDirectory(0)
                current_hist.Sumw2()
                RT.addFlows(current_hist)
                if current_hist.GetNbinsX() >= 1000: current_hist.Rebin(10)
                elif current_hist.GetNbinsX() >= 100: current_hist.Rebin(5)
                else: pass

                if i==0:
                    hden[hname] = current_hist
                else:
                    hden[hname].Add(current_hist)


        if len(hden) > 1: raise NotImplementedError('Too many denumerator histos - not yet implemented')
        elif len(hden) == 0: raise Exception('No denominator histogram found')
        hden = hden[hden.keys()[0]]

        for key in hnum:
            canvas = Plotter.Canvas(lumi='NoBPTXRun2016D-07Aug17')

            g[key] = R.TGraphAsymmErrors(hnum[key], hden, 'cp')
            g[key].SetNameTitle('g_'+key, ';'+hnum[key].GetXaxis().GetTitle()+';Efficiency')
            p[key] = Plotter.Plot(g[key], key, 'elp', 'pe')

            canvas.addMainPlot(p[key])
            p[key].setColor(R.kBlue)
            canvas.makeLegend(pos='br')
            canvas.legend.moveLegend(X=-.47)
            canvas.legend.moveLegend(Y=.05)
            canvas.legend.resizeHeight()
            canvas.firstPlot.GetXaxis().SetRangeUser(0., 150.)
            canvas.firstPlot.GetYaxis().SetRangeUser(0., 1.1)

            L2pTcut = re.findall(r'_pTGT(\d+)p(\d+)', key)
            if len(L2pTcut) > 1:
                raise Exception('Ambiguities in L2 pT threshold identification: {}'.format(L2pTcut))

            L2pTcut = float('.'.join(L2pTcut[0]))
            pTthreshold_str = R.TLatex()
            pTthreshold_str.SetTextSize(0.035)
            pTthreshold_str.DrawLatex(100., .56, 'p_{{T}}^{{L2}} > {} GeV'.format(L2pTcut))

            if L2pTcut > 0.0:
                L2vline = R.TLine(L2pTcut, 0., L2pTcut, 1.)
                R.SetOwnership(L2vline, 0)
                L2vline.SetLineColor(15)
                L2vline.SetLineStyle(1)
                L2vline.Draw()

            L1pTcut = re.findall(r'_L1pTGT(\d+)p(\d+)', key)
            if len(L1pTcut) > 1:
                raise Exception('Ambiguities in L1 pT threshold identification: {}'.format(L1pTcut))
            elif len(L1pTcut) == 0:
                raise Exception('No L1 pT threshold identified in {}'.format(key))

            L1pTcut = float('.'.join(L1pTcut[0]))
            pTthreshold_str = R.TLatex()
            pTthreshold_str.SetTextSize(0.035)
            pTthreshold_str.DrawLatex(100., .48, 'p_{{T}}^{{L1}} > {} GeV'.format(L1pTcut))

            if L1pTcut > 0.0:
                L1vline = R.TLine(L1pTcut, 0., L1pTcut, 1.)
                R.SetOwnership(L1vline, 0)
                L1vline.SetLineColor(15)
                L1vline.SetLineStyle(2)
                L1vline.Draw()

            if d0min is not None and d0max is not None:
                selection_str = R.TLatex()
                selection_str.SetTextSize(0.035)
                selection_str.DrawLatex(100., .4, '{} cm  < d_{{0}} < {} cm'.format(d0min,d0max))

            canvas.cleanup('pdfs/TETurnOn_{}.pdf'.format(key))


def makeCombinedPlots(categories, selection=None, exclude=None, logic='and'):
    rebinning_exceptions = ('nCSCDTHits',)

    h = {}
    p = {}

    # import all relevant histograms
    for dataset in HISTS:
        if selection and exclude:
            selected_hists_names = getHistNames(dataset, *selection,
                    exclude=exclude, logic=logic)
        elif selection and not exclude:
            selected_hists_names = getHistNames(dataset, *selection, logic=logic)
        elif not selection and exclude:
            selected_hists_names = getHistNames(dataset, '', exclude=exclude, logic=logic)
        else:
            selected_hists_names = HISTS[dataset]

        for key in selected_hists_names:
            if not any([cat in key for cat,__ in categories]): continue

            search_res = re.search(r'__(.+)VAR', key)
            if search_res:
                variable = search_res.group(1)
            else:
                print('Skipping {} (unidentifiable variable)...'.format(key))
                continue

            if variable not in h.keys():
                h[variable] = {}

            for category,__ in categories:
                if not category in key: continue

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
                    print('Do not rebin for variable {}'.format(variable))
                    pass
                else:
                    h[variable][category].Rebin(15)

            elif h[variable][category].GetNbinsX() >= 100:
                if variable in rebinning_exceptions:
                    print('Do not rebin for variable {}'.format(variable))
                    pass
                else:
                    h[variable][category].Rebin(5)

            else:
                pass

    # start creating plots
    for variable in h:
        p[variable] = {}

        # find the best vertical axes ranges
        realmin = float('inf')
        realmax = -float('inf')

        for category,category_name in categories:
            p[variable][category] = Plotter.Plot(h[variable][category],
                    category_name, 'l', 'hist')

            key_fname = h[variable][category].GetName()
            key_fname = key_fname.replace(category,'')
            if len(HISTS.keys())>1:
                search_res = re.search(r'(_*?NoBPTXRun\d+[A-Z][_-]07Aug17)',
                        key_fname)
                if search_res:
                    key_fname = key_fname.replace(search_res.group(0), '')
                else:
                    print('Could not identify datset. Dataset name will not be '
                            'stripped from the output file names')

            if p[variable][category].GetMaximum() > realmax:
                realmax = p[variable][category].GetMaximum()

            if p[variable][category].GetMaximum() < realmin:
                realmin = p[variable][category].GetMinimum()

        for is_logy in (True, False):
            palette = Plotter.ColorPalette([867,417,600,600,801,632])
            fname = 'pdfs/comb_{}{}.pdf'.format(key_fname,
                    ('_logy' if is_logy else ''))
            canvas = Plotter.Canvas(logy=is_logy, lumi='NoBPTXRun2016[D+E]-07Aug17')
            for category,category_name in categories:
                canvas.addMainPlot(p[variable][category])
                p[variable][category].SetLineColor(palette.getNextColor())
                if 'goodQuality' in category:
                    p[variable][category].SetLineStyle(2)

                RT.addBinWidth(p[variable][category])

            if variable in RANGES:
                canvas.firstPlot.GetXaxis().SetRangeUser(
                        RANGES[variable][0], RANGES[variable][1])

            canvas.makeLegend(lWidth=.3, pos='tr', fontscale=0.65)
            canvas.legend.resizeHeight()
            canvas.legend.moveLegend(X=-.2, Y=-.13)

            # trigger information for canvas
            pave_triggerinfo = R.TPaveText(.4, .75, .72, .88, 'NDCNB')
            pave_triggerinfo.SetTextAlign(13)
            pave_triggerinfo.SetTextFont(42)
            # pave_triggerinfo.SetTextSize(self.fontsize*.9)
            pave_triggerinfo.SetMargin(0)
            pave_triggerinfo.SetFillStyle(0)
            pave_triggerinfo.SetFillColor(0)
            pave_triggerinfo.SetLineStyle(0)
            pave_triggerinfo.SetLineColor(0)
            pave_triggerinfo.SetBorderSize(0)
            pave_triggerinfo.AddText(0., 1., HLT_info)
            pave_triggerinfo.AddText(0., .5, L1T_info)
            pave_triggerinfo.Draw()

            if is_logy and realmin == 0: realmin = 0.5
            canvas.firstPlot.GetYaxis().SetRangeUser(realmin*.8, realmax*1.2)

            # canvas.cleanup(fname.replace('.pdf','.root'))
            canvas.cleanup(fname)


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


alpha_categories = (
    ('__0p0alpha0p3', '0 < #alpha < 0.3'),
    ('__0p3alpha2p8', '0.3 < #alpha < 2.8'),
    ('__2p8alphaPi', '2.8 < #alpha < #pi'),
    ('__goodQuality_2p8alphaPi', '2.8 < #alpha < #pi (#chi^{2}/ndof < 4)'),
    ('__SSpairs_2p8alphaPi', '2.8 < #alpha < #pi (same-sign pairs)'),
    ('__noOppositeMuonMatch_0p0alpha2p8', '0 < #alpha < 2.8 (no match with opposite muon)'),
)

makeCombinedPlots(alpha_categories, selection=['DSA__alphaVAR','DSA__chargeVAR','DSA__nStationsVAR','DSA__dNStationsVAR','DSA__nCSCDTHitsVAR','DSA__dNCSCDTHitsVAR','DSA__pSigVAR','DSA__pTVAR','DSA__dimVtxChi2','DSA__dimCosAlpha','DSA__dimLxySig','DSA__chi2VAR','DSA__massVAR','DSA__chargeprodVAR','DSA__dimLxyVAR','DSA__pTdiffVAR','DSA__pairPTVAR','DSA__dEtaVAR','DSA__dPhiVAR','DSA__dD0VAR','DSA__dChi2VAR','DSA__pTSigVAR'], logic='or', exclude=['__d0GT','__d0LT','Eff','_noSelections'])

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
makePerSamplePlots(['DSAmuonMultiplicity'])


# makeTurnOnPlots()
