import ROOT as R
import glob, re, operator
import numpy as np
from DisplacedDimuons.Common.Constants import SIGNALPOINTS, SIGNALS
import DisplacedDimuons.Analysis.Plotter as Plotter
import argparse

# for switching between statistical methods
# probably just between AsymptoticLimits and HybridNew
PARSER = argparse.ArgumentParser()
PARSER.add_argument('--method', dest='METHOD', default='AsymptoticLimits')
ARGS = PARSER.parse_args()

CROSS_SECTION = 1.e-2

# converts a string into an operator;
# then OP[string](cTau, factor) will give the correct values
OP = {'div':operator.div, 'mul':operator.mul}

# CARDS are the datacard names, generated with generateCards.py
# TOKENS are just the mH_mX_cTau_op_factor substring
CARDS  = glob.glob('cards/*')
TOKENS = [s.replace('cards/card_','').replace('.txt','') for s in CARDS]

# codes for the quantiles, as well as a function for
# getting the code from the stored floating quantile value
QUANTILES = ('OBS', '-2S', '-1S', 'MED', '+1S', '+2S')
def getQuantileFromValue(value):
    TOL = 0.1
    if abs(value - (-1.0)) < TOL:
        return 'OBS'
    elif abs(value - .025) < TOL:
        return '-2S'
    elif abs(value - .16 ) < TOL:
        return '-1S'
    elif abs(value - .5  ) < TOL:
        return 'MED'
    elif abs(value - .84 ) < TOL:
        return '+1S'
    elif abs(value - .975) < TOL:
        return '+2S'

# whether to skip a particular point
# currently: for the small lifetimes, skip the /9 /10 and *anything points
def pointVeto(mH, mX, cTau, op, factor):
    if op == 'mul' and SIGNALS[mH][mX].index(cTau) == 0:
        return True
    if op == 'div' and SIGNALS[mH][mX].index(cTau) == 0 and factor > 8:
        return True
    return False

# output files are expected to be in combineOutput/ in the format below
# for HybridNew you probably need to hadd the different quantiles together
# now it opens each file, which is each individual point, gets the limit tree,
# loops over all 6 (obs + 5 quantiles) entries, and fills a dictionary
data = {}
for token in TOKENS:
    fname = 'combineOutput/higgsCombineLimits_2Mu_{}.{}{}.mH120.root'.format(token,ARGS.METHOD, '-hadded' if ARGS.METHOD=='HybridNew' else '')
    f = R.TFile.Open(fname)
    if not f: continue
    t = f.Get('limit')
    if not t:
        print fname
        continue
    data[token] = {}
    for i in xrange(6):
        t.GetEntry(i)
        quantileToken = getQuantileFromValue(t.quantileExpected)
        data[token][quantileToken] = {}
        data[token][quantileToken]['limit'] = t.limit
        data[token][quantileToken]['err'  ] = t.limitErr

# print the limits out
# I actually want to look up the data using an sp, rather than a token,
# so take advantage of this printing loop to fill another dictionary
# also, if a particular quantile code doesn't exist, fill it with obs
# which should always exist. it should become obvious if there's a problem.
newData = {}
for token in data:
    match = re.match(r'(\d{3,4})_(\d{2,3})_(\d{1,4})_(div|mul)_(\d{1,2})', token)
    mH, mX, cTau, op, factor = match.groups()
    sp = tuple(map(int, (mH, mX, cTau)))

    if sp not in newData:
        newData[sp] = {}
    newData[sp][(op, factor)] = data[token]

    print '*** 2Mu {:4s} {:3s} {:4s} --> {:9.4f} ***'.format(mH, mX, cTau, OP[op](float(cTau), float(factor)))
    for key in QUANTILES:
        if key not in data[token]:
            if 'OBS' in data[token]:
                data[token][key] = {'limit':data[token]['OBS']['limit'], 'err':0.}
            else:
                data[token][key] = {'limit':0., 'err':0.}
        print '  ', key, data[token][key]['limit']

