import re
from copy import deepcopy
import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.RootTools as RT
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
from DisplacedDimuons.Common.Utilities import SPStr
import HistogramGetter

# get histograms
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/TriggerDimuonPlots_HTo2XTo4Mu.root')
# f = R.TFile.Open('../analyzers/roots/TriggerDimuonPlots_HTo2XTo4Mu.root')
HISTS = HistogramGetter.getHistograms('../analyzers/roots/test_TriggerDimuonPlots_simple_HTo2XTo2Mu2J.root')
f = R.TFile.Open('../analyzers/roots/test_TriggerDimuonPlots_simple_HTo2XTo2Mu2J.root')
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/test_GEN-HLT-MatchedNumerator_TriggerDimuonPlots_simple_HTo2XTo4Mu.root')
# f = R.TFile.Open('../analyzers/roots/test_GEN-HLT-MatchedNumerator_TriggerDimuonPlots_simple_HTo2XTo4Mu.root')
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/test_GEN-HLT-MatchedNumerator_TriggerDimuonPlots_simple_HTo2XTo2Mu2J.root')
# f = R.TFile.Open('../analyzers/roots/test_GEN-HLT-MatchedNumerator_TriggerDimuonPlots_simple_HTo2XTo2Mu2J.root')

output_tag = ''
if len(output_tag) > 0 and  output_tag[-1] != '_': output_tag += '_'

# limit histogram ranges
limit_low = 0.
limit_high = 3.5

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

DISPLACEMENT_CATEGORIES = {
        (0,15):   {'label': 'gt0',  'color': R.kGray+1},
        (15,30):  {'label': 'gt15', 'color': R.kBlack},
        (30,60):  {'label': 'gt30', 'color': R.kRed},
        (60,85):  {'label': 'gt60', 'color': R.kBlue},
        (85,95):  {'label': 'gt85', 'color': R.kOrange+1},
        (95,101): {'label': 'gt95', 'color': R.kGreen+1},
}


# make plots that are per sample
def makePerSamplePlots():
    for ref in HISTS:
        for key in HISTS[ref]:
            if type(ref) == tuple:
                if ref[0] == '4Mu':
                    name = 'HTo2XTo4Mu_'
                    latexFS = '4#mu'
                elif ref[0] == '2Mu2J':
                    name = 'HTo2XTo2Mu2J_'
                    latexFS = '2#mu2j'
                name += SPStr(ref[1])
                lumi = '{} ({} GeV, {} GeV, {} mm)'.format(ref[0], *ref[1])
                legName = HistogramGetter.PLOTCONFIG['HTo2XTo'+ref[0]]['LATEX']
            else:
                if '_Matched' in key: continue
                name = ref
                lumi = HistogramGetter.PLOTCONFIG[ref]['LATEX']
                legName = HistogramGetter.PLOTCONFIG[ref]['LATEX']

            h = HISTS[ref][key].Clone()
            if h.GetNbinsX() > 100: h.Rebin(10)
            RT.addFlows(h)
            p = Plotter.Plot(h, legName, 'l', 'hist')
            fname = 'pdfs/{}_{}{}.pdf'.format(key, output_tag, name)

            canvas = Plotter.Canvas(lumi=lumi)
            canvas.addMainPlot(p)
            canvas.makeLegend(lWidth=.25, pos='tr')
            canvas.legend.moveLegend(Y=-.3)
            canvas.legend.resizeHeight()
            p.SetLineColor(R.kBlue)
            RT.addBinWidth(p)

            pave = canvas.makeStatsBox(p, color=R.kBlue)
            canvas.cleanup(fname)


