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
    'DY100to200' :  '/DYJetsToLL_M-100to200_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/alfloren-MC2016_dy100To200-1f3b8c9856797cc8218eed4f9594f861/USER'
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
