import ROOT as R
R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.SetBatch(True)
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import argparse, itertools
import numpy as np

PARSER = argparse.ArgumentParser()
PARSER.add_argument('FILE', help='which file to run over')
ARGS = PARSER.parse_args()

PI = R.TMath.Pi()

xbins = [i*PI/32. for i in xrange(9)] + [PI/2., 3.*PI/4., PI]
ybins = [float(i) for i in xrange(51)] + [float(i) for i in xrange(55, 91, 5)]

h = R.TH2F('h', '', len(xbins)-1, np.array(xbins), len(ybins)-1, np.array(ybins))

f = open(ARGS.FILE)
for line in f:
    cols = line.strip('\n').split()

    name     = cols[0]
    deltaPhi = float(cols[18])
    LxySig   = float(cols[15])

    if LxySig < 6: continue

    h.Fill(deltaPhi, LxySig)

f.close()

X = R.TFile.Open('roots/PoorMansShapeAnalysis.root', 'RECREATE')
h.Write()
X.Close()
