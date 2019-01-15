import re, itertools
import DisplacedDimuons.Common.DataHandler as DH

##### Place the output of this script, "ZDSignalMCSamples.dat", in ../dat
##### It is required by the DataHandler library for signal samples
##### and therefore by Tupler and by Analysis

# gets HTo2LongLivedTo4mu and HTo2LongLivedTo2mu2jets dataset strings
AODDatasetStrings = DH.DASQueryList('dataset=/HTo2ZdTo2mu2x_MZd-*_Epsilon-*_TuneCUETP8M1_13TeV_pythia8/escalant-MC2016_HAHM_2Mu2x_Dec2018-AOD-v1-*/USER instance=prod/phys03')

# gets PAT Tuple datasets -- there may be many of these, and the regexes may have to be tweaked to be unique
PATDatasetStrings = DH.DASQueryList('dataset=/HTo2ZdTo2mu2x_MZd-*_Epsilon*_TuneCUETP8M1_13TeV_pythia8/stempl-MC2016_Hto2ZDto2mu2x_*_*_Jan2019-v1*/USER instance=prod/phys03')

# matches dataset string with four groups: mZD (digits 2), epsilon (form #e-0#), process string (\S*), weird hash ID (\w*)
# apply these to AODDatasetStrings
rxAOD = re.compile(r'/HTo2ZdTo2mu2x_MZd-(\d{2})_Epsilon-(\d{1}e-0\d{1})_\S*2Mu2x_(\S*)-(\w*)/USER')

# matches PAT Tupler dataset string with three groups: mZD (digits 2), epsilon (form #e-0#), process string (\S*), weird hash ID (\w*)
# apply these to PATDatasetStrings
rxPAT = re.compile(r'/HTo2ZdTo2mu2x_MZd-(\d{2})_Epsilon-(\d{1}e-0\d{1})_\S*/stempl-MC2016_\S*_Jan2019-v1-(\w*)/USER')

# fill a list with split up metadata that will be sorted
datasets = []
for ds in AODDatasetStrings:
    match = rxAOD.match(ds)
    mZD     = int(match.group(1))
    epsilon =     match.group(2)
    process =     match.group(3)
    ID      =     match.group(4)
    datasets.append(((mZD, epsilon), (process, ID, ds)))

for ds in PATDatasetStrings:
    match = rxPAT.match(ds)
    mZD     = int(match.group(1))
    epsilon =     match.group(2)
    ID      =     match.group(3)
    process = 'PAT'
    datasets.append(((mZD, epsilon), (process, ID, ds)))

datasets.sort(key=lambda x: x[0])

# write to file
f = open('ZDSignalMCSamples.dat', 'w')
for sp, group in itertools.groupby(datasets, lambda x: x[0]):
    mZD, epsilon = sp
    groupList = list(group)

    # write basic info
    f        .write('HTo2ZDTo2Mu2X'                     + '\n') # name
    f        .write('{} {}'.format(mZD, epsilon)        + '\n') # signal point

    # write nEvents
    for data in groupList:
        process, ID, ds = data[1]
        if process == 'PAT':
            fleList = DH.DASQueryList('file,lumi,events dataset={} instance=prod/phys03'.format(ds))
            nEvents = 0
            for rstring in fleList:
                cols = rstring.split()
                files = cols[0]
                l = map(int, cols[1].strip('[').strip(']').split(','))
                e = map(int, cols[2].strip('[').strip(']').split(','))
                nEvents += sum(e)
            f.write(str(nEvents)                        + '\n') # nEvents
            break

    # write PAT dataset, if any
    for data in groupList:
        process, ID, ds = data[1]
        if process == 'PAT':
            f.write(ds                                  + '\n') # PATTuple dataset
            break
    else:
        f    .write('_'                                 + '\n') # no PATTuple dataset

    # write all other datasets
    for data in groupList:
        process, ID, ds = data[1]
        if process == 'PAT': continue
        f    .write('PROCESS {} {}'.format(process, ds) + '\n') # process datasets

    # end of entry
    f        .write('-'                                 + '\n') # end of entry
f.close()
