import ROOT as R

# this has to be done right after import ROOT
R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.SetBatch(True)

import DisplacedDimuons.Analysis.RootTools as RT
import HistogramGetter
import subprocess as bash
import argparse

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-c' , '--category', dest='CATEGORY', default='D'        , choices=['D', 'R'])
PARSER.add_argument('-s' , '--string'  , dest='STRING'  , default=''                             )
PARSER.add_argument('-m' , '--mconly'  , dest='MCONLY'  , action='store_true'                    )
PARSER.add_argument('-k' , '--hkey'    , dest='HKEY'    , default='Dim_pT'                       )
PARSER.add_argument('-b1', '--bin1'    , dest='BIN1'    , default=0          , type=int          )
PARSER.add_argument('-b2', '--bin2'    , dest='BIN2'    , default='N'                            )
ARGS = PARSER.parse_args()

if ARGS.CATEGORY == 'D':
    FULLCATEGORY = 'DimuonPlots'
elif ARGS.CATEGORY == 'R':
    FULLCATEGORY = 'RecoMuonPlots'

if ARGS.BIN2 != 'N' and ARGS.BIN2 != 'NM1':
    try:
        int(ARGS.BIN2)
    except:
        raise Exception('Error: Bin 2 must be int, N, or NM1')

FILE = R.TFile.Open('../analyzers/roots/Main/{}{}.root'.format(FULLCATEGORY, '' if ARGS.STRING == '' else '_'+ARGS.STRING))
if not FILE:
    raise Exception('{}{}.root: No such file'.format(FULLCATEGORY, '' if ARGS.STRING == '' else '_'+ARGS.STRING))

MCONLY = ARGS.MCONLY
HKEY = ARGS.HKEY

BGSAMPLES = ['WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'DY10to50', 'DY50toInf']
DATASAMPLES = ['DoubleMuonRun2016{}-07Aug17{}'.format(era, '' if era != 'B' else '-v2') for era in ('B', 'C', 'D', 'E', 'F', 'G', 'H')]

h = {}
MCStack = HistogramGetter.getHistogram(FILE, BGSAMPLES[0], HKEY)
if not MCStack:
    raise Exception('{}: No such MC key'.format(HKEY))
MCStack = MCStack.Clone()
MCStack.Scale(HistogramGetter.PLOTCONFIG[BGSAMPLES[0]]['WEIGHT'])
for SAMPLE in BGSAMPLES:
    h[SAMPLE] = HistogramGetter.getHistogram(FILE, SAMPLE, HKEY).Clone()
    h[SAMPLE].Scale(HistogramGetter.PLOTCONFIG[SAMPLE]['WEIGHT'])
for SAMPLE in BGSAMPLES[1:]:
    MCStack.Add(h[SAMPLE])

if not MCONLY:
    DataStack = HistogramGetter.getHistogram(FILE, DATASAMPLES[0], HKEY)
    if not DataStack:
        raise Exception('{}: No such data key'.format(HKEY))
    DataStack = DataStack.Clone()
    for dsample, era in zip(DATASAMPLES, ('B', 'C', 'D', 'E', 'F', 'G', 'H')):
        h['Data'+era] = HistogramGetter.getHistogram(FILE, dsample, HKEY).Clone()
    for era in ('C', 'D', 'E', 'F', 'G', 'H'):
        DataStack.Add(h['Data'+era])

# Probably won't be changing this that much
# fields are: name (11) nBins (4) nEntries (11) Integral (11.2)
# total = 40 (for blank line)

BLANKLINE = '\033[4m{:40s}\033[m'.format(' ')

def printIntegral(hist, name):
    try:
        H = hist.GetStack().Last()
    except:
        H = hist


    nBins    = H.GetNbinsX()
    nEntries = int(H.GetEntries())

    if ARGS.BIN2 == 'N':
        BIN2 = nBins+1
    elif ARGS.BIN2 == 'NM1':
        BIN2 = nBins
    else:
        BIN2 = int(ARGS.BIN2)

    Integral = H.Integral(ARGS.BIN1, BIN2)

    print '{:11s} {:4d} {:11d} {:11.2f}'.format(name, nBins, nEntries, Integral)

print '\033[4m\033[1m=== {} :: {} :: {} ===\033[m'.format(FULLCATEGORY, ARGS.STRING, HKEY)
print '\033[4m\033[1m{:11s} {:4s} {:>11s} {:>11s}\033[m'.format('Name', 'Bins', 'Entries', 'Integral')
printIntegral(MCStack, 'MC Total')
for SAMPLE in BGSAMPLES:
    printIntegral(h[SAMPLE], '  '+SAMPLE)

print BLANKLINE

if not MCONLY:
    printIntegral(DataStack, 'Data Total')
    for era in ('B', 'C', 'D', 'E', 'F', 'G', 'H'):
        printIntegral(h['Data'+era], '  Data'+era)
    print BLANKLINE
