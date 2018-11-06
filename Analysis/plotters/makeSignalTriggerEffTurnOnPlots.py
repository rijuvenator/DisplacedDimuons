import re
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import HistogramGetter

# get histograms
HISTS = HistogramGetter.getHistograms('../analyzers/roots/2Mu2J_turnon/SignalTriggerEffTurnOnPlots_HTo2XTo2Mu2J.root')
f = R.TFile.Open('../analyzers/roots/2Mu2J_turnon/SignalTriggerEffTurnOnPlots_HTo2XTo2Mu2J.root')
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/4Mu_turnon/SignalTriggerEffTurnOnPlots_HTo2XTo4Mu.root')
# f = R.TFile.Open('../analyzers/roots/4Mu_turnon/SignalTriggerEffTurnOnPlots_HTo2XTo4Mu.root')

# redefinition of SIGNIALPOINTS to exclude some very boosted samples which have
# a considerable fraction of multiple matches
SIGNALPOINTS = [
    (1000, 350,   35),
	(1000, 350,  350),
	(1000, 350, 3500),
	(1000, 150,   10),
	(1000, 150,  100),
	(1000, 150, 1000),
	# (1000,  50,    4),
	# (1000,  50,   40),
	# (1000,  50,  400),
	# (1000,  20,    2),
	# (1000,  20,   20),
	# (1000,  20,  200),
	( 400, 150,   40),
	( 400, 150,  400),
	( 400, 150, 4000),
	( 400,  50,    8),
	( 400,  50,   80),
	( 400,  50,  800),
	# ( 400,  20,    4),
	# ( 400,  20,   40),
	# ( 400,  20,  400),
	( 200,  50,   20),
	( 200,  50,  200),
	( 200,  50, 2000),
	( 200,  20,    7),
	( 200,  20,   70),
	( 200,  20,  700),
	( 125,  50,   50),
	( 125,  50,  500),
	( 125,  50, 5000),
	( 125,  20,   13),
	( 125,  20,  130),
	( 125,  20, 1300),
]

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



# make overlaid plots that combine all signal points
def makeEffPlots(quantity, fs, SP=None):
    HKeys = {
        'GEN_Eff'       : 'GEN_{}Eff'      ,
        'GEN_Den'       : 'GEN_{}Den'      ,
        'DSA_Eff'       : 'DSA_{}Eff'      ,
        'DSA_Den'       : 'DSA_{}Den'      ,
        'RSA_Eff'       : 'RSA_{}Eff'      ,
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
        h[key].Rebin(10)

    NumDens = (
        ('GEN_Eff'      , 'GEN_Den'          , 'GEN'       , R.kGreen   ),
        ('DSA_Eff'      , 'DSA_Den'          , 'DSA'       , R.kBlue    ),
        ('RSA_Eff'      , 'RSA_Den'          , 'RSA'       , R.kRed     ),
    )

    for num, den, leg, col in NumDens:
        g[num] = R.TGraphAsymmErrors(h[num], h[den], 'cp')
        g[num].SetNameTitle('g_'+num, ';'+h[num].GetXaxis().GetTitle()+'; Trigger Efficiency')
        g[num].GetXaxis().SetRangeUser(0, 100)
        p[num] = Plotter.Plot(g[num], leg, 'elp', 'pe')

        h[num].Sumw2()
        h[den].Sumw2()

#         # ratio_hist = h[num]
#         # ratio_hist.Divide(h[den])
#         # eff_sum_num = 0
#         # eff_sum_den = 0
#         # if quantity == 'pT':
#         #     for binx in range(1, h[num].GetXaxis().GetNbins()+1):
#         #         if h[num].GetBinLowEdge(binx) < 30.: continue
#         #         efferror = ratio_hist.GetBinError(binx)
#         #         if efferror != 0:
#         #             eff_sum_num += ratio_hist.GetBinContent(binx) / \
#         #                     (efferror*efferror)
#         #             if ratio_hist.GetBinContent(binx) != 0:
#         #                 eff_sum_den += 1/(efferror*efferror)
#         #     if eff_sum_den != 0:
#         #         hm[num] = eff_sum_num / eff_sum_den

#         ratio_hist = R.TEfficiency(h[num], h[den])
#         eff_sum_num = 0
#         eff_sum_den = 0
#         if quantity == 'pT':
#             for binx in range(1, h[num].GetXaxis().GetNbins()+2):
#                 if h[num].GetBinLowEdge(binx) < 30.: continue
#                 glob_bin = ratio_hist.GetGlobalBin(binx)
#                 efferror = max(ratio_hist.GetEfficiencyErrorLow(glob_bin),
#                         ratio_hist.GetEfficiencyErrorUp(glob_bin))
#                 if efferror != 0:
#                     eff_sum_num += ratio_hist.GetEfficiency(glob_bin) / \
#                             (efferror*efferror)
#                     if ratio_hist.GetEfficiency(glob_bin) != 0:
#                         eff_sum_den += 1/(efferror*efferror)
#             if eff_sum_den != 0:
#                 hm[num] = eff_sum_num / eff_sum_den

    FIRST  = (0, 3)
    # SECOND = (3, 5)
    CHARGE = ''
    for SECTION in (FIRST,):
        fraction_str = '' if SP is None else '[{}%, {}%]'.format(
                round(FRACTIONS[fs]['{}_{}_{}'.format(*SP)][0], 1),
                round(FRACTIONS[fs]['{}_{}_{}'.format(*SP)][1], 1))
        canvas = Plotter.Canvas(lumi = fs if SP is None else '{} ({} GeV, {} GeV, {} mm) #scale[0.7]{{{fraction_str}}}'.format(
            fs, *SP, fraction_str=fraction_str))
        for i in range(SECTION[0], SECTION[1]):
            key = NumDens[i][0]
            col = NumDens[i][3]
            canvas.addMainPlot(p[key])
            p[key].SetMarkerColor(col)
            p[key].SetLineColor(col)

            if quantity == 'pT':
                axis_max = p[NumDens[SECTION[0]][0]].GetXaxis().GetBinLowEdge(p[NumDens[SECTION[0]][0]].GetXaxis().GetNbins())
                hline = R.TLine(30., hm[key], axis_max, hm[key])
                R.SetOwnership(hline, 0)
                hline.SetLineColor(col)
                hline.Draw()

        canvas.makeLegend(pos='tl')
        # canvas.legend.moveLegend(X=0.08)
        canvas.legend.resizeHeight()
        canvas.firstPlot.SetMinimum(0.)
        canvas.firstPlot.SetMaximum(1.)
        RT.addBinWidth(canvas.firstPlot)
        if quantity == 'pT':
            vline = R.TLine(28.,0.,28.,1.)  # draw vertical line at 28 GeV
            vline.SetLineColor(15)
            vline.Draw()


        canvas.cleanup('pdfs/STETurnOn_zoomed_{}{}Eff_HTo2XTo{}_{}.pdf'.format(quantity, CHARGE, fs, 'Global' if SP is None else SPStr(SP)))
        CHARGE = 'Charge'

for quantity in ('pT', 'eta', 'phi', 'd0', 'Lxy'):
    for fs in ('2Mu2J',):
        makeEffPlots(quantity, fs)
        for sp in SIGNALPOINTS:
            makeEffPlots(quantity, fs, sp)

