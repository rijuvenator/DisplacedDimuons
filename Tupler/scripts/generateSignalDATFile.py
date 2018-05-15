import re, itertools
import DisplacedDimuons.Tupler.Utilities.dataHandler as DH

##### Place the output of this script, "SignalMCSamples.dat", in ../dat
##### It is required by the dataHandler library for signal samples
##### and therefore everything else in the ../python directory

# gets HTo2LongLivedTo4mu and HTo2LongLivedTo2mu2jets dataset strings
DatasetStrings = DH.DASQueryList('dataset=/HTo2LongLivedTo*_MH-*_MFF-*_CTau-*/escalant*/* instance=prod/phys03')

# matches dataset string with six groups: final state (4mu or 2mu2jets), mH, mX, cTau (digits 1-4), process string (\S*), weird hash ID (\w*)
rx = re.compile(r'/HTo2LongLivedTo(4mu|2mu2jets)_MH-(\d{1,4})_MFF-(\d{1,4})_CTau-(\d{1,4})mm\S*pythia8_(\S*)-(\w*)/USER')

# fill a list with split up metadate that will be sorted
datasets = []
for ds in DatasetStrings:
    match = rx.match(ds)
    FS      =     match.group(1)
    mH      = int(match.group(2))
    mX      = int(match.group(3))
    cTau    = int(match.group(4))
    process =     match.group(5)
    ID      =     match.group(6)
    datasets.append(((mH, mX, cTau, FS), (process, ID, ds)))
datasets.sort(key=lambda x: x[0])

# write to file
f = open('SignalMCSamples.dat', 'w')
for sp, group in itertools.groupby(datasets, lambda x: x[0]):
    mH, mX, cTau, FS = sp
    if   FS == '4mu'     : FS = '4Mu'
    elif FS == '2mu2jets': FS = '2Mu2J'
    f    .write('HTo2XTo'+FS                        + '\n') # name
    f    .write('{} {} {}'.format(mH, mX, cTau)     + '\n') # signal point
    f    .write('_'                                 + '\n') # PATTuple dataset
    for data in group:
        process, ID, ds = data[1]
        f.write('PROCESS {} {}'.format(process, ds) + '\n') # process datasets
    f    .write('-'                                 + '\n') # end of entry
f.close()
