import ROOT as R
R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.SetBatch(True)
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import argparse, itertools

PARSER = argparse.ArgumentParser()
PARSER.add_argument('FILE', help='which file to run over')
ARGS = PARSER.parse_args()

LKeys = range(10, 301, 20)

singles = {}
for sample in itertools.chain(HG.BGORDER, ['Data']):

    singles[sample] = {}

    for L in LKeys:
        singles[sample][L] = {
            'num': R.TH1F('hNum_{}_{}'.format(L, sample), ';;', 100, 0., R.TMath.Pi()),
            'den': R.TH1F('hDen_{}_{}'.format(L, sample), ';;', 100, 0., R.TMath.Pi())
        }

boolMap = {True:'Less', False:'More'}

f = open(ARGS.FILE)
for line in f:
    cols = line.strip('\n').split()

    name     = cols[0]
    LxySig   = float(cols[15])
    deltaPhi = float(cols[18])
    Lxy      = float(cols[20])
    Sig      = float(cols[21])

    LKey = None
    for MyLKey in LKeys:
        if abs(Lxy-MyLKey)/MyLKey < 0.01:
            LKey = MyLKey
            break
    else:
        continue

    weight = float(cols[4])

    if 'Data' in name:
        sample = 'Data'
    elif 'QCD' in name:
        sample = 'QCD20toInf-ME'
    else:
        sample = name

    try:
        singles[sample][LKey]['num'].Fill(deltaPhi, Sig*weight)
        singles[sample][LKey]['den'].Fill(deltaPhi,     weight)
    except:
        pass

f.close()

X = R.TFile.Open('roots/Fixed.root', 'RECREATE')
for sample in singles:
    for key in singles[sample]:
        singles[sample][key]['num'].Write()
        singles[sample][key]['den'].Write()
X.Close()
