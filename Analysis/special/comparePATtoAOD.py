import ROOT as R
from DisplacedDimuons.Common.Utilities import SPStr

R.gROOT.SetBatch(True)

FileTemplate = '/eos/cms/store/user/adasgupt/DisplacedDimuons/NTuples/Special/{}ntuple_HTo2XTo2Mu2J_{}_NoTrackerTweak.root'
SignalPoints = ((125, 20, 13), (1000, 150, 1000))

FILES, TREES = {}, {}
for sp in SignalPoints:
    FILES[sp] = {}
    TREES[sp] = {}
    FILES[sp]['AOD'] = R.TFile.Open(FileTemplate.format('aodOnly_', SPStr(sp)))
    FILES[sp]['PAT'] = R.TFile.Open(FileTemplate.format(''        , SPStr(sp)))
    for TYPE in ('AOD', 'PAT'):
        TREES[sp][TYPE] = FILES[sp][TYPE].Get('SimpleNTupler/DDTree')

for sp in SignalPoints:
    print 'Now checking signal point', sp

    tPAT = TREES[sp]['PAT']
    tAOD = TREES[sp]['AOD']
    nEntriesPAT = tPAT.GetEntries()
    nEntriesAOD = tAOD.GetEntries()

    if not nEntriesPAT == nEntriesAOD:
        print 'PAT and AOD do not have the same number of entries:', nEntriesPAT, 'vs', nEntriesAOD
    else:
        print 'PAT and AOD have the same number of entries:', nEntriesPAT

    quantities = ('bs_x', 'vtx_pv_x', 'gen_pt', 'dsamu_px', 'rsamu_px', 'dim_pt', 'dim_mu1_px')
    axislimits = ((.1, .13), (.101, .109), (0., 200.), (-200., 200.), (-200., 200.), (0., 200.), (-20., 20.))

    for q, axes in zip(quantities, axislimits):
        hPAT = R.TH1F('hPAT', '', 100, *axes)
        hAOD = R.TH1F('hAOD', '', 100, *axes)

        tPAT.Draw(q + '>>hPAT')
        tAOD.Draw(q + '>>hAOD')

        for ibin in xrange(hPAT.GetNbinsX()+1):
            if not hPAT.GetBinContent(ibin) == hAOD.GetBinContent(ibin):
                print 'PAT and AOD', q, 'histograms differ'
                break
        else:
            print 'PAT and AOD', q, 'histograms are identical'

        R.gROOT.ProcessLine('delete gROOT->FindObject("hPAT");')
        R.gROOT.ProcessLine('delete gROOT->FindObject("hAOD");')
