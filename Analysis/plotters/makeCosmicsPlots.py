import sys
import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter


OUTPUT_PATH = 'pdfs/'


HISTS = HistogramGetter.getHistograms('../analyzers/test.root')
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/testing/test_cosmicsPlots_alphaGT2p9_nCSCDTHitsGT12_nStationsGT1_pTSigLT1p0_NoBPTXRun2016E-07Aug17.root')
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/testing/cosmicsPlots_alphaGT2p9_nCSCDTHitsGT12_nStationsGT1_pTSigLT1p0_NoBPTXRun2016E-07Aug17.root')
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/testing/cosmicsPlots_2016E-full_withOHrequirement_maxAlphaPair_wAlphaCut_wTurnOnHistos_d0Binning-corrected.root')
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/testing/cosmicsPlots_2016E-full_withOHrequirement_maxAlphaPair_wAlphaCut_wTurnOnHistos-corrected.root')
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/testing/cosmicsPlots_2016E-full_withOHrequirement_maxAlphaPair_wAlphaCut_wTurnOnHistos.root')
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/testing/cosmicsPlots_2016E-full_withOHrequirement_maxAlphaPair_noAlphaCut.root')
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/testing/cosmicsPlots_2016E-full_woOHrequirement_maxAlphaPair_noAlphaCut.root')

def makePerSamplePlots(selection=None, selection_exclude=None):
    ranges = {
            'pTdiff': (-1.5, 30.),
            'd0': (0., 500),
    }

    h = {}
    p = {}
    for ref in HISTS:
        if selection is not None:
            selected_hists_names = getHistNames(ref, *selection)

        for key in HISTS[ref]:
            if selection is not None and key not in selected_hists_names:
                continue

            h = HISTS[ref][key].Clone()
            RT.addFlows(h)
            if h.GetNbinsX() >= 1000:
                h.Rebin(10)
            elif h.GetNbinsX() >= 100:
                h.Rebin(5)
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

            p = Plotter.Plot(h, legName, 'l', 'hist')

            for is_logy in (True, False):
                fname = 'pdfs/{}.pdf'.format(key if not is_logy else key+'_logy')
                canvas = Plotter.Canvas(logy=is_logy, lumi='NoBPTXRun2016E-07Aug17')
                canvas.addMainPlot(p)
                if legName != '':
                    canvas.makeLegend(lWidth=.25, pos='tl', fontscale=0.65)
                    canvas.legend.moveLegend()
                    canvas.legend.resizeHeight()

                for var in ranges:
                    if '_{}'.format(var) in key and not '__{}'.format(var) in key:
                        canvas.firstPlot.GetXaxis().SetRangeUser(ranges[var][0],
                                ranges[var][1])

                p.SetLineColor(R.kBlue)
                RT.addBinWidth(p)

                pave = canvas.makeStatsBox(p, color=R.kBlue)
                canvas.cleanup(fname)

    return


def makeTurnOnPlots():

    # these intervals must be equal (or a subset) of the ones defined in the
    # ../analyzers/cosmicsPlots.py script
    d0intervals = (
        (None, None),
        (0,10),
        (10,50),
        (0,50),
        (50,100),
        (100,150),
        (150,250),
        (250,350),
        (250,1000),
        (350,1000),
    )

    for d0min,d0max in d0intervals:
        hden = {}
        hnum = {}
        p = {}
        g = {}
        for i,dataset in enumerate(HISTS):
            if d0min is None or d0max is None:
                hnums = getHistNames(dataset, 'DSA','pTEffNum', exclude=['d0GT','d0LT'])
                hdens = getHistNames(dataset, 'DSA','pTEffDen', exclude=['d0GT','d0LT'])
            else:
                hnums = getHistNames(dataset, 'DSA','pTEffNum', 'd0GT'+str(d0min), 'd0LT'+str(d0max))
                hdens = getHistNames(dataset, 'DSA','pTEffDen', 'd0GT'+str(d0min), 'd0LT'+str(d0max))


            for hname in hnums:
                current_hist = HISTS[dataset][hname].Clone()
                current_hist.SetDirectory(0)
                current_hist.Sumw2()
                RT.addFlows(current_hist)
                if current_hist.GetNbinsX() >= 1000: current_hist.Rebin(10)
                elif current_hist.GetNbinsX() >= 100: current_hist.Rebin(5)
                else: pass #current_hist.Rebin(5)

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
                else: pass #current_hist.Rebin(5)

                if i==0:
                    hden[hname] = current_hist
                else:
                    hden[hname].Add(current_hist)


        if len(hden) > 1: raise NotImplementedError('Too many denumerator histos - not yet implemented')
        hden = hden[hden.keys()[0]]

        for key in hnum:
            canvas = Plotter.Canvas(lumi='NoBPTXRun2016E-07Aug17')

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


def getHistNames(dataset, *args, **kwargs):
    logic = kwargs.pop('logic', 'and')
    exclude_list = kwargs.pop('exclude', None)
    if kwargs: raise Exception('Invalid argument(s): {}'.format(kwargs))

    exclude = None
    if exclude_list is not None:
        exclude = re.compile('|'.join([e for e in exclude_list]))

    results = []
    for dataset in HISTS:
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


makePerSamplePlots()
# makePerSamplePlots(['DSA','L1pTres'])
makeTurnOnPlots()
