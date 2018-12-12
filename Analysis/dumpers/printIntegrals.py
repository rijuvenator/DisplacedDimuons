import ROOT as R

# this has to be done right after import ROOT
R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.SetBatch(True)

import DisplacedDimuons.Analysis.RootTools as RT
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter
import subprocess as bash
import argparse

# define parser
PARSER = argparse.ArgumentParser()
PARSER.add_argument('-c' , '--category', dest='CATEGORY', default='D'        , choices=['D', 'R'], help='dimuon or recoMuon'    )
PARSER.add_argument('-s' , '--string'  , dest='STRING'  , default=''                             , help='cut string, e.g. NS_NH')
PARSER.add_argument('-m' , '--mconly'  , dest='MCONLY'  , action='store_true'                    , help='whether mconly'        )
PARSER.add_argument('-k' , '--hkey'    , dest='HKEY'    , default='Dim_pT'                       , help='histogram name'        )
PARSER.add_argument('-b1', '--bin1'    , dest='BIN1'    , default=0          , type=int          , help='first bin, 0 underflow')
PARSER.add_argument('-b2', '--bin2'    , dest='BIN2'    , default='N'                            , help='last bin, N overflow'  )
PARSER.add_argument('-t' , '--total'   , dest='TOTAL'   , action='store_true'                    , help='whether only total'    )
ARGS = PARSER.parse_args()

# get and process all the arguments; open a file
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
TOTAL = ARGS.TOTAL

# some constants
BGSAMPLES = ['WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf']
DATASAMPLES = ['DoubleMuonRun2016{}-07Aug17{}'.format(era, '' if era != 'B' else '-v2') for era in ('B', 'C', 'D', 'E', 'F', 'G', 'H')]

# get the stacked MC
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

# get the added data
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
# fields are: name (15) nBins (4) nEntries (11) Integral (11.2)
# + 3 spaces because 4 columns
# total = 44 (for blank line)
# prints an underline

BLANKLINE = '\033[4m{:44s}\033[m'.format(' ')

# what gets printed for a given histogram
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

    print '{:15s} {:4d} {:11d} {:11.2f}'.format(name, nBins, nEntries, Integral)

# header stuff
if ARGS.BIN2 == 'N':
    B2 = 'N+1'
elif ARGS.BIN2 == 'NM1':
    B2 = 'N'
else:
    B2 = ARGS.BIN2
print '\033[4m\033[1m=== {} :: {} :: {} :: Bins {}-{} ===\033[m'.format(FULLCATEGORY, ARGS.STRING, HKEY, ARGS.BIN1, B2)
print '\033[4m\033[1m{:15s} {:4s} {:>11s} {:>11s}\033[m'.format('Name', 'Bins', 'Entries', 'Integral')

# actual prints
printIntegral(MCStack, 'MC Total')
if not TOTAL:
    for SAMPLE in BGSAMPLES:
        printIntegral(h[SAMPLE], '  '+SAMPLE)

print BLANKLINE

# also print data
if not MCONLY:
    printIntegral(DataStack, 'Data Total')
    if not TOTAL:
        for era in ('B', 'C', 'D', 'E', 'F', 'G', 'H'):
            printIntegral(h['Data'+era], '  Data'+era)
    print BLANKLINE
