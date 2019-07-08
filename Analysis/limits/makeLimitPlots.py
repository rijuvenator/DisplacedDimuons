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
PARSER.add_argument('--square', dest='SQUARE', action='store_true')
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
    if op == 'mul' and SIGNALS[mH][mX].index(cTau) == 1 and factor > 15:
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
for token in sorted(data.keys()):
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

rColors = {
    'UCLA_BLUE' : R.TColor(7001, *[c/255. for c in (39 , 116, 174)]),
    'UCLA_GOLD' : R.TColor(7002, *[c/255. for c in (259, 209,   0)]),
}

# loop over mH, mX pairs
# fill an X and 6 Y vectors with values
# X only needs to be filled once; do it on OBS
# Y gets filled for each key; that is also when the applied cross section is put back in
# just before filling all the Y, determine whether to skip this point:
# if it's pointVeto, or the limit is 0 because the job didn't finish or whatever, etc.
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

            sp = (mH, mX, cTau)
            if (mH, mX, cTau) not in newData: continue
            for op, factor in newData[sp]:
                if pointVeto(mH, mX, cTau, op, factor):
                    print 'Vetoing', mH, mX, cTau, op, factor
                    continue
                if newData[sp][(op, factor)]['OBS']['limit'] == 0.:
                    print 'Zeroing', mH, mX, cTau, op, factor
                    continue

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
            'OBS' : R.TGraph           (len(x), xArray, np.array(y['OBS'])                                                                                               ),
            'MED' : R.TGraph           (len(x), xArray, np.array(y['MED'])                                                                                               ),
            '1S'  : R.TGraphAsymmErrors(len(x), xArray, np.array(y['MED']), zeroes, zeroes, -np.array(y['-1S'])+np.array(y['MED']), np.array(y['+1S'])-np.array(y['MED'])),
            '2S'  : R.TGraphAsymmErrors(len(x), xArray, np.array(y['MED']), zeroes, zeroes, -np.array(y['-2S'])+np.array(y['MED']), np.array(y['+2S'])-np.array(y['MED'])),
        }

        p = {
            'OBS' : Plotter.Plot(g['OBS'], 'Observed'               , 'pl', 'pl'),
#           'MED' : Plotter.Plot(g['MED'], 'Expected (median)'      , 'pl', 'pl'),
            'MED' : Plotter.Plot(g['MED'], 'Expected (median)'      , 'l' , 'l' ),
            '1S'  : Plotter.Plot(g['1S' ], 'Expected (68% quantile)', 'f' , '3' ),
            '2S'  : Plotter.Plot(g['2S' ], 'Expected (95% quantile)', 'f' , '3' ),
        }

        dummyGraph = R.TGraph(2, np.array([.1, 30000.]), np.array([50., 5.e-4]))
        dummy = Plotter.Plot(dummyGraph, '', '', 'p')

        c = Plotter.Canvas(lumi='35.9 fb^{-1} (13 TeV)', logy=True, cWidth=600 if ARGS.SQUARE else 800)

        #c = Plotter.Canvas(lumi='35.9 fb^{{-1}} (13 TeV) m_{{H}} = {} GeV, m_{{X}} = {} GeV'.format(mH, mX), logy=True)

        c.addMainPlot(dummy, addToPlotList=False)
        dummy.setColor(0, which='LMF')

        #c.addMainPlot(p['2S'])
        c.addMainPlot(p['1S'])
        c.addMainPlot(p['MED'])
        c.addMainPlot(p['OBS'])

        COLORS = {
            'STANDARD' : {
                'MED': R.kRed,
                '1S' : R.kGreen,
            },
            'UCLA' : {
                'MED': 7001,
                '1S' : 7002,
            }
        }

        CKEY = 'UCLA'

        p['1S'].setColor(COLORS[CKEY]['1S'] , which='LMF')

        p['MED'].SetMarkerSize(2.)
        p['MED'].SetLineWidth(5)
        p['MED'].setColor(COLORS[CKEY]['MED'], which='LMF')

        c.mainPad.SetLogx()

        c.makeLegend(lWidth=.2, autoOrder=False, pos='tr')
        c.legend.addLegendEntry(p['OBS'])
        c.legend.addLegendEntry(p['MED'])
        c.legend.addLegendEntry(p['1S' ])
        c.legend.resizeHeight()
        c.legend.moveLegend(X=-.19)
        if ARGS.SQUARE:
            c.legend.moveLegend(X=-.04)
            c.firstPlot.scaleTitleOffsets(1.1, 'XY')

        c.drawText('m_{{H}} = {} GeV'.format(mH), (c.margins['l']+.03, 1.-c.margins['t']-.04    ), 'tl')
        c.drawText('m_{{X}} = {} GeV'.format(mX), (c.margins['l']+.03, 1.-c.margins['t']-.04-.05), 'tl')

        c.firstPlot.setTitles(X='c#tau [cm]', Y='95% CL upper limit on #sigma(H#rightarrowXX)B(X#rightarrow#mu#mu) [pb]')
        c.cleanup('pdfs/Limits_2Mu_{}_{}_{}.pdf'.format(mH, mX, ARGS.METHOD))
