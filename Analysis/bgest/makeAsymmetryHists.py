import ROOT as R
R.PyConfig.IgnoreCommandLineOptions = True
R.gROOT.SetBatch(True)
import DisplacedDimuons.Analysis.HistogramGetter as HG
import DisplacedDimuons.Analysis.RootTools as RT
import argparse, itertools

PARSER = argparse.ArgumentParser()
PARSER.add_argument('FILE', help='which file to run over')
PARSER.add_argument('--cutoff', dest='LXYSIGCUTOFF', type=float, default=6.)
ARGS = PARSER.parse_args()

hists, singles = {}, {}
for sample in itertools.chain(HG.BGORDER, ['Data']):

    hists[sample] = {
        'LxySig-SplitDPhi' : {
            'Less' : {'plot': R.TH1F('hLessLxySig'     +'_'+sample, ';L_{xy}/#sigma_{L_{xy}};Counts'                     , 100, 0., 50.            ), 'legName':'|#Delta#Phi| < #pi/2'},
            'More' : {'plot': R.TH1F('hMoreLxySig'     +'_'+sample, ';L_{xy}/#sigma_{L_{xy}};Counts'                     , 100, 0., 50.            ), 'legName':'|#Delta#Phi| > #pi/2'},
        },
        'LxySig-SplitDPhi-Big' : {
            'Less' : {'plot': R.TH1F('hLessLxySigBig'  +'_'+sample, ';L_{xy}/#sigma_{L_{xy}};Counts'                     ,  86, 6., 50.            ), 'legName':'|#Delta#Phi| < #pi/2'},
            'More' : {'plot': R.TH1F('hMoreLxySigBig'  +'_'+sample, ';L_{xy}/#sigma_{L_{xy}};Counts'                     ,  86, 6., 50.            ), 'legName':'|#Delta#Phi| > #pi/2'},
        },
        'LxySig-SplitDPhi-Edges' : {
            'Less' : {'plot': R.TH1F('hLessLxySigEdges'+'_'+sample, ';L_{xy}/#sigma_{L_{xy}};Counts'                     ,  86, 6., 50.            ), 'legName':'|#Delta#Phi| < #pi/2'},
            'More' : {'plot': R.TH1F('hMoreLxySigEdges'+'_'+sample, ';L_{xy}/#sigma_{L_{xy}};Counts'                     ,  86, 6., 50.            ), 'legName':'|#Delta#Phi| > #pi/2'},
        },
        'deltaPhi-SplitLxySig' : {
            'Less' : {'plot': R.TH1F('hLessDeltaPhi'   +'_'+sample, ';|#Delta#Phi|;Counts'                               , 100, 0., R.TMath.Pi()/2.), 'legName':'|#Delta#Phi| < #pi/2'},
            'More' : {'plot': R.TH1F('hMoreDeltaPhi'   +'_'+sample, ';|#Delta#Phi|;Counts'                               , 100, 0., R.TMath.Pi()/2.), 'legName':'|#Delta#Phi| > #pi/2'},
        },
        'deltaPhi-SplitLxySig-Big' : {
            'Less' : {'plot': R.TH1F('hLessDeltaPhiBig'+'_'+sample, ';|#Delta#Phi| for L_{xy}/#sigma_{L_{xy}} > 6;Counts', 100, 0., R.TMath.Pi()/2.), 'legName':'|#Delta#Phi| < #pi/2'},
            'More' : {'plot': R.TH1F('hMoreDeltaPhiBig'+'_'+sample, ';|#Delta#Phi| for L_{xy}/#sigma_{L_{xy}} > 6;Counts', 100, 0., R.TMath.Pi()/2.), 'legName':'|#Delta#Phi| > #pi/2'},
        },
    }

    singles[sample] = {
        'deltaPhi-Big' : {'plot': R.TH1F('hDeltaPhiBig'+'_'+sample, ';|#Delta#Phi| for L_{xy}/#sigma_{L_{xy}} > 6;Counts', 100, 0., R.TMath.Pi()   ), 'legName':''},
        'deltaPhi'     : {'plot': R.TH1F('hDeltaPhi'   +'_'+sample, ';|#Delta#Phi|;Counts'                               , 100, 0., R.TMath.Pi()   ), 'legName':''},
    }

boolMap = {True:'Less', False:'More'}

f = open(ARGS.FILE)
for line in f:
    cols = line.strip('\n').split()

    name     = cols[0]
    PdPhi    = float(cols[14])
    deltaPhi = float(cols[18])
    LxySig   = float(cols[15])
    sign     = cols[-1]

    if sign != 'OS': continue
    if PdPhi >= 1.: continue

    Less_DPhi = (deltaPhi <    R.TMath.Pi()/4.)
    More_DPhi = (deltaPhi > 3.*R.TMath.Pi()/4.)

    #Less_DPhi = (deltaPhi <    R.TMath.Pi()/2.)
    #More_DPhi = (deltaPhi >    R.TMath.Pi()/2.)

    More_LSig = (LxySig > ARGS.LXYSIGCUTOFF)

    weight = float(cols[4])

    if 'Data' in name:
        sample = 'Data'
    elif 'QCD' in name:
        sample = 'QCD20toInf-ME'
    else:
        sample = name

    foldedDeltaPhi = (0. if Less_DPhi else R.TMath.Pi()) + (1. if Less_DPhi else -1.) * deltaPhi

    if True:
        if True:
            singles[sample]['deltaPhi'                ]                    ['plot'].Fill(      deltaPhi, weight)
        if More_LSig:
            singles[sample]['deltaPhi-Big'            ]                    ['plot'].Fill(      deltaPhi, weight)

    if Less_DPhi or More_DPhi:
        if True:
            hists  [sample]['deltaPhi-SplitLxySig'    ][boolMap[Less_DPhi]]['plot'].Fill(foldedDeltaPhi, weight)
            hists  [sample]['LxySig-SplitDPhi'        ][boolMap[Less_DPhi]]['plot'].Fill(      LxySig  , weight)
        if More_LSig:
            hists  [sample]['deltaPhi-SplitLxySig-Big'][boolMap[Less_DPhi]]['plot'].Fill(foldedDeltaPhi, weight)
            hists  [sample]['LxySig-SplitDPhi-Big'    ][boolMap[Less_DPhi]]['plot'].Fill(      LxySig  , weight)

            if foldedDeltaPhi < 0.25:
                hists[sample]['LxySig-SplitDPhi-Edges'][boolMap[Less_DPhi]]['plot'].Fill(LxySig, weight)
f.close()

X = R.TFile.Open('roots/Hists.root' if int(ARGS.LXYSIGCUTOFF) == 6 else 'roots/Hists_{}.root'.format(int(ARGS.LXYSIGCUTOFF)), 'RECREATE')
for sample in hists:
    for key in hists[sample]:
        for which in hists[sample][key]:
            hists[sample][key][which]['plot'].Write()

    for key in singles[sample]:
        if True:
            singles[sample][key]['plot'].Write()
X.Close()
