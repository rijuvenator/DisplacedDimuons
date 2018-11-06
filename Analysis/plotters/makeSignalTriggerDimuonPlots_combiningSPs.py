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
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/test_TriggerDimuonPlots_simple_HTo2XTo2Mu2J.root')
# f = R.TFile.Open('../analyzers/roots/test_TriggerDimuonPlots_simple_HTo2XTo2Mu2J.root')
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/test_GEN-HLT-MatchedNumerator_TriggerDimuonPlots_simple_HTo2XTo4Mu.root')
# f = R.TFile.Open('../analyzers/roots/test_GEN-HLT-MatchedNumerator_TriggerDimuonPlots_simple_HTo2XTo4Mu.root')
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/test_GEN-HLT-MatchedNumerator_TriggerDimuonPlots_simple_HTo2XTo2Mu2J.root')
# f = R.TFile.Open('../analyzers/roots/test_GEN-HLT-MatchedNumerator_TriggerDimuonPlots_simple_HTo2XTo2Mu2J.root')
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/TriggerDimuonPlots_pTGT30_etaLT2.0_simple_HTo2XTo2Mu2J.root')
# f = R.TFile.Open('../analyzers/roots/TriggerDimuonPlots_pTGT30_etaLT2.0_simple_HTo2XTo2Mu2J.root')
# HISTS = HistogramGetter.getHistograms('../analyzers/roots/TriggerDimuonPlots_pTGT30_etaLT2.0_massGT15_cosAlphaGT-0.8_simple_HTo2XTo2Mu2J.root')
# f = R.TFile.Open('../analyzers/roots/TriggerDimuonPlots_pTGT30_etaLT2.0_massGT15_cosAlphaGT-0.8_simple_HTo2XTo2Mu2J.root')
HISTS = HistogramGetter.getHistograms('../analyzers/roots/test_GEN-HLT-MatchedNumerator-dRMatching0.03_TriggerDimuonPlots_simple_HTo2XTo2Mu2J.root')
f = R.TFile.Open('../analyzers/roots/test_GEN-HLT-MatchedNumerator-dRMatching0.03_TriggerDimuonPlots_simple_HTo2XTo2Mu2J.root')

output_tag = 'GEN-HLTMatchedNum'
if len(output_tag) > 0 and output_tag[-1] != '_': output_tag += '_'

# maximally accepted errors size when searching for the distribution maximum etc
accepted_error_max = 0.1
accepted_error_halfmax = 0.2


