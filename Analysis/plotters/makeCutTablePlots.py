import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.Selections as Selections
from DisplacedDimuons.Common.Utilities import SPStr
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import re

# some constants
MAPPING = {
    'MUO' : 'Muon',
    'DIM' : 'Dimuon',
    'IND' : 'PlusAll',
    'SEQ' : 'PlusNone',
    'NM1' : ''
}
TITLES = {
    'IND' : 'Individual Efficiency',
    'SEQ' : 'Sequential Efficiency',
    'NM1' : 'N#minus1 Efficiency',
}

# get data from text file
DATA = {
    'MUO' : {'IND' : [], 'SEQ' : [], 'NM1' : [] },
    'DIM' : {'IND' : [], 'SEQ' : [], 'NM1' : [] }
}
signal = True
f = open('../dumpers/cutTable.txt')
for line in f:
    # split up the line, check if this is a header line, save what it is, then skip it
    cols = line.strip('\n').split()
    if 'Sample' in cols: signal = False
    if 'mH'     in cols: signal = True
    if 'Sample' in cols or 'mH' in cols: continue

    # figure out what kind of data this is, and define the cutList
    matches = re.match(r'(MUO|DIM) (IND|SEQ|NM1):', line)
    short, dtype = matches.group(1), matches.group(2)
    cutList = Selections.CutLists[MAPPING[short] + 'CutList' + MAPPING[dtype]]

    # define the headers for the columns
    if signal:
        headers = ('FS', 'mH', 'mX', 'cTau') + cutList
    else:
        headers = ('Sample',) + cutList

    # fill data
    # i+2 because the first two columns are OBJ DTYPE:
    fields = {}
    for i, header in enumerate(headers):
        fields[header] = cols[i+2]
    DATA[short][dtype].append(fields)
f.close()

# plotter function
def makeIndividualPlots(obj, dtype, key):
    if type(key) == tuple:
        fs, sp = key
        lumi = '{} ({} GeV, {} GeV, {} mm)'.format(fs, *sp)
        fname = 'pdfs/CutTable_{}-{}_HTo2XTo{}_{}.pdf'.format(obj, dtype, fs, SPStr(sp))
    else:
        sample = key
        lumi = sample
        fname = 'pdfs/CutTable_{}-{}_{}.pdf'.format(obj, dtype, sample)

    p = Plotter.Plot(HISTS[obj][dtype][key], '', '', 'hist')
    canvas = Plotter.Canvas(lumi=lumi)
    canvas.addMainPlot(p)
    canvas.firstPlot.SetMaximum(1.)
    canvas.firstPlot.SetMinimum(0.)

    #canvas.firstPlot.SetMarkerColor(R.kBlue)
    #canvas.firstPlot.SetLineColor(R.kBlue)

    canvas.firstPlot.SetLineColor(4000)
    canvas.firstPlot.SetFillColor(R.kOrange)

    for ibin in xrange(1, p.GetNbinsX()+1):
        canvas.drawText(text='{:.2f}'.format(p.GetBinContent(ibin)), pos=(ibin-0.5, 0.1), align='cc', NDC=False)
    canvas.cleanup(fname)

