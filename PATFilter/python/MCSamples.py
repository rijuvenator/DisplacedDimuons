#!/usr/bin/env python

import os
from DisplacedDimuons.PATFilter.tools import files_from_dbs
#from SUSYBSMAnalysis.Zprime2muAnalysis.crabtools import dataset_from_publish_log

class sample(object):
    def __init__(self, name, nice_name, dataset, nevents, color, syst_frac, cross_section, k_factor=1, filenames=None, scheduler='condor', hlt_process_name='HLT', ana_dataset=None, is_madgraph=False, is_signal=False):
        self.name = name
        self.nice_name = nice_name
        self.dataset = dataset
        self.nevents = nevents
        self.color = color
        self.syst_frac = syst_frac
        self.cross_section = cross_section
        self.k_factor = k_factor
        self.filenames_ = filenames
        self.scheduler = scheduler
        self.hlt_process_name = hlt_process_name
        self.ana_dataset = ana_dataset
        self.is_madgraph = is_madgraph
        self.is_signal = is_signal

    @property
    def partial_weight(self):
        return self.cross_section / float(self.nevents) * self.k_factor # the total weight is partial_weight * integrated_luminosity

    @property
    def filenames(self):
        # Return a list of filenames for running the histogrammer not
        # using crab.
        if self.filenames_ is not None:
            return self.filenames_
        return files_from_dbs(self.ana_dataset, ana02=True)

    def __getitem__(self, key):
        return getattr(self, key)

    def _dump(self, redump_existing=False):
        dst = os.path.join('/uscmst1b_scratch/lpc1/3DayLifetime/tucker', self.name) 
        os.system('mkdir ' + dst)
        for fn in self.filenames:
            print fn
            if redump_existing or not os.path.isfile(os.path.join(dst, os.path.basename(fn))):
                os.system('dccp ~%s %s/' % (fn,dst))

class tupleonlysample(sample):
    def __init__(self, name, dataset, scheduler='condor', hlt_process_name='HLT'):
        super(tupleonlysample, self).__init__(name, 'dummy', dataset, 1, 1, 1, 1, scheduler=scheduler, hlt_process_name=hlt_process_name)

