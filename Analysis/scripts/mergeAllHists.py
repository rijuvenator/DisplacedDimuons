import os, re
import argparse
import ROOT as R
import DisplacedDimuons.Analysis.HistogramGetter as HistogramGetter

Patterns = {
    "HTo2XTo4Mu": re.compile(r"(.*)_HTo2XTo4Mu_(\d{3,4})_(\d{2,3})_(\d{1,4})"),
    "HTo2XTo2Mu2J": re.compile(r"(.*)_HTo2XTo2Mu2J_(\d{3,4})_(\d{2,3})_(\d{1,4})"),
    "HTo2XTo2Mu2J_reHLT_CosmicSeed": re.compile(
        r"(.*)_HTo2XTo2Mu2J_reHLT_CosmicSeed_(\d{3,4})_(\d{2,3})_(\d{1,4})"
    ),
    "HTo2XTo2Mu2J_reHLT_ppSeed": re.compile(
        r"(.*)_HTo2XTo2Mu2J_reHLT_ppSeed_(\d{3,4})_(\d{2,3})_(\d{1,4})"
    ),
}


def importHistograms(filepath):

    # dictionary structure for collecting all histograms
    hists = {}

    f_allhists = HistogramGetter.getHistograms(filepath)

    for fs, sp in f_allhists:
        if fs not in hists:
            hists[fs] = {}

        for hkey in f_allhists[(fs, sp)]:
            if hkey not in hists[fs]:
                hists[fs][hkey] = f_allhists[(fs, sp)][hkey].Clone()

            else:
                hists[fs][hkey].Add(f_allhists[(fs, sp)][hkey])

            hname = hists[fs][hkey].GetName()
            if "HTo2X" in hname:
                if "4Mu" in hname:
                    # hkey has the form KEY_HTo2XTo4Mu_mH_mX_cTau
                    matches = Patterns["HTo2XTo4Mu"].match(hname)
                    fs = "4Mu"

                elif "2Mu2J" in hname:
                    # hname has the form KEY_HTo2XTo2Mu2J_mH_mX_cTau
                    matches = Patterns["HTo2XTo2Mu2J"].match(hname)
                    if "reHLT_CosmicSeed" in hname:
                        matches = Patterns["HTo2XTo2Mu2J_reHLT_CosmicSeed"].match(hname)
                    if "reHLT_ppSeed" in hname:
                        matches = Patterns["HTo2XTo2Mu2J_reHLT_ppSeed"].match(hname)

                if matches:
                    sp = tuple(map(int, matches.group(2, 3, 4)))

                    hname = hname.replace("_{}_{}_{}".format(*sp), "")

                    hists[fs][hkey].SetName(hname)

            else:
                raise NotImplementedError("Only signal samples supported at this point")

    return hists


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "FILEPATH", help="Path of a hadded ROOT file containing histograms for merging"
    )

    args = parser.parse_args()
    hists = importHistograms(args.FILEPATH)

    outfile = R.TFile.Open(args.FILEPATH.replace(".root", "_merged.root"), "RECREATE")
    for fs in hists:
        for key in hists[fs]:
            hists[fs][key].Write()

    outfile.Close()