# make histograms, write them to a file, and make the PDFs
f = R.TFile('../analyzers/roots/CutTable.root', 'RECREATE')
HISTS = {
    'MUO' : {'IND' : {}, 'SEQ' : {}, 'NM1' : {} },
    'DIM' : {'IND' : {}, 'SEQ' : {}, 'NM1' : {} }
}
for obj in DATA:
    for dtype in DATA[obj]:
        cutList = Selections.CutLists[MAPPING[obj] + 'CutList' + MAPPING[dtype]]
        for fields in DATA[obj][dtype]:
            if 'mH' in fields:
                sp = (int(fields['mH']), int(fields['mX']), int(fields['cTau']))
                fs = fields['FS']
                name = 'CutTable_{}-{}_HTo2XTo{}_{}'.format(obj, dtype, fs, SPStr(sp))
                key = (fs, sp)
            else:
                sample = fields['Sample']
                name = 'CutTable_{}-{}_{}'.format(obj, dtype, sample)
                key = sample

            TITLE = ';' + MAPPING[obj] + ' Cuts;' + TITLES[dtype]
            HISTS[obj][dtype][key] = R.TH1F(name, TITLE, len(cutList), 0., float(len(cutList)))

            for i, header in enumerate(cutList):
                HISTS[obj][dtype][key].SetBinContent(i+1, float(fields[header]))
                HISTS[obj][dtype][key].GetXaxis().SetBinLabel(i+1, Selections.PrettyTitles[header])

            HISTS[obj][dtype][key].Write()

            makeIndividualPlots(obj, dtype, key)

# this is not that interesting or useful
#COLORS = {
#    (1000, 350,   35) : R.kBlack,
#    (1000, 350,  350) : R.kBlack+1,
#    (1000, 350, 3500) : R.kBlack+2,
#    (1000, 150,   10) : R.kYellow,
#    (1000, 150,  100) : R.kYellow+1,
#    (1000, 150, 1000) : R.kYellow+2,
#    (1000,  50,    4) : R.kViolet,
#    (1000,  50,   40) : R.kViolet+1,
#    (1000,  50,  400) : R.kViolet+2,
#    (1000,  20,    2) : R.kRed,
#    (1000,  20,   20) : R.kRed+1,
#    (1000,  20,  200) : R.kRed+2,
#    ( 400, 150,   40) : R.kBlue,
#    ( 400, 150,  400) : R.kBlue+1,
#    ( 400, 150, 4000) : R.kBlue+2,
#    ( 400,  50,    8) : R.kSpring,
#    ( 400,  50,   80) : R.kSpring+1,
#    ( 400,  50,  800) : R.kSpring+2,
#    ( 400,  20,    4) : R.kMagenta,
#    ( 400,  20,   40) : R.kMagenta+1,
#    ( 400,  20,  400) : R.kMagenta+2,
#    ( 200,  50,   20) : R.kCyan,
#    ( 200,  50,  200) : R.kCyan+1,
#    ( 200,  50, 2000) : R.kCyan+2,
#    ( 200,  20,    7) : R.kTeal,
#    ( 200,  20,   70) : R.kTeal+1,
#    ( 200,  20,  700) : R.kTeal+2,
#    ( 125,  50,   50) : R.kGreen,
#    ( 125,  50,  500) : R.kGreen+1,
#    ( 125,  50, 5000) : R.kGreen+2,
#    ( 125,  20,   13) : R.kOrange,
#    ( 125,  20,  130) : R.kOrange+1,
#    ( 125,  20, 1300) : R.kOrange+2,
#}
#
#PLOTS = {}
#for sp in HISTS:
#    PLOTS[sp] = Plotter.Plot(HISTS[sp], legName='({}, {}, {})'.format(*sp), legType='lp', option='hist p')
#
#def makeCombinedPlot():
#    canvas = Plotter.Canvas(lumi='CutTable Plot', cWidth=1000)
#    for sp in SIGNALPOINTS:
#        canvas.addMainPlot(PLOTS[sp])
#        PLOTS[sp].SetMarkerColor(COLORS[sp])
#        PLOTS[sp].SetLineColor(COLORS[sp])
#
#    canvas.firstPlot.SetMaximum(1.)
#    canvas.firstPlot.SetMinimum(0.)
#    canvas.scaleMargins(3.5, 'R')
#
#    canvas.makeLegend()
#    canvas.legend.resizeHeight(scale=.8)
#    canvas.legend.moveLegend(X=.18)
#
#    canvas.cleanup('pdfs/CutTable_HTo2XTo4Mu_Global.pdf')
#
#makeCombinedPlot()