samples = [
    # Dimuon Drell-Yan POWHEG samples; cross sections are from POWHEG (RunIIWinter15GS campaign)
# ### K factor for Drell-Yan samples is the ratio of the NNLO to POWHEG cross sections for M > 20 GeV bin, 1915/1871=1.024
#    sample('dy50to120',   'DY50to120',    '/ZToMuMu_NNPDF30_13TeV-powheg_M_50_120/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM',   2977600, 209, 1., 1975., k_factor=1.), # Latest FEWZ x-sec is 1921.8 pb
#    sample('dy120to200',  'DY120to200',   '/ZToMuMu_NNPDF30_13TeV-powheg_M_120_200/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM',   100000, 210, 1., 19.32, k_factor=1.),
#    sample('dy200to400',  'DY200to400',   '/ZToMuMu_NNPDF30_13TeV-powheg_M_200_400/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM',   100000, 211, 1., 2.731, k_factor=1.),
#    sample('dy400to800',  'DY400to800',   '/ZToMuMu_NNPDF30_13TeV-powheg_M_400_800/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM',    98400, 212, 1., 0.241, k_factor=1.),
#    sample('dy800to1400', 'DY800to1400',  '/ZToMuMu_NNPDF30_13TeV-powheg_M_800_1400/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM',  100000,  72, 1., 0.01678, k_factor=1.),
#    sample('dy1400to2300','DY1400to2300', '/ZToMuMu_NNPDF30_13TeV-powheg_M_1400_2300/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM',  95106,  70, 1., 0.00139, k_factor=1.),
#    sample('dy2300to3500','DY2300to3500', '/ZToMuMu_NNPDF30_13TeV-powheg_M_2300_3500/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM', 100000,  70, 1., 0.00008948, k_factor=1.),
#    #- cross-sections too small to matter
#    sample('dy3500to4500','DY3500to4500', '/ZToMuMu_NNPDF30_13TeV-powheg_M_3500_4500/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM', 100000,  70 , 1., 0.000004135, k_factor=1.),
#    sample('dy4500to6000','DY4500to6000', '/ZToMuMu_NNPDF30_13TeV-powheg_M_4500_6000/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM', 100000,  70 , 1., 4.56E-7, k_factor=1.),
#    sample('dy6000toInf', 'DY6000toInf',  '/ZToMuMu_NNPDF30_13TeV-powheg_M_6000_Inf/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM',  100000,  70 , 1., 2.066E-8, k_factor=1.),

    # Dilepton Drell-Yan aMC@NLO samples (including tautau); cross sections are from XSDB (i.e., from aMC@NLO)
    # Nevents below is the real number of events; no scaling is done
# ### 	N_EVENT scaled by: -N_EVENT * n_neg/n + n * n_pos/n (N_EVENT from report = 28968252; n from weight = 9112991 n_neg = 1507200 (0.1654); n_pos = 7605790 (0.8346); )
#    sample('dy10To50',     'DY10to50',     '/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM',        30935823, 209, 1., 18810.,  k_factor=1., is_madgraph=True),
    sample('dy50ToInf',    'DY50toInf',    '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v1/AODSIM',      122547040, 209, 1., 5941.,   k_factor=1., is_madgraph=True), # In the Z' code, Nevents used to be 19385554
    sample('dy100To200',   'DY100To200',   '/DYJetsToLL_M-100to200_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/AODSIM',  1083606, 209, 1., 226.6,   k_factor=1., is_madgraph=True),
    sample('dy200To400',   'DY200to400',   '/DYJetsToLL_M-200to400_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext2-v2/AODSIM',   298679, 209, 1., 7.77,    k_factor=1., is_madgraph=True),
    sample('dy400To500',   'DY400to500',   '/DYJetsToLL_M-400to500_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/AODSIM',   287262, 209, 1., 0.4065,  k_factor=1., is_madgraph=True),
    sample('dy500To700',   'DY500to700',   '/DYJetsToLL_M-500to700_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/AODSIM',   280940, 209, 1., 0.2334,  k_factor=1., is_madgraph=True),
    sample('dy700To800',   'DY700to800',   '/DYJetsToLL_M-700to800_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/AODSIM',   276235, 209, 1., 0.03614, k_factor=1., is_madgraph=True),
    sample('dy800To1000',  'DY800to1000',  '/DYJetsToLL_M-800to1000_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/AODSIM',  271768, 209, 1., 0.03047, k_factor=1., is_madgraph=True),
    sample('dy1000To1500', 'DY1000to1500', '/DYJetsToLL_M-1000to1500_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/AODSIM', 258620, 209, 1., 0.01636, k_factor=1., is_madgraph=True),
    sample('dy1500To2000', 'DY1500to2000', '/DYJetsToLL_M-1500to2000_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/AODSIM', 258625, 209, 1., 0.00218, k_factor=1., is_madgraph=True),
    sample('dy2000To3000', 'DY2000to3000', '/DYJetsToLL_M-2000to3000_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/AODSIM', 255342, 209, 1., 0.0005156, k_factor=1., is_madgraph=True),

    sample('WZ',     'WZ',     '/WZ_TuneCUETP8M1_13TeV-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM',      1000000,  98, 1., 47.13, k_factor=1.), #NLO from MCFM (Source?? xsdb x-sec is 23.43 pb)
    sample('WZ_ext', 'WZ_ext', '/WZ_TuneCUETP8M1_13TeV-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/AODSIM', 2997571,  98, 1., 47.13, k_factor=1.),

    sample('ZZ',     'ZZ',     '/ZZ_TuneCUETP8M1_13TeV-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM',       990064,  94, 1., 16.523, k_factor=1.), #NLO from MCFM (Source? xsdb x-sec is 10.16 pb)
    sample('ZZ_ext', 'ZZ_ext', '/ZZ_TuneCUETP8M1_13TeV-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/AODSIM',  998034,  94, 1., 16.523, k_factor=1.),

    sample('WW',     'WW',     '/WWTo2L2Nu_13TeV-powheg-herwigpp/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM',    1999000, 208, 1., 12.178, k_factor=1.), #already NNLO xs (Source? xsdb x-sec is 10.48 pb)
    #- mass-bin samples likely not needed? (Don't know where the x-sections came from)
#    sample('WW200to600',   'WW200to600',   '/WWTo2L2Nu_Mll_200To600_13TeV-powheg/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM',   200000, 208, 1., 1.385, k_factor=1.), # already NNLO xs
#    sample('WW600to1200',  'WW600to1200',  '/WWTo2L2Nu_Mll_600To1200_13TeV-powheg/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM',  200000, 208, 1., 0.0566, k_factor=1.), #already NNLO xs
#    sample('WW1200to2500', 'WW1200to2500', '/WWTo2L2Nu_Mll_1200To2500_13TeV-powheg/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM', 200000, 208, 1., 0.003557, k_factor=1.), #already NNLO xs
#    sample('WW2500toInf',  'WW2500toInf',  '/WWTo2L2Nu_Mll_2500ToInf_13TeV-powheg/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM',   38969, 208, 1., 0.00005395, k_factor=1.), #already NNLO xs

    sample('ttbar', 'ttbar', '/TTTo2L2Nu_TuneCUETP8M2_ttHtranche3_13TeV-powheg-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM', 79140880, 4, 1., 87.31, k_factor=1.), # Source? xsdb x-sec is 76.7 pb
    #- mass-bin samples likely not needed? (Don't know where the x-sections came from)
#    sample('ttbar_500to800',  'ttbar_500to800',    '/TTToLL_MLL_500To800_TuneCUETP8M1_13TeV-powheg-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM', 200000, 4 , 1., 0.32611, k_factor=1.),
#    sample('ttbar_800to1200',  'ttbar_800to1200',  '/TTToLL_MLL_800To1200_TuneCUETP8M1_13TeV-powheg-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM', 199800, 4 , 1., 0.03265, k_factor=1.),
#    sample('ttbar_1200to1800', 'ttbar_1200to1800', '/TTToLL_MLL_1200To1800_TuneCUETP8M1_13TeV-powheg-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM', 200000, 4 , 1., 0.00305, k_factor=1.),
#    sample('ttbar_1800toInf',  'ttbar_1800toInf',  '/TTToLL_MLL_1800ToInf_TuneCUETP8M1_13TeV-powheg-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM', 40829, 4 , 1., 0.00017, k_factor=1.),

    # Single-top cross sections are NNLO from https://twiki.cern.ch/twiki/bin/view/LHCPhysics/SingleTopRefXsec
    sample('tW', 'tW', '/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/AODSIM', 6952830, 66, 1., 35.8, k_factor=1.), # xsdb x-sec is 38.09 pb
    sample('tbarW', 'tbarW', 'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/AODSIM', 6933094, 63, 1., 35.8, k_factor=1.), # xsdb x-sec is 38.06

    # For W+jets, there also exist extensions and aMC@NLO samples
    sample('Wjets', 'Wjets', '/WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM', 29804825, 52, 1., 61526.7, k_factor=1.), #already NNLO xs (Source? xsdb number is 50260 pb)
    # For QCD, there are also MuEnrichedPt5 and inclusive samples in pT bins
    sample('QCD', 'QCD', '/QCD_Pt-20toInf_MuEnrichedPt15_TuneCUETP8M1_13TeV_pythia8/RunIISummer16DR80Premix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/AODSIM', 22094081, 43, 1., 269900., k_factor=1.)
    ]

