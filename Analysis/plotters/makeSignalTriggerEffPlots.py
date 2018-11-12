import sys
import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import HistogramGetter

LxyBins = (
    (0, 'Inf'),
    (0, 25),
    (25, 50),
    (50, 100),
    (100, 200),
    (200, 350),
    (100, 350),
)

OUTPUT_PATH = 'pdfs/LxyScan/'

for LXYMIN,LXYMAX in LxyBins:
    # get histograms
    FILENAME_IN = '../analyzers/roots/testing/STEplots_cosAlphaGT-0p8_d0LT7p0_deltaRleftGT0p5_deltaRrightGT2p5_etaLT2p0_massGT15p0_pTGT30p0_LxyGT{}_LxyLT{}_HTo2XTo2Mu2J.root'
    FILENAME_OUT_TEMPLATE = 'cosAlphaGT-0p8_d0LT7p0_deltaRleftGT0p5_deltaRrightGT2p5_etaLT2p0_massGT15p0_pTGT30p0_LxyGT{}_LxyLT{}_HTo2XTo2Mu2J.root'

    FILENAME_OUT = '{}_' + FILENAME_OUT_TEMPLATE + '_{}Xaxis_HTo2XTo{}_{}.pdf'

    HISTS = HistogramGetter.getHistograms(FILENAME_IN.format(LXYMIN,LXYMAX))
    f = R.TFile.Open(FILENAME_IN.format(LXYMIN,LXYMAX))

    rbins1 = 40
    rbins2 = 40
    xmax1 = 500.
    xmax2 = 500.

    FRACTIONS = {
        '2Mu2J': {
            '125_20_13':   [13.67,100.0,0.0],
            '125_20_130':  [14.01,76.507,23.494],
            '125_20_1300': [9.353,28.205,71.795],
            '125_50_50':   [14.66,97.892,2.108],
            '125_50_500':  [14.943,39.505,60.495],
            '125_50_5000': [9.403,8.691,91.309],
            '200_20_7':    [31.937,100.0,0.0],
            '200_20_70':   [31.724,92.867,7.133],
            '200_20_700':  [25.317,40.277,59.723],
            '200_50_20':   [31.276,99.961,0.039],
            '200_50_200':  [31.04,66.832,33.168],
            '200_50_2000': [24.467,17.62,82.38],
            '400_20_4':    [56.88,100.0,0.0],
            '400_20_40':   [57.053,98.778,1.222],
            '400_20_400':  [45.9,60.654,39.346],
            '400_50_8':    [55.477,100.0,0.0],
            '400_50_80':   [55.829,92.292,7.708],
            '400_50_800':  [48.343,36.877,63.123],
            '400_150_40':  [67.093,99.796,0.204],
            '400_150_400': [67.053,64.513,35.487],
            '400_150_4000':[54.71,18.61,81.39],
            '1000_20_2':   [75.869,100.0,0.0],
            '1000_20_20':  [75.47,99.961,0.039],
            '1000_20_200': [60.067,84.403,15.597],
            '1000_50_4':   [74.837,100.0,0.0],
            '1000_50_40':  [74.468,98.914,1.086],
            '1000_50_400': [63.82,60.791,39.209],
            '1000_150_10':  [76.873,100.0,0.0],
            '1000_150_100': [76.547,90.888,9.112],
            '1000_150_1000':[70.048,35.235,64.765],
            '1000_350_35':  [82.546,99.87,0.13],
            '1000_350_350': [82.255,68.09,31.91],
            '1000_350_3500':[70.417,20.4,79.6],
        },
        '4Mu': {
            '125_20_13':   [55.42,100.0,0.0],
            '125_20_130':  [55.773,95.972,4.028],
            '125_20_1300': [36.497,55.757,44.243],
            '125_50_50':   [60.87,99.804,0.196],
            '125_50_500':  [59.987,81.871,18.129],
            '125_50_5000': [35.117,31.286,68.714],
            '200_20_7':    [71.883,100.0,0.0],
            '200_20_70':   [71.373,98.761,1.239],
            '200_20_700':  [56.647,67.031,32.969],
            '200_50_20':   [76.117,100.0,0.0],
            '200_50_200':  [76.227,92.941,7.059],
            '200_50_2000': [57.79,42.229,57.771],
            '400_20_4':    [86.757,100.0,0.0],
            '400_20_40':   [87.123,99.786,0.214],
            '400_20_400':  [74.707,78.704,21.296],
            '400_50_8':    [89.033,100.0,0.0],
            '400_50_80':   [89.0,98.756,1.244],
            '400_50_800':  [79.91,61.88,38.12],
            '400_150_40':  [94.813,99.993,0.007],
            '400_150_400': [94.663,87.881,12.119],
            '400_150_4000':[79.92,32.611,67.389],
            '1000_20_2':   [94.217,100.0,0.0],
            '1000_20_20':  [94.12,99.989,0.011],
            '1000_20_200': [85.73,92.443,7.557],
            '1000_50_4':   [95.169,100.0,0.0],
            '1000_50_40':  [94.98,99.863,0.137],
            '1000_50_400': [89.633,79.48,20.52],
            '1000_150_10':  [98.659,100.0,0.0],
            '1000_150_100': [98.603,98.877,1.123],
            '1000_150_1000':[95.01,58.513,41.487],
            '1000_350_35':  [99.737,99.997,0.003],
            '1000_350_350': [99.771,90.775,9.225],
            '1000_350_3500':[93.165,35.031,64.969],
        }
    }

    SAMPLE_SPECS = {
        '2Mu2J': {
            '125_20_13':    {'fractions': FRACTIONS['2Mu2J']['125_20_13'], 'rebin': rbins2, 'xmax': xmax2},
            '125_20_130':   {'fractions': FRACTIONS['2Mu2J']['125_20_130'], 'rebin': rbins1, 'xmax': xmax1},
            '125_20_1300':  {'fractions': FRACTIONS['2Mu2J']['125_20_1300'], 'rebin': rbins1, 'xmax': xmax1},
            '125_50_50':    {'fractions': FRACTIONS['2Mu2J']['125_50_50'], 'rebin': rbins2, 'xmax': xmax2},
            '125_50_500':   {'fractions': FRACTIONS['2Mu2J']['125_50_500'], 'rebin': rbins1, 'xmax': xmax1},
            '125_50_5000':  {'fractions': FRACTIONS['2Mu2J']['125_50_5000'], 'rebin': rbins1, 'xmax': xmax1},
            '200_20_7':     {'fractions': FRACTIONS['2Mu2J']['200_20_7'], 'rebin': rbins2, 'xmax': xmax2},
            '200_20_70':    {'fractions': FRACTIONS['2Mu2J']['200_20_70'], 'rebin': rbins1, 'xmax': xmax1},
            '200_20_700':   {'fractions': FRACTIONS['2Mu2J']['200_20_700'], 'rebin': rbins1, 'xmax': xmax1},
            '200_50_20':    {'fractions': FRACTIONS['2Mu2J']['200_50_20'], 'rebin': rbins2, 'xmax': xmax2},
            '200_50_200':   {'fractions': FRACTIONS['2Mu2J']['200_50_200'], 'rebin': rbins1, 'xmax': xmax1},
            '200_50_2000':  {'fractions': FRACTIONS['2Mu2J']['200_50_2000'], 'rebin': rbins1, 'xmax': xmax1},
            '400_20_4':     {'fractions': FRACTIONS['2Mu2J']['400_20_4'], 'rebin': rbins2, 'xmax': xmax2},
            '400_20_40':    {'fractions': FRACTIONS['2Mu2J']['400_20_40'], 'rebin': rbins1, 'xmax': xmax1},
            '400_20_400':   {'fractions': FRACTIONS['2Mu2J']['400_20_400'], 'rebin': rbins1, 'xmax': xmax1},
            '400_50_8':     {'fractions': FRACTIONS['2Mu2J']['400_50_8'], 'rebin': rbins2, 'xmax': xmax2},
            '400_50_80':    {'fractions': FRACTIONS['2Mu2J']['400_50_80'], 'rebin': rbins1, 'xmax': xmax1},
            '400_50_800':   {'fractions': FRACTIONS['2Mu2J']['400_50_800'], 'rebin': rbins1, 'xmax': xmax1},
            '400_150_40':   {'fractions': FRACTIONS['2Mu2J']['400_150_40'], 'rebin': rbins2, 'xmax': xmax2},
            '400_150_400':  {'fractions': FRACTIONS['2Mu2J']['400_150_400'], 'rebin': rbins1, 'xmax': xmax1},
            '400_150_4000': {'fractions': FRACTIONS['2Mu2J']['400_150_4000'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_20_2':    {'fractions': FRACTIONS['2Mu2J']['1000_20_2'], 'rebin': rbins2, 'xmax': xmax2},
            '1000_20_20':   {'fractions': FRACTIONS['2Mu2J']['1000_20_20'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_20_200':  {'fractions': FRACTIONS['2Mu2J']['1000_20_200'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_50_4':    {'fractions': FRACTIONS['2Mu2J']['1000_50_4'], 'rebin': rbins2, 'xmax': xmax2},
            '1000_50_40':   {'fractions': FRACTIONS['2Mu2J']['1000_50_40'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_50_400':  {'fractions': FRACTIONS['2Mu2J']['1000_50_400'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_50_500':  {'fractions': FRACTIONS['2Mu2J']['1000_50_400'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_150_10':  {'fractions': FRACTIONS['2Mu2J']['1000_150_10'], 'rebin': rbins2, 'xmax': xmax2},
            '1000_150_100': {'fractions': FRACTIONS['2Mu2J']['1000_150_100'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_150_1000':{'fractions': FRACTIONS['2Mu2J']['1000_150_1000'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_350_35':  {'fractions': FRACTIONS['2Mu2J']['1000_350_35'], 'rebin': rbins2, 'xmax': xmax2},
            '1000_350_350': {'fractions': FRACTIONS['2Mu2J']['1000_350_350'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_350_3500':{'fractions': FRACTIONS['2Mu2J']['1000_350_3500'], 'rebin': rbins1, 'xmax': xmax1}
        },
        '4Mu': {
            '125_20_13':    {'fractions': FRACTIONS['4Mu']['125_20_13'], 'rebin': rbins2, 'xmax': xmax2},
            '125_20_130':   {'fractions': FRACTIONS['4Mu']['125_20_130'], 'rebin': rbins1, 'xmax': xmax1},
            '125_20_1300':  {'fractions': FRACTIONS['4Mu']['125_20_1300'], 'rebin': rbins1, 'xmax': xmax1},
            '125_50_50':    {'fractions': FRACTIONS['4Mu']['125_50_50'], 'rebin': rbins2, 'xmax': xmax2},
            '125_50_500':   {'fractions': FRACTIONS['4Mu']['125_50_500'], 'rebin': rbins1, 'xmax': xmax1},
            '125_50_5000':  {'fractions': FRACTIONS['4Mu']['125_50_5000'], 'rebin': rbins1, 'xmax': xmax1},
            '200_20_7':     {'fractions': FRACTIONS['4Mu']['200_20_7'], 'rebin': rbins2, 'xmax': xmax2},
            '200_20_70':    {'fractions': FRACTIONS['4Mu']['200_20_70'], 'rebin': rbins1, 'xmax': xmax1},
            '200_20_700':   {'fractions': FRACTIONS['4Mu']['200_20_700'], 'rebin': rbins1, 'xmax': xmax1},
            '200_50_20':    {'fractions': FRACTIONS['4Mu']['200_50_20'], 'rebin': rbins2, 'xmax': xmax2},
            '200_50_200':   {'fractions': FRACTIONS['4Mu']['200_50_200'], 'rebin': rbins1, 'xmax': xmax1},
            '200_50_2000':  {'fractions': FRACTIONS['4Mu']['200_50_2000'], 'rebin': rbins1, 'xmax': xmax1},
            '400_20_4':     {'fractions': FRACTIONS['4Mu']['400_20_4'], 'rebin': rbins2, 'xmax': xmax2},
            '400_20_40':    {'fractions': FRACTIONS['4Mu']['400_20_40'], 'rebin': rbins1, 'xmax': xmax1},
            '400_20_400':   {'fractions': FRACTIONS['4Mu']['400_20_400'], 'rebin': rbins1, 'xmax': xmax1},
            '400_50_8':     {'fractions': FRACTIONS['4Mu']['400_50_8'], 'rebin': rbins2, 'xmax': xmax2},
            '400_50_80':    {'fractions': FRACTIONS['4Mu']['400_50_80'], 'rebin': rbins1, 'xmax': xmax1},
            '400_50_800':   {'fractions': FRACTIONS['4Mu']['400_50_800'], 'rebin': rbins1, 'xmax': xmax1},
            '400_150_40':   {'fractions': FRACTIONS['4Mu']['400_150_40'], 'rebin': rbins2, 'xmax': xmax2},
            '400_150_400':  {'fractions': FRACTIONS['4Mu']['400_150_400'], 'rebin': rbins1, 'xmax': xmax1},
            '400_150_4000': {'fractions': FRACTIONS['4Mu']['400_150_4000'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_20_2':    {'fractions': FRACTIONS['4Mu']['1000_20_2'], 'rebin': rbins2, 'xmax': xmax2},
            '1000_20_20':   {'fractions': FRACTIONS['4Mu']['1000_20_20'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_20_200':  {'fractions': FRACTIONS['4Mu']['1000_20_200'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_50_4':    {'fractions': FRACTIONS['4Mu']['1000_50_4'], 'rebin': rbins2, 'xmax': xmax2},
            '1000_50_40':   {'fractions': FRACTIONS['4Mu']['1000_50_40'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_50_400':  {'fractions': FRACTIONS['4Mu']['1000_50_400'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_150_10':  {'fractions': FRACTIONS['4Mu']['1000_150_10'], 'rebin': rbins2, 'xmax': xmax2},
            '1000_150_100': {'fractions': FRACTIONS['4Mu']['1000_150_100'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_150_1000':{'fractions': FRACTIONS['4Mu']['1000_150_1000'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_350_35':  {'fractions': FRACTIONS['4Mu']['1000_350_35'], 'rebin': rbins2, 'xmax': xmax2},
            '1000_350_350': {'fractions': FRACTIONS['4Mu']['1000_350_350'], 'rebin': rbins1, 'xmax': xmax1},
            '1000_350_3500':{'fractions': FRACTIONS['4Mu']['1000_350_3500'], 'rebin': rbins1, 'xmax': xmax1}
        }
    }


    # make overlaid plots that combine all signal points
    def makeEffPlots(quantity, fs, SP=None):
        range_limits = {
                'pT': [0., 300.],
                'eta': None,
                'phi': None,
                'd0': None,
                'Lxy': [0., (500. if SP is None else \
                        SAMPLE_SPECS[fs]['{}_{}_{}'.format(*SP)]['xmax'])],
                'deltaR': None,
                'mass': None,
                'cosAlpha': None,
                'dimuonPTOverM': [0, 10],
                'XBeta': None,
        }

        HKeys = {
            'GEN_Eff'       : 'GEN_{}Num'      ,
            'GEN_Den'       : 'GEN_{}Den'      ,
            'DSA_Eff'       : 'DSA_{}Num'      ,
            'DSA_Den'       : 'DSA_{}Den'      ,
            'RSA_Eff'       : 'RSA_{}Num'      ,
            'RSA_Den'       : 'RSA_{}Den'      ,
        }
        for key in HKeys:
            HKeys[key] = HKeys[key].format(quantity, 'HTo2XTo'+fs)

        h = {}
        p = {}
        g = {}
        hm = {}

        if SP is None:
            for i, sp in enumerate(SIGNALPOINTS):
                if i == 0:
                    for key in HKeys:
                        h[key] = HISTS[(fs, sp)][HKeys[key]].Clone()
                        h[key].SetDirectory(0)
                else:
                    for key in HKeys:
                        h[key].Add(HISTS[(fs, sp)][HKeys[key]])

        else:
            sp = SP
            for key in HKeys:
                h[key] = HISTS[(fs, sp)][HKeys[key]].Clone()
                h[key].SetDirectory(0)

        for key in HKeys:
            RT.addFlows(h[key])
            nConcatBins = 20 if SP is None else \
                    SAMPLE_SPECS[fs]['{}_{}_{}'.format(*SP)]['rebin']
            h[key].Rebin(nConcatBins)
            # h[key].Rebin(30)

        NumDens = (
            ('GEN_Eff'      , 'GEN_Den'          , 'GEN'       , R.kGreen   ),
            ('DSA_Eff'      , 'DSA_Den'          , 'DSA'       , R.kBlue    ),
            ('RSA_Eff'      , 'RSA_Den'          , 'RSA'       , R.kRed     ),
        )

        for num, den, leg, col in NumDens:
            g[num] = R.TGraphAsymmErrors(h[num], h[den], 'cp')
            g[num].SetNameTitle('g_'+num, ';'+h[num].GetXaxis().GetTitle()+'; Trigger Efficiency')
            # g[num].GetXaxis().SetRangeUser(0., 30.)
            if range_limits[quantity] is not None:
                g[num].GetXaxis().SetLimits(
                        range_limits[quantity][0],
                        range_limits[quantity][1])

            p[num] = Plotter.Plot(g[num], leg, 'elp', 'pe')

            h[num].Sumw2()
            h[den].Sumw2()

            ratio_hist = R.TEfficiency(h[num], h[den])
            eff_sum_num = 0
            eff_sum_den = 0
            for binx in range(1,h[num].GetXaxis().GetNbins()+2):
                # if h[num].GetBinLowEdge(binx) > 250: continue
                glob_bin = ratio_hist.GetGlobalBin(binx)
                efferror = max(ratio_hist.GetEfficiencyErrorLow(glob_bin),
                        ratio_hist.GetEfficiencyErrorUp(glob_bin))
                if efferror != 0:
                    eff_sum_num += ratio_hist.GetEfficiency(glob_bin) / \
                            (efferror*efferror)
                    if ratio_hist.GetEfficiency(glob_bin) != 0:
                        eff_sum_den += 1/(efferror*efferror)
            if eff_sum_den != 0:
                hm[num] = eff_sum_num / eff_sum_den


        FIRST  = (0, 3)
        # SECOND = (3, 5)
        CHARGE = ''
        for SECTION in (FIRST,):
            fraction_str = '' if SP is None else '[{}%, {}%]'.format(
                    round(SAMPLE_SPECS[fs]['{}_{}_{}'.format(*SP)]['fractions'][0], 1),
                    round(SAMPLE_SPECS[fs]['{}_{}_{}'.format(*SP)]['fractions'][1], 1))
            canvas = Plotter.Canvas(lumi = fs if SP is None else \
                    '{} ({} GeV, {} GeV, {} mm) ' \
                    '#scale[0.7]{{{fraction_str}}}'.format(
                        fs, *SP, fraction_str=fraction_str))
            for i in range(SECTION[0], SECTION[1]):
                key = NumDens[i][0]
                col = NumDens[i][3]
                canvas.addMainPlot(p[key])
                p[key].SetMarkerColor(col)
                p[key].SetLineColor(col)

                # if quantity in ['Lxy','pT']:
                #     axis_min = p[key].GetXaxis().GetBinLowEdge(1)
                #     axis_max = p[key].GetXaxis().GetBinLowEdge(p[key].GetXaxis().GetNbins()+1)
                #     hline = R.TLine(axis_min, hm[key], range_limits[quantity][1], hm[key])
                #     R.SetOwnership(hline, 0)
                #     hline.SetLineColor(col)
                #     hline.Draw()
                

            canvas.makeLegend(pos='tr')
            canvas.legend.moveLegend(X=-0.18)
            canvas.legend.resizeHeight()
            canvas.firstPlot.SetMinimum(0.)
            canvas.firstPlot.SetMaximum(1.)
            RT.addBinWidth(canvas.firstPlot)
            if quantity == 'pT':
                vline = R.TLine(28.,0.,28.,1.)  # draw vertical line at 28 GeV
                R.SetOwnership(vline, 0)
                vline.SetLineColor(15)
                vline.Draw()

            canvas.cleanup(OUTPUT_PATH + FILENAME_OUT.format('STE', LXYMIN, LXYMAX, quantity, fs, 'Global' if SP is None else SPStr(SP)))


    def makeSimplePlots(quantity, fs, SP=None, normalize=False):
        range_limits = {
                'pT': [0., 300.],
                'eta': None,
                'phi': None,
                'd0': None,
                'Lxy': [0., (500. if SP is None else \
                        SAMPLE_SPECS[fs]['{}_{}_{}'.format(*SP)]['xmax'])],
                'deltaR': None,
                'mass': None,
                'cosAlpha': None,
                'dimuonPTOverM': [0, 10],
                'XBeta': None,
        }

        HKeys = {
            'GEN_Den' : 'GEN_{}Den',
            'DSA_Den' : 'DSA_{}Den',
            'RSA_Den' : 'RSA_{}Den',
        }
        for key in HKeys:
            HKeys[key] = HKeys[key].format(quantity, 'HTo2XTo'+fs)

        h = {}
        p = {}

        if SP is None:
            for i, sp in enumerate(SIGNALPOINTS):
                if i == 0:
                    for key in HKeys:
                        h[key] = HISTS[(fs, sp)][HKeys[key]].Clone()
                        h[key].Sumw2()
                        h[key].SetDirectory(0)
                else:
                    for key in HKeys:
                        h[key].Sumw2()
                        h[key].Add(HISTS[(fs, sp)][HKeys[key]])

        else:
            for key in HKeys:
                h[key] = HISTS[(fs, SP)][HKeys[key]].Clone()
                h[key].Sumw2()
                if normalize is True and h[key].Integral() != 0:
                    h[key].Scale(1/h[key].Integral())
                h[key].SetDirectory(0)

        for key in HKeys:
            RT.addFlows(h[key])
            nConcatBins = 20 if SP is None else \
                    SAMPLE_SPECS[fs]['{}_{}_{}'.format(*SP)]['rebin']
            h[key].Rebin(nConcatBins)
        
        if quantity == 'deltaR':
            ratio_cut = 0.5
            hist_ratios = {}
            for key in HKeys:
                num_before_cut = 0
                num_after_cut = 0
                for i in range(h[key].GetNbinsX()+1):
                    if h[key].GetXaxis().GetBinCenter(i) < ratio_cut:
                        num_before_cut += h[key].GetBinContent(i)
                    else:
                        num_after_cut += h[key].GetBinContent(i)

                if num_before_cut+num_after_cut != 0:
                    hist_ratios[key] = 1.0*num_before_cut/(num_before_cut+num_after_cut)
                else:
                    hist_ratios[key] = -1

        HistSpecs = (
            ('GEN_Den', 'GEN', R.kGreen, 'Yield [a.u.]'),
            ('DSA_Den', 'DSA', R.kBlue, 'Yield [a.u.]'),
            ('RSA_Den', 'RSA', R.kRed, 'Yield [a.u.]'),
        )

        for key, leg, col, yTitle in HistSpecs:
            if range_limits[quantity] is not None:
                h[key].GetXaxis().SetRangeUser(
                        range_limits[quantity][0],
                        range_limits[quantity][1])
            
            h[key].SetNameTitle('h_'+key,
                    ';'+h[key].GetXaxis().GetTitle() + '; ' + \
                    ('Normalized ' if normalize is True else '') + yTitle)
            # leg += (': yield(#Delta R<0.5) #times 100 / (total yield) = {}'.format(
            #     round(hist_ratios[key]*100,2)) if quantity == 'deltaR' else '')
            p[key] = Plotter.Plot(h[key], leg, '', 'hist e1 x0')
            
        FIRST = (0, 3)
        CHARGE = ''
        for SECTION in (FIRST,):
            fraction_str = '' if SP is None else '[{}%, {}%]'.format(
                    round(SAMPLE_SPECS[fs]['{}_{}_{}'.format(*SP)]['fractions'][0], 1),
                    round(SAMPLE_SPECS[fs]['{}_{}_{}'.format(*SP)]['fractions'][1], 1))

            canvas = Plotter.Canvas(lumi = fs if SP is None else \
                    '{} ({} GeV, {} GeV, {} mm) ' \
                    '#scale[0.7]{{{fraction_str}}}'.format(
                        fs, *SP, fraction_str=fraction_str))

            for i in range(SECTION[0], SECTION[1]):
                key = HistSpecs[i][0]
                col = HistSpecs[i][2]
                yTitle = HistSpecs[i][3]
                canvas.addMainPlot(p[key])
                p[key].SetMarkerColor(col)
                p[key].SetLineColor(col)
                # p[key].firstPlot.SetYTitle(yTitle)

            canvas.makeLegend(pos='tl')
            canvas.legend.moveLegend(X=0.15)
            canvas.legend.resizeHeight()
            RT.addBinWidth(canvas.firstPlot)

            canvas.cleanup(OUTPUT_PATH + FILENAME_OUT.format('STD', LXYMIN, LXYMAX, quantity, fs, 'Global' if SP is None else SPStr(SP)))


    for quantity in ('pT', 'eta', 'phi', 'd0', 'Lxy', 'deltaR', 'mass', 'cosAlpha', 'dimuonPTOverM', 'XBeta'):
        for fs in ('2Mu2J',):
            makeEffPlots(quantity, fs)
            makeSimplePlots(quantity, fs)
            for sp in SIGNALPOINTS:
                makeEffPlots(quantity, fs, sp)
                makeSimplePlots(quantity, fs, sp, normalize=False)