# loop over mH, mX pairs
# fill an X and 6 Y vectors with values
# X only needs to be filled once; do it on OBS
# Y gets filled for each key; that is also when the applied cross section is put back in
# the table zip block sorts a "table" by the X values so that a connected graph doesn't jump around
# then, because zip is its own inverse, the vectors can be updated
# then, make some graphs, setting the errors "manually", make the plots, put them on a canvas, and finish
for mH in SIGNALS:
    for mX in SIGNALS[mH]:
#for mH in (400,):
#    for mX in (150,):
        x = []
        y = {key:[] for key in QUANTILES}
        for i,cTau in enumerate(SIGNALS[mH][mX]):
            for op, factor in newData[(mH, mX, cTau)]:
                if pointVeto(mH, mX, cTau, op, factor): continue
                for key in QUANTILES:
                    if key == 'OBS':
                        x.append(OP[op](float(cTau), float(factor))/10.)
                    y[key].append(newData[(mH, mX, cTau)][(op, factor)][key]['limit'] * CROSS_SECTION)

        table = zip(x, y['OBS'], y['-2S'], y['-1S'], y['MED'], y['+1S'], y['+2S'])
        table.sort(key=lambda i:i[0])
        x, y['OBS'], y['-2S'], y['-1S'], y['MED'], y['+1S'], y['+2S'] = zip(*table)

        xArray = np.array(x)
        zeroes = np.zeros(len(x))
        g = {
            'OBS' : R.TGraph           (len(x), xArray, np.array(y['OBS'])                                                        ),
            'MED' : R.TGraph           (len(x), xArray, np.array(y['MED'])                                                        ),
            '1S'  : R.TGraphAsymmErrors(len(x), xArray, np.array(y['MED']), zeroes, zeroes, -np.array(y['-1S'])+np.array(y['MED']), np.array(y['+1S'])-np.array(y['MED'])),
            '2S'  : R.TGraphAsymmErrors(len(x), xArray, np.array(y['MED']), zeroes, zeroes, -np.array(y['-2S'])+np.array(y['MED']), np.array(y['+2S'])-np.array(y['MED'])),
        }

        p = {
            'OBS' : Plotter.Plot(g['OBS'], 'Observed limits'             , 'pl', 'pl'),
            'MED' : Plotter.Plot(g['MED'], 'Expected limits (median)'    , 'pl', 'pl'),
            '1S'  : Plotter.Plot(g['1S' ], 'Expected limits (#pm1#sigma)', 'f' , '3' ),
            '2S'  : Plotter.Plot(g['2S' ], 'Expected limits (#pm2#sigma)', 'f' , '3' ),
        }

        c = Plotter.Canvas(lumi='13 TeV ( 35.9 fb^{{-1}} ) m_{{H}} = {} GeV, m_{{X}} = {} GeV'.format(mH, mX), logy=True)
        #c.addMainPlot(p['2S'])
        c.addMainPlot(p['1S'])
        c.addMainPlot(p['MED'])
        c.addMainPlot(p['OBS'])

        p['2S'].setColor(R.kOrange, which='LMF')
        p['1S'].setColor(R.kGreen , which='LMF')

        p['MED'].SetMarkerSize(2.)
        p['MED'].SetLineWidth(5)
        p['MED'].setColor(R.kRed, which='LMF')

        c.mainPad.SetLogx()

        c.makeLegend(lWidth=.2, autoOrder=False, pos='tr')
        c.legend.addLegendEntry(p['OBS'])
        c.legend.addLegendEntry(p['MED'])
        c.legend.addLegendEntry(p['1S' ])
        c.legend.resizeHeight()
        c.legend.moveLegend(X=-.15)

        c.firstPlot.setTitles(X='c#tau [cm]', Y='Upper limit on #sigma(H#rightarrowXX)B(X#rightarrow#mu#mu) [pb]')
        c.cleanup('pdfs/Limits_2Mu_{}_{}_{}.pdf'.format(mH, mX, ARGS.METHOD))