samples.reverse()

for sample in samples:
   exec '%s = sample' % sample.name
   sample.ana_dataset = '/%s/rradogna-datamc_%s-c4b4ec8fa143ea00cec443e9d0afb38f/USER'  % (sample.dataset.split('/')[1], sample.name)

#dy100to200.ana_dataset = '/DYJetsToLL_M-100to200_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/rradogna-datamc_dy100to200-1e36332d8badf10b79a5027340f46eb1/USER'

__all__ = ['samples'] + [s.name for s in samples]


if __name__ == '__main__':
    if False:
        from dbstools import dbsparents
        for s in samples:
            print s.dataset
            parents = dbsparents(s.dataset)
            for parent in parents:
                for line in os.popen('dbss rel %s' % parent):
                    if 'CMSSW' in line:
                        print parent, line,
            print

    if False:
        import os
        from dbstools import dbsparents
        for s in [ww,wz,zz]:
            print s.dataset
            parents = dbsparents(s.dataset)
            print parents
            os.system('dbsconfig %s > %s' % (parents[-1], s.name))

        os.system('dbss nevents %s' % x.replace('RECO','RAW'))
        os.system('dbss nevents %s' % x)

    if False:
        import os
        from dbstools import dbsparents
        for s in samples:
            print s.dataset
            def fuf(y):
                x = os.popen(y).read()
                for line in x.split('\n'):
                    try:
                        print int(line)
                    except ValueError:
                        pass
            fuf('dbss nevents %s' % s.dataset)
            fuf('dbss nevents %s' % s.dataset.replace('AODSIM','GEN-SIM-RECO'))

    if False:
        for s in samples:
            print s.name
            os.system('grep "total events" ~/nobackup/crab_dirs/384p3/publish_logs/publish.crab_datamc_%s' % s.name)
            os.system('grep "total events" ~/nobackup/crab_dirs/413p2/publish_logs/publish.crab_datamc_%s' % s.name)
            print

    if False:
        os.system('mkdir ~/scratch/wjets')
        for fn in wjets.filenames:
            assert fn.startswith('/store')
            fn = '/pnfs/cms/WAX/11' + fn
            cmd = 'dccp %s ~/scratch/wjets/' % fn
            print cmd
            os.system(cmd)

    if False:
        for s in samples:
            print s.name
            os.system('dbss site %s' % s.dataset)
            print

    if False:
        for s in samples:
            if s.ana_dataset is None:
                continue
            c = []
            for line in os.popen('dbss ana02 find file.numevents where dataset=%s' % s.ana_dataset):
                try:
                    n = int(line)
                except ValueError:
                    continue
                c.append(n)
            c.sort()
            print s.name, c
