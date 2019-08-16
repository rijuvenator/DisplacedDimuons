import ROOT as R
R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.SetBatch(True)
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import argparse, itertools

PARSER = argparse.ArgumentParser()
PARSER.add_argument('FILE', help='which file to run over')
ARGS = PARSER.parse_args()

singles = R.TH3F('hDalitz_{}'.format('Signal'), ';#rho_{1};#rho_{2};M', 100, 0., 0.5, 100, 0., 0.5, 20, 50., 250.)

f = open(ARGS.FILE)
for line in f:
    cols = line.strip('\n').split()

    pA, pB, pM = map(float, cols[-3:])

    M = pA+pB+pM

    singles.Fill(pA/M, pB/M, M)

f.close()

X = R.TFile.Open('DalitzSignal.root', 'RECREATE')
singles.Write()
X.Close()