FRACTIONS = {
    '2Mu2J': {
        (125,20,13):   [13.67,100.0,0.0],
        (125,20,130):  [14.01,76.507,23.494],
        (125,20,1300): [9.353,28.205,71.795],
        (125,50,50):   [14.66,97.892,2.108],
        (125,50,500):  [14.943,39.505,60.495],
        (125,50,5000): [9.403,8.691,91.309],
        (200,20,7):    [31.937,100.0,0.0],
        (200,20,70):   [31.724,92.867,7.133],
        (200,20,700):  [25.317,40.277,59.723],
        (200,50,20):   [31.276,99.961,0.039],
        (200,50,200):  [31.04,66.832,33.168],
        (200,50,2000): [24.467,17.62,82.38],
        (400,20,4):    [56.88,100.0,0.0],
        (400,20,40):   [57.053,98.778,1.222],
        (400,20,400):  [45.9,60.654,39.346],
        (400,50,8):    [55.477,100.0,0.0],
        (400,50,80):   [55.829,92.292,7.708],
        (400,50,800):  [48.343,36.877,63.123],
        (400,150,40):  [67.093,99.796,0.204],
        (400,150,400): [67.053,64.513,35.487],
        (400,150,4000):[54.71,18.61,81.39],
        (1000,20,2):   [75.869,100.0,0.0],
        (1000,20,20):  [75.47,99.961,0.039],
        (1000,20,200): [60.067,84.403,15.597],
        (1000,50,4):   [74.837,100.0,0.0],
        (1000,50,40):  [74.468,98.914,1.086],
        (1000,50,400): [63.82,60.791,39.209],
        (1000,150,10):  [76.873,100.0,0.0],
        (1000,150,100): [76.547,90.888,9.112],
        (1000,150,1000):[70.048,35.235,64.765],
        (1000,350,35):  [82.546,99.87,0.13],
        (1000,350,350): [82.255,68.09,31.91],
        (1000,350,3500):[70.417,20.4,79.6],
    },
    '4Mu': {
        (125,20,13):   [55.42,100.0,0.0],
        (125,20,130):  [55.773,95.972,4.028],
        (125,20,1300): [36.497,55.757,44.243],
        (125,50,50):   [60.87,99.804,0.196],
        (125,50,500):  [59.987,81.871,18.129],
        (125,50,5000): [35.117,31.286,68.714],
        (200,20,7):    [71.883,100.0,0.0],
        (200,20,70):   [71.373,98.761,1.239],
        (200,20,700):  [56.647,67.031,32.969],
        (200,50,20):   [76.117,100.0,0.0],
        (200,50,200):  [76.227,92.941,7.059],
        (200,50,2000): [57.79,42.229,57.771],
        (400,20,4):    [86.757,100.0,0.0],
        (400,20,40):   [87.123,99.786,0.214],
        (400,20,400):  [74.707,78.704,21.296],
        (400,50,8):    [89.033,100.0,0.0],
        (400,50,80):   [89.0,98.756,1.244],
        (400,50,800):  [79.91,61.88,38.12],
        (400,150,40):  [94.813,99.993,0.007],
        (400,150,400): [94.663,87.881,12.119],
        (400,150,4000):[79.92,32.611,67.389],
        (1000,20,2):   [94.217,100.0,0.0],
        (1000,20,20):  [94.12,99.989,0.011],
        (1000,20,200): [85.73,92.443,7.557],
        (1000,50,4):   [95.169,100.0,0.0],
        (1000,50,40):  [94.98,99.863,0.137],
        (1000,50,400): [89.633,79.48,20.52],
        (1000,150,10):  [98.659,100.0,0.0],
        (1000,150,100): [98.603,98.877,1.123],
        (1000,150,1000):[95.01,58.513,41.487],
        (1000,350,35):  [99.737,99.997,0.003],
        (1000,350,350): [99.771,90.775,9.225],
        (1000,350,3500):[93.165,35.031,64.969],
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


def makeEffPlots(quantity, fs, SPlist=None, SPcombiName=None, **options):
    xTitle = options.pop('xTitle', '')
    yTitle = options.pop('yTitle', 'Trigger Efficiency')
    legTitle = options.pop('legTitle', None)
    padXmin = options.pop('padXmin', None)
    padXmax = options.pop('padXmax', None)
    padYmin = options.pop('padYmin', 0.)
    padYmax = options.pop('padYmax', 1.)
    add_hists = options.pop('add_hists', False)
    if options:
        raise TypeError('Invalid option(s): {}'.format(options))
    if ([True if val is not None else False for val in [padXmin,padXmax]]).count(True) == 1:
        raise RuntimeError('padXmin, padXmax: If one is specified, the other needs to be specified as well.')


    palette = Plotter.ColorPalette()

    HKeys = {
        'GEN_Num'       : 'DSADim_Num_{}'      ,
        'GEN_Den'       : 'DSADim_Den_{}'      ,
    }
    for key in HKeys:
        HKeys[key] = HKeys[key].format(quantity, 'HTo2XTo'+fs)

    h = {}
    g = {}
    pg = {}
    displacement_str = {}
    displacement_color = {}

    if add_hists is True:
        for iSP, SP in enumerate(SPlist):
            if iSP == 0:
                for key in HKeys:
                    h[key] = HISTS[(fs, SP)][HKeys[key]].Clone()
                    h[key].SetDirectory(0)
                    h[key].SetXTitle(xTitle)
                    h[key].SetYTitle(yTitle)
            else:
                for key in HKeys:
                    h[key].Add(HISTS[(fs, SP)][HKeys[key]])

        for key in HKeys:
            if padXmin is not None and padYmin is not None:
                h[key].GetXaxis().SetRangeUser(padXmin, padXmax)
            RT.addFlows(h[key])
            h[key].Rebin(5)
            # h[key].Rebin(20)
            h[key].Sumw2()

    else:
        for SP in SPlist:
            h[SP] = {}
            g[SP] = {}
            for key in HKeys:
                h[SP][key] = HISTS[(fs, SP)][HKeys[key]].Clone()
                h[SP][key].SetDirectory(0)
                h[SP][key].SetXTitle(xTitle)
                h[SP][key].SetYTitle(yTitle)
                if padXmin is not None and padXmax is not None:
                    h[SP][key].GetXaxis().SetRangeUser(padXmin, padXmax)
                RT.addFlows(h[SP][key])
                # h[SP][key].Rebin(20)
                h[SP][key].Rebin(5)
                h[SP][key].Sumw2()

            displacement_str[SP] = {}
            displacement_color[SP] = {}
            dxy_fraction = FRACTIONS[fs][SP][1]
            for key in DISPLACEMENT_CATEGORIES:
                if key[0] <= dxy_fraction < key[1]:
                    displacement_str[SP] = DISPLACEMENT_CATEGORIES[key]['label']
                    displacement_color[SP] = DISPLACEMENT_CATEGORIES[key]['color']
                    break
            else:
                # we must have dxy_fraction == 100.0
                key = DISPLACEMENT_CATEGORIES.keys()[-1]
                displacement_str[SP] = DISPLACEMENT_CATEGORIES[key]['label']
                displacement_color[SP] = DISPLACEMENT_CATEGORIES[key]['color']


    NumDens = (
        ('GEN_Num', 'GEN_Den'),
    )
    
    for num, den in NumDens:
        if add_hists is True:
            g[num] = R.TGraphAsymmErrors(h[num], h[den], 'cp')
            if padXmin is not None and padXmax is not None:
                g[num].GetXaxis().SetLimits(padXmin, padXmax)
            g[num].SetNameTitle('g_'+num,
                    ';'  + h[num].GetXaxis().GetTitle() + '; Trigger Efficiency')
            pg[num] = Plotter.Plot(g[num], legType='elp', option='pe')
            pg[num].setTitles(X=xTitle, Y=yTitle)
        else:
            for SP in SPlist:
                g[SP][num] = R.TGraphAsymmErrors(h[SP][num], h[SP][den], 'cp')
                if padXmin is not None and padXmax is not None:
                    g[SP][num].GetXaxis().SetLimits(padXmin, padXmax)
                g[SP][num].SetNameTitle('g_'+num,
                        ';' + h[SP][num].GetXaxis().GetTitle() + '; Trigger Efficiency')
                pg[SP] = {}
                pg[SP][num] = Plotter.Plot(g[SP][num], legType='elp', option='pe')
                pg[SP][num].setTitles(X=xTitle, Y=yTitle)

    lumi_str = '{}'
    canvas_eff = Plotter.Canvas(
            lumi = fs if SPlist is None else lumi_str.format(fs))

    for effDistr in NumDens:
        key = effDistr[0]

        if add_hists is True:
            canvas_eff.addMainPlot(pg[key])
            pg[key].SetMarkerColor(R.kBlue)
            pg[key].SetLineColor(R.kBlue)

            if quantity == 'deltaR':
                run1_line = R.TLine(0.2, padYmin, 0.2, padYmax)
                R.SetOwnership(run1_line, 0)
                run1_line.SetLineColor(R.kGray)
                run1_line.SetLineStyle(2)
                run1_line.Draw()

            if quantity == 'cosAlpha':
                HLTcut_line = R.TLine(-0.8, padYmin, -0.8, padYmax)
                R.SetOwnership(HLTcut_line, 0)
                HLTcut_line.SetLineColor(R.kGray)
                HLTcut_line.SetLineStyle(2)
                HLTcut_line.Draw()

            if legTitle is None:
                pass
            else:
                pg[key].legName = legTitle

            canvas_eff.makeLegend(lWidth=0.55, pos='tl')
            canvas_eff.legend.SetTextSize(.03)
            canvas_eff.legend.resizeHeight()
            canvas_eff.firstPlot.SetMinimum(padYmin)
            canvas_eff.firstPlot.SetMaximum(padYmax)
            RT.addBinWidth(canvas_eff.firstPlot)

            if SPlist is not None and len(SPlist) > 1:
                SPdescr = SPcombiName if SPcombiName is not None else ''
            else:
                SPdescr = ''

            outputfilename = u'DimSTE_{}{}Eff_HTo2XTo{}_{}_combinedSPs'.format(
                    output_tag, quantity, fs, SPdescr)
            outputfilename = 'pdfs/' + slugify(outputfilename) + '.pdf'

            canvas_eff.cleanup(outputfilename)

        else:
            for SP in SPlist:
                canvas_eff.addMainPlot(pg[SP][key])
                col = palette.getNextColor()
                pg[SP][key].SetMarkerColor(col)
                pg[SP][key].SetLineColor(col)

                ymax_pos = None
                yhalfmax_pos = None
                if quantity == 'deltaR':
                    # find the positions of max and max/2
                    ymax = -1.
                    ymaxErrorYLow = 0.
                    ymaxErrorYhigh = 0.
                    for b in range(pg[SP][key].GetN(), 0, -1):
                        xtemp = R.Double(-1.)
                        ytemp = R.Double(-1.)
                        pg[SP][key].GetPoint(b, xtemp, ytemp)
                        ytempErrorYlow = pg[SP][key].GetErrorYlow(b)
                        ytempErrorYhigh = pg[SP][key].GetErrorYhigh(b)
                        # if ytemp > ymax and max(pg[SP][key].GetErrorYlow(b),
                        #         pg[SP][key].GetErrorYhigh(b)) < accepted_error_max:
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
                        maxarrow = R.TArrow(ymax_pos, -0.08, ymax_pos, 0.)
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
                        for b in range(pg[SP][key].GetN()):
                            xtemp = R.Double(-1.)
                            ytemp = R.Double(-1.)
                            pg[SP][key].GetPoint(b, xtemp, ytemp)
                            if ytemp > yhalfmax and max(pg[SP][key].GetErrorYlow(b),
                                    pg[SP][key].GetErrorYhigh(b)) < accepted_error_halfmax:
                                x2 = xtemp
                                y2 = ytemp
                                xtemp_prev = R.Double(0.)
                                ytemp_prev = R.Double(0.)
                                for bprev in range(1, b+1):
                                    if b-bprev >= 0 and max(pg[SP][key].GetErrorYlow(b-bprev),
                                            pg[SP][key].GetErrorYhigh(b-bprev)) < accepted_error_halfmax:
                                        pg[SP][key].GetPoint(b-bprev, xtemp_prev, ytemp_prev)
                                        x1 = xtemp_prev
                                        y1 = ytemp_prev
                                        # linear interpolation:
                                        yhalfmax_pos = (yhalfmax*(x1-x2)+(y1*x2-y2*x1))/(y1-y2)
                                        break
                                else:
                                    yhalfmax_pos = x2*0.5

                                halfmaxarrow = R.TArrow(yhalfmax_pos, -0.057, yhalfmax_pos, 0.)
                                R.SetOwnership(halfmaxarrow, 0)
                                halfmaxarrow.SetLineColor(col)
                                halfmaxarrow.SetLineWidth(2)
                                halfmaxarrow.SetArrowSize(0.012)
                                halfmaxarrow.Draw()
                                break

                if legTitle is None:
                    pg[SP][key].legName = '#scale[0.4]{{M_{{H}} = {} GeV, M_{{X}} = {} GeV, c#tau = {} mm, #color[{dxyfrac_color}]{{{dxyfrac}%}}}}'.format(
                            *SP,
                            dxyfrac=FRACTIONS[fs][SP][1],
                            dxyfrac_color=displacement_color[SP])
                    if quantity == 'deltaR' and ymax_pos is not None and yhalfmax_pos is not None:
                        pg[SP][key].legName += ' #scale[0.4]{{#Delta R_{{max/2}}/#Delta R_{{max}} = {deltaRfrac}}}'.format(
                            deltaRfrac=round(yhalfmax_pos/ymax_pos, 3))
                else:
                    pg[SP][key].legName = legTitle


        
            if quantity == 'deltaR':
                run1_line = R.TLine(0.2, padYmin, 0.2, padYmax)
                R.SetOwnership(run1_line, 0)
                run1_line.SetLineColor(R.kGray)
                run1_line.SetLineStyle(2)
                run1_line.Draw()

            if quantity == 'cosAlpha':
                HLTcut_line = R.TLine(-0.8, padYmin, -0.8, padYmax)
                R.SetOwnership(HLTcut_line, 0)
                HLTcut_line.SetLineColor(R.kGray)
                HLTcut_line.SetLineStyle(2)
                HLTcut_line.Draw()

            canvas_eff.makeLegend(lWidth=0.55, pos='tr')
            canvas_eff.legend.resizeHeight()
            canvas_eff.firstPlot.SetMinimum(padYmin)
            canvas_eff.firstPlot.SetMaximum(padYmax)
            RT.addBinWidth(canvas_eff.firstPlot)

            if SPlist is not None and len(SPlist) > 1:
                SPdescr = SPcombiName+'_overlayedSPs' if SPcombiName is not None else ''
            elif SPlist is not None and len(SPlist) == 1:
                SPdescr = '{}-{}-{}_{displacement_str}'.format(*SP,
                        displacement_str=displacement_str[SP])
            else:
                SPdescr = ''

            outputfilename = u'DimSTE_{}{}Eff_HTo2XTo{}_{}'.format(
                    output_tag, quantity, fs, SPdescr)
            outputfilename = 'pdfs/' + slugify(outputfilename) + '.pdf'
            canvas_eff.cleanup(outputfilename)


def slugify(value, lowercase=False):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens. Returns the resulting string.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip())
    if lowercase is True: value = value.lower()
    value = unicode(re.sub('[-\s]+', '-', value))
    return value


if __name__ == '__main__':

    SP_COMBINATIONS = {
        'prompt dimuons': [
            (125,20,13),
            (125,50,50),
            (200,20,7),
            (200,50,20),
            (400,20,4),
            (400,50,8),
            (400,150,40),
            (1000,20,2),
            (1000,50,4),
            (1000,150,10),
            (1000,350,35),
        ],
        'highly pointing, short-lived muons (excl. M_{X} = 20 GeV samples)': [
            (1000,350,35),
            (1000,150,10),
            (1000,50,4),
            (400,150,40),
            (400,50,8),
            (200,50,20),
            (125,50,50),
        ],
    }

    SP_COMBINATIONS['all'] = [sp for sp in SIGNALPOINTS]

    for var,xTitle,xranges in (('deltaR','#Delta R(#mu#mu)', [0, 0.5]),
            ('cosAlpha', 'cos #alpha', [-1.05, 1.05])):
        for fs in ('2Mu2J',):
            for SPcombi in SP_COMBINATIONS.keys():
                makeEffPlots(var, fs, SP_COMBINATIONS[SPcombi], SPcombi,
                        padXmin=xranges[0], padXmax=xranges[1], padYmax=2.7,
                        xTitle=xTitle)
                makeEffPlots(var, fs, SP_COMBINATIONS[SPcombi], SPcombi,
                        padXmin=xranges[0], padXmax=xranges[1], padYmax=1.2,
                        xTitle=xTitle, add_hists=True, legTitle=SPcombi)

                # make per-sample plots
                for SP in SP_COMBINATIONS[SPcombi]:
                    makeEffPlots(var, fs, [SP,], '',
                            xTitle=xTitle)

