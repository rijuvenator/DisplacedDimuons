import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.AnalysisTools as AT

# a dictionary of the limits on sigmaB for different signal points
# I eyeballed the plots / used an online digitizer, which was tedious
# this may need to be updated with different cross sections for different
# reweighted lifetimes, since this is the same value for a single point
# also, with the reweighting the nEvents field is actually sumWeights
# for the nominal (factor 1), sumWeights is just nEvents
# so the older scripts can become compatible by replacing SignalInfo[sp]['nEvents']
# with SignalInfo[sp]['sumWeights'][1]
SignalInfo = {
#   (1000, 350,   35) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    (1000, 350,  350) : {'sigmaBLimit' : 2.5e-3 , 'sumWeights' : {}},
    (1000, 350, 3500) : {'sigmaBLimit' : 3.5e-3 , 'sumWeights' : {}},
#   (1000, 150,   10) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    (1000, 150,  100) : {'sigmaBLimit' : 4.0e-3 , 'sumWeights' : {}},
    (1000, 150, 1000) : {'sigmaBLimit' : 1.7e-3 , 'sumWeights' : {}},
#   (1000,  50,    4) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    (1000,  50,   40) : {'sigmaBLimit' : 2.1e-2 , 'sumWeights' : {}},
    (1000,  50,  400) : {'sigmaBLimit' : 4.1e-3 , 'sumWeights' : {}},
#   (1000,  20,    2) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    (1000,  20,   20) : {'sigmaBLimit' : 1.0    , 'sumWeights' : {}},
    (1000,  20,  200) : {'sigmaBLimit' : 1.5e-1 , 'sumWeights' : {}},
#   ( 400, 150,   40) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    ( 400, 150,  400) : {'sigmaBLimit' : 2.7e-3 , 'sumWeights' : {}},
    ( 400, 150, 4000) : {'sigmaBLimit' : 4.4e-3 , 'sumWeights' : {}},
#   ( 400,  50,    8) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    ( 400,  50,   80) : {'sigmaBLimit' : 1.0e-2 , 'sumWeights' : {}},
    ( 400,  50,  800) : {'sigmaBLimit' : 2.7e-3 , 'sumWeights' : {}},
#   ( 400,  20,    4) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    ( 400,  20,   40) : {'sigmaBLimit' : 4.8e-2 , 'sumWeights' : {}},
    ( 400,  20,  400) : {'sigmaBLimit' : 9.6e-3 , 'sumWeights' : {}},
#   ( 200,  50,   20) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    ( 200,  50,  200) : {'sigmaBLimit' : 8.8e-3 , 'sumWeights' : {}},
    ( 200,  50, 2000) : {'sigmaBLimit' : 9.7e-3 , 'sumWeights' : {}},
#   ( 200,  20,    7) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    ( 200,  20,   70) : {'sigmaBLimit' : 4.3e-2 , 'sumWeights' : {}},
    ( 200,  20,  700) : {'sigmaBLimit' : 9.2e-3 , 'sumWeights' : {}},
#   ( 125,  50,   50) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    ( 125,  50,  500) : {'sigmaBLimit' : 2.7e-2 , 'sumWeights' : {}},
    ( 125,  50, 5000) : {'sigmaBLimit' : 6.8e-2 , 'sumWeights' : {}},
#   ( 125,  20,   13) : {'sigmaBLimit' : 0.     , 'sumWeights' : {}},
    ( 125,  20,  130) : {'sigmaBLimit' : 4.8e-2 , 'sumWeights' : {}},
    ( 125,  20, 1300) : {'sigmaBLimit' : 4.3e-2 , 'sumWeights' : {}},
}

# this is the result of catting the output files
# from the reweightedPlots jobs
# lines are of the format mH mX cTau ::: factor weight
f = open('text/SignalSumWeights.txt')
for line in f:
    cols = line.strip('\n').split()
    sp = tuple(map(int, cols[:3]))
    if sp not in SignalInfo: continue
    factor = int(cols[4])
    weight = float(cols[5])
    SignalInfo[sp]['sumWeights'][factor] = weight

# this is the scale factor for signal samples
# turning whatever events pass out of ~30000 into an expected number of events
def ScaleFactor(sp, factor=1, sigmaB=None):
    if sigmaB is None:
        sigmaB = SignalInfo[sp]['sigmaBLimit']
    return sigmaB / SignalInfo[sp]['sumWeights'][factor] * HG.INTEGRATED_LUMINOSITY_2016

# sHist and bHist and signal and bg histograms; sCum and bCum are their cumulatives
# nBins and xAxis are just one of these axes, to save extra calls
# ibin is the current bin number
# FORWARD is the forward bool for the cumulative histogram, i.e.
# true if you want a normal int(0, x) integral, and false if you want int(x, inf)
# I'm adding the overflows in manually because the GetCumulative function
# doesn't put it in by default, and it's weird to use my usual addFlows function
def calculateFOM(sHist, bHist, sCum, bCum, nBins, ibin, xAxis, FORWARD):

    S = sCum.GetBinContent(ibin)
    B = bCum.GetBinContent(ibin)
    if not FORWARD:
        S += sHist.GetBinContent(nBins+1)
        B += bHist.GetBinContent(nBins+1)
    FOMs = {
        'ZBi' : AT.ZBi(S+B, B, 1.),
        'ZPL' : AT.ZPL(S+B, B, 1.),
    }

    cutVal = xAxis.GetBinUpEdge(ibin) if FORWARD else xAxis.GetBinLowEdge(ibin)

    return S, B, cutVal, FOMs
