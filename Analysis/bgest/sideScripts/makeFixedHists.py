import ROOT as R
R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.SetBatch(True)
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import argparse, itertools

PARSER = argparse.ArgumentParser()
PARSER.add_argument('FILE', help='which file to run over')
ARGS = PARSER.parse_args()

singles = {}
for sample in itertools.chain(HG.BGORDER, ['Data']):

    singles[sample] = {
        'LxyVSSig'   : R.TH3F('h_LxyVSSig_{}'   .format(sample), '', 100, 0., R.TMath.Pi(), 300, 0., 300., 200, 0., 50.),
        'LxyVSLxySig': R.TH3F('h_LxyVSLxySig_{}'.format(sample), '', 100, 0., R.TMath.Pi(), 300, 0., 300., 200, 0., 50.),
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

    #if LxySig < 7.: continue
    if not abs(LxySig - Lxy/Sig) < 1.e-3:
        print LxySig, Lxy, Sig, Lxy/Sig

    weight = float(cols[4])

    if 'Data' in name:
        sample = 'Data'
    elif 'QCD' in name:
        sample = 'QCD20toInf-ME'
    else:
        sample = name

    singles[sample]['LxyVSSig']   .Fill(deltaPhi, Lxy,    Sig, weight)
    singles[sample]['LxyVSLxySig'].Fill(deltaPhi, Lxy, LxySig, weight)

f.close()

X = R.TFile.Open('roots/Fixed.root', 'RECREATE')
for sample in singles:
    for key in singles[sample]:
        singles[sample][key].Write()
X.Close()