# make overlaid plots that combine all signal points
def makeEffPlots(quantity, fs, SP=None):
    HKeys = {
        'DSA_Num'       : 'DSADim_Num_{}'      ,
        'DSA_Den'       : 'DSADim_Den_{}'      ,
    }
    for key in HKeys:
        HKeys[key] = HKeys[key].format(quantity, 'HTo2XTo'+fs)

    h = {}
    pg = {}
    pnum = {}
    pden = {}
    prn = {}
    prd = {}
    g = {}
    rn = {}
    rd = {}

    if SP is None:
        for i, sp in enumerate(SIGNALPOINTS):
            if i == 0:
                for key in HKeys:
                    h[key] = HISTS[(fs, sp)][HKeys[key]].Clone()
                    h[key].SetDirectory(0)
            else:
                for key in HKeys:
                    h[key].Add(HISTS[(fs, sp)][HKeys[key]])

        displacement_str = None
        displacement_color = None
    else:
        sp = SP
        if isinstance(sp, tuple):
            for key in HKeys:
                h[key] = HISTS[(fs, sp)][HKeys[key]].Clone()
                h[key].SetDirectory(0)

                h[key].GetXaxis().SetLimits(limit_low, limit_high)
                h[key].GetXaxis().SetRangeUser(limit_low, limit_high)
                RT.addFlows(h[key])
                h[key].Rebin(10)
                h[key].Sumw2()
        elif isinstance(sp, list):
            h[key] = {}
            for key in HKeys:
                for spl in sp:
                    h[key][spl] = HISTS[(fs, spl)][HKeys[key]].Clone()
                    h[key][spl].SetDirectory(0)
                    h[key][spl].GetXaxis().SetLimits(limit_low, limit_high)
                    RT.addFlows(h[key][spl])
                    h[key][spl].Rebin(10)
                    h[key][spl].Sumw2()

        dxy_fraction = round(FRACTIONS[fs]['{}_{}_{}'.format(*SP)][1], 1) 
        for key in DISPLACEMENT_CATEGORIES:
            if key[0] <= dxy_fraction < key[1]:
                displacement_str = DISPLACEMENT_CATEGORIES[key]['label']
                displacement_color = DISPLACEMENT_CATEGORIES[key]['color']
                break
        else:
            # we must have dxy_fractions == 100.0
            key = DISPLACEMENT_CATEGORIES.keys()[-1]
            displacement_str = DISPLACEMENT_CATEGORIES[key]['label']
            displacement_color = DISPLACEMENT_CATEGORIES[key]['color']


