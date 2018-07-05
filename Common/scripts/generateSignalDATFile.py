import re, itertools
import DisplacedDimuons.Common.DataHandler as DH

##### Place the output of this script, "SignalMCSamples.dat", in ../dat
##### It is required by the DataHandler library for signal samples
##### and therefore by Tupler and by Analysis

# gets HTo2LongLivedTo4mu and HTo2LongLivedTo2mu2jets dataset strings
AODDatasetStrings = DH.DASQueryList('dataset=/HTo2LongLivedTo*_MH-*_MFF-*_CTau-*/escalant*/* instance=prod/phys03')

# gets PAT Tuple datasets -- there may be many of these, and the regexes may have to be tweaked to be unique
#PATDatasetStrings = DH.DASQueryList('dataset=/HTo2LongLivedTo*_MH-*_MFF-*_CTau-*/adasgupt-MC2016_*/* instance=prod/phys03')
PATDatasetStrings = DH.DASQueryList('dataset=/HTo2LongLivedTo*_MH-*_MFF-*_CTau-*/stempl-MC2016_*Jun2018-v1*/* instance=prod/phys03')

# matches dataset string with six groups: final state (4mu or 2mu2jets), mH, mX, cTau (digits 1-4), process string (\S*), weird hash ID (\w*)
# apply these to AODDatasetStrings
rxAOD = re.compile(r'/HTo2LongLivedTo(4mu|2mu2jets)_MH-(\d{1,4})_MFF-(\d{1,4})_CTau-(\d{1,4})mm\S*pythia8_(\S*)-(\w*)/USER')

# matches PAT Tupler dataset string with five groups: final state (4mu or 2mu2jets), mH, mX, cTau (digits 1-4), weird hash ID (\w*)
# apply these to PATDatasetStrings
#rxPAT = re.compile(r'/HTo2LongLivedTo(4mu|2mu2jets)_MH-(\d{1,4})_MFF-(\d{1,4})_CTau-(\d{1,4})mm\S*pythia8/adasgupt-MC2016_\S*-(\w*)/USER')
rxPAT = re.compile(r'/HTo2LongLivedTo(4mu|2mu2jets)_MH-(\d{1,4})_MFF-(\d{1,4})_CTau-(\d{1,4})mm\S*pythia8/stempl-MC2016_\S*_Jun2018-v1-(\w*)/USER')

# fill a list with split up metadata that will be sorted
datasets = []
for ds in AODDatasetStrings:
    match = rxAOD.match(ds)
    FS      =     match.group(1)
    mH      = int(match.group(2))
    mX      = int(match.group(3))
    cTau    = int(match.group(4))
    process =     match.group(5)
    ID      =     match.group(6)
    datasets.append(((mH, mX, cTau, FS), (process, ID, ds)))

for ds in PATDatasetStrings:
    match = rxPAT.match(ds)
    FS      =     match.group(1)
    mH      = int(match.group(2))
    mX      = int(match.group(3))
    cTau    = int(match.group(4))
    ID      =     match.group(5)
    process = 'PAT'
    datasets.append(((mH, mX, cTau, FS), (process, ID, ds)))

datasets.sort(key=lambda x: x[0])

# write to file
f = open('SignalMCSamples.dat', 'w')
for sp, group in itertools.groupby(datasets, lambda x: x[0]):
    mH, mX, cTau, FS = sp
    groupList = list(group)

    # set capitalized FS
    if   FS == '4mu'     : FS = '4Mu'
    elif FS == '2mu2jets': FS = '2Mu2J'

    # write basic info
    f        .write('HTo2XTo'+FS                        + '\n') # name
    f        .write('{} {} {}'.format(mH, mX, cTau)     + '\n') # signal point

    # write nEvents
    for data in groupList:
        process, ID, ds = data[1]
        if process == 'May2018-AOD-v1':
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