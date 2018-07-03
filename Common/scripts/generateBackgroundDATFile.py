from DisplacedDimuons.PATFilter.MCSamples import samples

##### Place the output of this script, "BackgroundMCSamples.dat", in ../dat
##### It is required by the DataHandler library for background samples
##### and therefore by Tupler and by Analysis

# this script only uses MCSamples.py in PATFilter
# to sustainably regenerate BackgroundMCSamples.dat

# Note: at the moment, most of the Drell-Yan samples are commented out
# Therefore, rerunning this script will not regenerate the .dat file exactly
# Simply uncomment the samples in MCSamples.py to restore functionality

# Add PAT datasets here are they are generated
PATDatasets = {
    'DY100to200' : '/DYJetsToLL_M-100to200_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/alfloren-MC2016_dy100To200-1f3b8c9856797cc8218eed4f9594f861/USER',
    'DY10to50'   : '/DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/stempl-MC2016_dy10To50_Jun2018-v1-fc2578df0fe9569a82b5f2126d2d5c02/USER',
    'DY50toInf'  : '/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/stempl-MC2016_dy50ToInf_Jun2018-v1-fc2578df0fe9569a82b5f2126d2d5c02/USER',
    'tW'         : '/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/stempl-MC2016_tW_Jun2018-v1-fc2578df0fe9569a82b5f2126d2d5c02/USER',
    'tbarW'      : '/ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/stempl-MC2016_tbarW_Jun2018-v1-fc2578df0fe9569a82b5f2126d2d5c02/USER',
    'ttbar'      : '/TTTo2L2Nu_TuneCUETP8M2_ttHtranche3_13TeV-powheg-pythia8/stempl-MC2016_ttbar_Jun2018-v1-fc2578df0fe9569a82b5f2126d2d5c02/USER',
    'WW'         : '/WWTo2L2Nu_13TeV-powheg-herwigpp/stempl-MC2016_WW_Jun2018-v1-fc2578df0fe9569a82b5f2126d2d5c02/USER',
    'WJets'      : '/WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/stempl-MC2016_Wjets_Jun2018-v1-fc2578df0fe9569a82b5f2126d2d5c02/USER',
    'WZ'         : '/WZ_TuneCUETP8M1_13TeV-pythia8/stempl-MC2016_WZ_Jun2018-v1-fc2578df0fe9569a82b5f2126d2d5c02/USER',
    'WZ-ext'     : '/WZ_TuneCUETP8M1_13TeV-pythia8/stempl-MC2016_WZ_ext_Jun2018-v1-fc2578df0fe9569a82b5f2126d2d5c02/USER',
    'ZZ'         : '/ZZ_TuneCUETP8M1_13TeV-pythia8/stempl-MC2016_ZZ_Jun2018-v1-fc2578df0fe9569a82b5f2126d2d5c02/USER',
    'ZZ-ext'     : '/ZZ_TuneCUETP8M1_13TeV-pythia8/stempl-MC2016_ZZ_ext_Jun2018-v1-fc2578df0fe9569a82b5f2126d2d5c02/USER'
}

# build and write the output file
output = ''
for sample in reversed(samples):
    if sample.name.startswith('Hto2X'): break

    name         = sample.name
    AODDataset   = sample.dataset
    nEvents      = sample.nevents
    negFrac      = sample.f_neg_weights
    systFrac     = sample.syst_frac
    crossSection = sample.cross_section

    if name.startswith('dy'):
        name = name.replace('dy', 'DY')
        name = name.replace('To', 'to')
    if name == 'Wjets':
        name = 'WJets'
    if '_ext' in name:
        name = name.replace('_ext', '-ext')

    PATDataset = PATDatasets[name] if name in PATDatasets else '_'

    output += '''{NAME}
{AODDATASET}
{PATDATASET}
{NEVENTS:d}
{NEGFRAC}
{SYSTFRAC}
{CROSSSECTION}
-
'''.format(
        NAME         = name,
        AODDATASET   = AODDataset,
        PATDATASET   = PATDataset,
        NEVENTS      = nEvents,
        NEGFRAC      = negFrac,
        SYSTFRAC     = systFrac,
        CROSSSECTION = crossSection,
    )
open('BackgroundMCSamples.dat', 'w').write(output)