#     for key in HKeys:
#         RT.addFlows(h[key])
#         h[key].Rebin(10)
#         # area = h[key].Integral()
#         h[key].Sumw2()
#         # if area != 0: h[key].Scale(1./area)

    NumDens = (
        ('DSA_Num'      , 'DSA_Den'          , 'GEN'       , R.kBlue),
        ('DSA_Num'      , 'DSA_Den'          , ('untriggered','triggered'), (R.kBlue, R.kRed)),
    )

    num, den, leg, col = NumDens[0]
    g[num] = R.TGraphAsymmErrors(h[num], h[den], 'cp')
    g[num].GetXaxis().SetLimits(limit_low, limit_high)
    g[num].SetNameTitle('g_'+num, ';'+h[num].GetXaxis().GetTitle()+'; Trigger Efficiency')
    pg[num] = Plotter.Plot(g[num], leg, 'elp', 'pe')

    num, den, leg, col = NumDens[1]
    pnum[num] = Plotter.Plot(deepcopy(h[num]), leg[1], 'elp', 'pe')
    pden[num] = Plotter.Plot(deepcopy(h[den]), leg[0], 'elp', 'pe')
    pnum[num].SetNameTitle('pnum_'+num, ';'+h[num].GetXaxis().GetTitle()+'; yield')
    rn[num] = deepcopy(h[num])
    rn[num].Scale(1./(h[num].Integral()))
    rn[num].SetNameTitle('rn_'+num, ';'+h[num].GetXaxis().GetTitle()+'; norm. yield')
    # rn[num].GetXaxis().SetRangeUser(0, 100)
    prn[num] = Plotter.Plot(rn[num], leg[1], 'elp', 'pe')
    rd[num] = deepcopy(h[den])
    rd[num].Scale(1./(h[den].Integral()))
    rd[num].SetNameTitle('rd_'+num, ';'+h[num].GetXaxis().GetTitle()+'; norm. yield')
    prd[num] = Plotter.Plot(rd[num], leg[0], 'elp', 'pe')


    FIRST  = (0, 1)
    SECOND = (1, 2)

    fraction_str = '' if SP is None else '[{}%, #color[{}]{{{}%}}]'.format(
            round(FRACTIONS[fs]['{}_{}_{}'.format(*SP)][0], 1),
            displacement_color,
            round(FRACTIONS[fs]['{}_{}_{}'.format(*SP)][1], 1))

    accepted_error_max = 0.1
    accepted_error_halfmax = 0.2

    for SECTION in (FIRST,):
        canvas_eff = Plotter.Canvas(lumi = fs if SP is None else '{} ({} GeV, {} GeV, {} mm) #scale[0.7]{{{fraction_str}}}'.format(fs, *SP,
                    fraction_str=fraction_str))
        for i in range(SECTION[0], SECTION[1]):
            key = NumDens[i][0]
            col = NumDens[i][3]
            # pg[key].GetXaxis().SetLimits(0., 3.5)
            canvas_eff.addMainPlot(pg[key])
            pg[key].SetMarkerColor(col)
            pg[key].SetLineColor(col)
            ymax = -1. 
            ymaxErrorYlow = 0.
            ymaxErrorYhigh = 0.
            ymax_pos = None
            for b in range(pg[key].GetN(), 0, -1):
                xtemp = R.Double(-1.)
                ytemp = R.Double(-1.)
                pg[key].GetPoint(b, xtemp, ytemp)
                ytempErrorYlow = pg[key].GetErrorYlow(b)
                ytempErrorYhigh = pg[key].GetErrorYhigh(b)
                # if ytemp > ymax and max(pg[key].GetErrorYlow(b),
                #         pg[key].GetErrorYhigh(b)) < accepted_error_max:
                #     ymax = ytemp
                #     ymax_pos = xtemp

                # if point has a lower value than the one one the right, but it
                # is compatible with the fluctuations of the plot on the right
                # (i.e., its errors are contained in the errors of the other
                # plot), then call the (left) point the new maximum nevertheless
                if ytemp < ymax and max(ytempErrorYlow,
                        ytempErrorYhigh) < accepted_error_max and \
                                ytemp-ytempErrorYlow > ymax-ymaxErrorYlow and \
                                ytemp+ytempErrorYhigh < ymax+ymaxErrorYhigh:
                    ymax = ytemp
                    ymaxErrorYlow = ytempErrorYlow
                    ymaxErrorYhigh = ytempErrorYhigh
                    ymax_pos = xtemp
                
                elif ytemp > ymax and max(ytempErrorYlow,
                        ytempErrorYhigh) < accepted_error_max:
                    ymax = ytemp
                    ymaxErrorYlow = ytempErrorYlow
                    ymaxErrorYhigh = ytempErrorYhigh
                    ymax_pos = xtemp

            if ymax_pos is not None:
                maxarrow = R.TArrow(ymax_pos, -0.065, ymax_pos, 0.)
                R.SetOwnership(maxarrow, 0)
                maxarrow.SetLineColor(col)
                maxarrow.SetLineWidth(3)
                maxarrow.SetArrowSize(0.02)
                maxarrow.Draw()
            else:
                print('WARNING: No maximum found. Maybe the accepted errors '
                        'are too small?')
                ymax_pos = None
                yhalfmax_pos = None

            if ymax_pos is not None:
                yhalfmax = 0.5*ymax
                yhalfmax_pos = None
                for b in range(pg[key].GetN()):
                    xtemp = R.Double(-1.)
                    ytemp = R.Double(-1.)
                    pg[key].GetPoint(b, xtemp, ytemp)
                    if ytemp > yhalfmax and max(pg[key].GetErrorYlow(b),
                            pg[key].GetErrorYhigh(b)) < accepted_error_halfmax:
                        x2 = xtemp
                        y2 = ytemp
                        xtemp_prev = R.Double(0.)
                        ytemp_prev = R.Double(0.)
                        for bprev in range(1, b+1):
                            if b-bprev >= 0 and max(pg[key].GetErrorYlow(b-bprev),
                                    pg[key].GetErrorYhigh(b-bprev)) < accepted_error_halfmax:
                                pg[key].GetPoint(b-bprev, xtemp_prev, ytemp_prev)
                                x1 = xtemp_prev
                                y1 = ytemp_prev
                                # linear interpolation:
                                yhalfmax_pos = (yhalfmax*(x1-x2)+(y1*x2-y2*x1))/(y1-y2)
                                break
                        else:
                            yhalfmax_pos = x2*0.5

                        halfmaxarrow = R.TArrow(yhalfmax_pos, -0.06, yhalfmax_pos, 0.)
                        R.SetOwnership(halfmaxarrow, 0)
                        halfmaxarrow.SetLineColor(col)
                        halfmaxarrow.SetLineWidth(2)
                        halfmaxarrow.SetArrowSize(0.02)
                        halfmaxarrow.Draw()
                        break

        if ymax_pos is not None and yhalfmax_pos is not None:
            pg[key].legName = pg[key].legName + \
                    ' #scale[0.7]{{(#Delta R_{{max}} = {}, #Delta R_{{max/2}} = {}, #frac{{#Delta R_{{max/2}}}}{{#Delta R_{{max}}}} = {})}}'.format(
                        round(ymax_pos,3), round(yhalfmax_pos,3),
                        round(yhalfmax_pos/ymax_pos, 3))

        run1_line = R.TLine(0.2, 0., 0.2, 1.)
        R.SetOwnership(run1_line, 0)
        run1_line.SetLineColor(R.kGray)
        run1_line.Draw()

        canvas_eff.makeLegend(lWidth=0.65, pos='tr')
        # canvas_eff.legend.moveLegend(X=0.08)
        canvas_eff.legend.resizeHeight()
        # canvas_eff.firstPlot.GetXaxis().SetLimits(0., 3.5)
        canvas_eff.firstPlot.SetMinimum(0.)
        canvas_eff.firstPlot.SetMaximum(1.)
        RT.addBinWidth(canvas_eff.firstPlot)

        canvas_eff.cleanup('pdfs/DimSTE_{}{}Eff_HTo2XTo{}_{}_{}.pdf'.format(output_tag,
            quantity, fs, 'Global' if SP is None else SPStr(SP),
            (displacement_str if displacement_str is not None else '')))

    for SECTION in (SECOND,):
        canvas_ratioplot = Plotter.Canvas(ratioFactor=1/3., lumi = fs if SP is
                None else '{} ({} GeV, {} GeV, {} mm) #scale[0.7]{{{fraction_str}}}'.format(fs, *SP,
                    fraction_str=fraction_str))
        for i in range(SECTION[0], SECTION[1]):
            key = NumDens[i][0]
            col = NumDens[i][3]
            # prn[key].GetXaxis().SetLimits(0., 3.5)
            # prd[key].GetXaxis().SetLimits(0., 3.5)
            canvas_ratioplot.makeLegend(lWidth=.35, pos='tr')
            canvas_ratioplot.addLegendEntry(prn[key])
            canvas_ratioplot.addLegendEntry(prd[key])
            canvas_ratioplot.legend.resizeHeight()
            canvas_ratioplot.addMainPlot(prn[key])
            canvas_ratioplot.addMainPlot(prd[key])
            canvas_ratioplot.makeRatioPlot(prn[key], prd[key], ytit='triggered / untriggered')
            canvas_ratioplot.firstPlot.scaleTitleOffsets(0.8, axes='Y')
            canvas_ratioplot.rat.scaleTitleOffsets(0.8, axes='Y')
            vline = R.TLine(2.5, 0.5, 2.5, 1.5)
            R.SetOwnership(vline, 0)
            vline.SetLineColor(15)
            vline.Draw()
            prn[key].SetMarkerColor(col[0])
            prn[key].SetLineColor(col[0])
            prd[key].SetMarkerColor(col[1])
            prd[key].SetLineColor(col[1])
        # canvas_ratioplot.makeLegend(pos='tr')
        # canvas_ratioplot.legend.moveLegend(X=0.08)
        # canvas_ratioplot.legend.resizeHeight()
        # canvas_ratioplot.firstPlot.SetMinimum(0.)
        # canvas_ratioplot.firstPlot.SetMaximum(1.)
        # vline = R.TLine(0., 1., 5., 1.)
        # R.SetOwnership(vline, 0)
        # vline.SetLineColor(15)
        # vline.Draw()
        # RT.addBinWidth(canvas_ratioplot.firstPlot)
        # canvas_ratioplot.finishCanvas(extrascale=1.+1/3.)
        canvas_ratioplot.cleanup('pdfs/DimSTE_{}{}NormRatio_HTo2XTo{}_{}_{}.pdf'.format(output_tag,
            quantity, fs, 'Global' if SP is None else SPStr(SP),
            (displacement_str if displacement_str is not None else '')))

        canvas_overlay = Plotter.Canvas(lumi = fs if SP is None else '{} ({} GeV, {} GeV, {} mm) #scale[0.7]{{{fraction_str}}}'.format(fs,
                    *SP, fraction_str=fraction_str))
        for i in range(SECTION[0], SECTION[1]):
            key = NumDens[i][0]
            col = NumDens[i][3]
            canvas_overlay.addMainPlot(pden[num])
            canvas_overlay.addMainPlot(pnum[num])
            canvas_overlay.makeLegend(pos='tr', lWidth=.2)
            canvas_overlay.legend.resizeHeight()
            # canvas_overlay.firstPlot.GetXaxis().SetLimits(0., 3.5)
            pnum[num].SetMarkerColor(col[0])
            pden[num].SetMarkerColor(col[1])
            pnum[num].SetLineColor(col[0])
            pden[num].SetLineColor(col[1])
        canvas_overlay.cleanup('pdfs/DimSTE_{}Overlay{}_{}_{}.pdf'.format(quantity,
            fs, 'Global' if SP is None else SPStr(SP),
            (displacement_str if displacement_str is not None else '')))


makePerSamplePlots()

for quantity in ('deltaR',):
    for fs in ('2Mu2J',):
        makeEffPlots(quantity, fs)
        for sp in SIGNALPOINTS:
            makeEffPlots(quantity, fs, sp)

