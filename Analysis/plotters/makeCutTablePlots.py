import ROOT as R
import DisplacedDimuons.Analysis.Plotter as Plotter
import DisplacedDimuons.Analysis.Selections as Selections
from DisplacedDimuons.Common.Utilities import SPStr
from DisplacedDimuons.Common.Constants import SIGNALPOINTS
import HistogramGetter
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
    'MUO' : {'IND' : {}, 'SEQ' : {}, 'NM1' : {} },
    'DIM' : {'IND' : {}, 'SEQ' : {}, 'NM1' : {} }
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
        headers = ('FS', 'mH', 'mX', 'cTau', 'Total') + cutList
        ref = (cols[2], (int(cols[3]), int(cols[4]), int(cols[5])))
        start = 4
    else:
        headers = ('Sample', 'Total') + cutList
        ref = cols[2]
        start = 1

    # make a line for each sample
    # add onto it if there are multiple
    if ref not in DATA[short][dtype]:
        DATA[short][dtype][ref] = {}
        for i, header in enumerate(headers[start:], start+2):
            DATA[short][dtype][ref][header]  = int(cols[i])
    else:
        for i, header in enumerate(headers[start:], start+2):
            DATA[short][dtype][ref][header] += int(cols[i])

f.close()

# compute the "Stack" version
BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'DY10to50', 'DY50toInf')
for obj in DATA:
    for dtype in DATA[obj]:
        cutList = Selections.CutLists[MAPPING[obj] + 'CutList' + MAPPING[dtype]]
        DATA[obj][dtype]['Stack'] = {}
        for ref in BGORDER:
            for header in ('Total',) + cutList:
                try:
                    DATA[obj][dtype]['Stack'][header] += DATA[obj][dtype][ref][header] * HistogramGetter.PLOTCONFIG[ref]['WEIGHT']
                except:
                    DATA[obj][dtype]['Stack'][header]  = DATA[obj][dtype][ref][header] * HistogramGetter.PLOTCONFIG[ref]['WEIGHT']

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
        if dtype in ('IND', 'SEQ'):
            func = lambda val, total: val/float(total) if total != 0 else 0.
        elif dtype in ('NM1',):
            func = lambda val, total: total/float(val) if val   != 0 else 0.
        for ref in DATA[obj][dtype]:
            if type(ref) == tuple:
                fs, sp = ref
                fname = 'CutTable_{}-{}_HTo2XTo{}_{}'.format(obj, dtype, fs, SPStr(sp))
            else:
                sample = ref
                fname = 'CutTable_{}-{}_{}'.format(obj, dtype, sample)

            fields = DATA[obj][dtype][ref]
            total = fields['Total']

            TITLE = ';' + MAPPING[obj] + ' Cuts;' + TITLES[dtype]
            HISTS[obj][dtype][ref] = R.TH1F(fname, TITLE, len(cutList), 0., float(len(cutList)))

            for i, header in enumerate(cutList):
                HISTS[obj][dtype][ref].SetBinContent(i+1, func(fields[header], total))
                HISTS[obj][dtype][ref].GetXaxis().SetBinLabel(i+1, Selections.PrettyTitles[header])

            HISTS[obj][dtype][ref].Write()

            makeIndividualPlots(obj, dtype, ref)
