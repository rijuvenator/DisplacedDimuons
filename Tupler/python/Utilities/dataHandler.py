import subprocess as bash
import os, re

#########################
# GENERAL DATASET TOOLS #
#########################

ROOT_PREFIX = 'root://cms-xrd-global.cern.ch/'

# das client wrapper functions
def DASQuery(query):
    try:
        return bash.check_output('dasgoclient -query="{}"'.format(query), shell=True).strip('\n')
    except bash.CalledProcessError as e:
        estring = ''
        if 'voms-proxy-init' in e.output:
            estring += '[DATAHANDLER ERROR]: did you forget to initialize your grid certificate?\n'
        estring += '[DATAHANDLER ERROR]: Error message from dasgoclient below\n\n'
        estring += e.output
        print estring
        exit()

def DASQueryList(query):
    return DASQuery(query).split('\n')

###################
# DATASET CLASSES #
###################

# regex patterns, compiled for ... speed?
PATTERNS = {
    # matches Drell-Yan MC "name" with two groups: mLow (digits 2-4) and mHigh (digits 3-4 OR "Inf")
    'DY_MBIN'    : re.compile(r'DY(\d{2,4})to(Inf|\d{3,4})'),
}

# class for storing information about data
# dataset is a dataset string from DAS: /*/*/*
# EDMDataset is for the EDM sample that produced the PAT Tuples
# PATDataset is for the PAT Tuples
# name is a short key that refers to the dataset
class Dataset(object):
    def __init__(self, name, EDMDataset, PATDataset):
        self.name        = name
        self.datasets    = {'PAT':PATDataset   , 'EDM':EDMDataset   }
        self.instances   = {'PAT':'prod/phys03', 'EDM':'prod/global'}
        self.files       = None
        self.isMC        = None

    # gets a list of files as strings
    # prefix: prepends something to each string (e.g. "file:")
    # dataset and instance: have complete control over the DAS query
    # force: by default if self.files is set, a DAS query will not be run again
    # set force to True to force a re-write of self.files
    def getFiles(self, prefix=None, dataset='PAT', instance='PAT', force=False):
        # set dataset: dataset can be "PAT", "EDM", some other key, or some other dataset
        if dataset in self.datasets:
            dataset = self.datasets[dataset]

        # make sure dataset is not _
        if dataset == '_':
            print '[DATAHANDLER ERROR]: Invalid dataset _, likely a PATTuple set not created yet'
            exit()

        # set instance: instance can be None, "PAT", "EDM", some other key, or some other dataset
        # probably prod/global or prod/phys03, or global or phys03
        if instance in self.instances:
            instance = self.instances[instance]
        if not instance.startswith('prod/'):
            instance = 'prod/' + instance

        # set self.files if it's not set or if force = True
        if not self.files or force:
            self.files = DASQueryList('file dataset={} instance={}'.format(dataset, instance))
            self.files.sort()

        # return list of files
        if prefix is None:
            return self.files
        else:
            return [prefix + fn for fn in self.files]

# derived class for any MC dataset
class MCSample(Dataset):
    def __init__(self, name, EDMDataset, PATDataset):
        Dataset.__init__(self, name, EDMDataset, PATDataset)

        self.isMC = True

# derived class for a background sample
# in this implementation, takes its input from a data file
# so all of the inputs are in that file, and the code for running over the file is below
class BackgroundSample(MCSample):
    def __init__(self, name, EDMDataset, PATDataset, nEvents, color, systFrac, crossSection, kFactor=1.):
        MCSample.__init__(self, name, EDMDataset, PATDataset)

        self.isSignal     = False
        self.nEvents      = int(nEvents)
        self.color        = int(color)
        self.systFrac     = float(systFrac)
        self.crossSection = float(crossSection)
        self.kFactor      = float(kFactor)
        self.isMadgraph   = 'amcatnlo' in self.datasets['EDM']

        if self.name.startswith('DY'):
            match = PATTERNS['DY_MBIN'].match(self.name)
            self.massRange = (int(match.group(1)), float('inf') if match.group(2) == 'Inf' else int(match.group(2)))

# derived class for a signal sample
# in this implementation, takes its input from a data file
# so all of the inputs are in that file, and the code for running over the file is below
class SignalSample(MCSample):
    def __init__(self, name, SP, PATDataset, *PROC):
        MCSample.__init__(self, name, '_', PATDataset)

        mH, mX, cTau = map(int, SP.split())

        self.isSignal    = True
        self.mH          = mH
        self.mX          = mX
        self.cTau        = cTau
        self.name        = self.name + '_' + '_'.join(map(str,(self.mH, self.mX, self.cTau)))

        # given a list of strings of the form "PROCESS <PROC> <DS>"
        # and make sure that no keys get overwritten!
        for arg in PROC:
            header, proc, ds = arg.split()
            if proc in self.datasets:
                if proc + '_OW1' not in self.datasets:
                    proc += '_OW1'
                else:
                    i = 1
                    while proc + '_OW' + str(i) in datasets:
                        i += 1
                    proc += '_OW' + str(i)
            self.datasets[proc] = ds
            self.instances[proc] = 'prod/phys03'
        assert len(PROC)+2 == len(self.datasets)
    
    def signalPoint(self):
        return (self.mH, self.mX, self.cTau)

# derived class for any data dataset
# in this implementation, takes its input from a data file
# so all of the inputs are in that file, and the code for running over the file is below
class DataSample(Dataset):
    def __init__(self, EDMDataset, PATDataset, name):
        Dataset.__init__(self, EDMDataset, PATDataset, name)

        self.isSignal = False
        self.isMC = False

###############
# GET SAMPLES #
###############

# get samples
# wrapped in a function so that it can be called from other scripts
# the success of this code relies on some *Samples.dat file
# having records separated by a - alone on a line, and
# having the positional arguments of the *Sample constructor 
# be in the same order as the records in *Samples.dat
# then the parameters are stored in a list, and can be unpacked with *
def getSamples(TYPE):
    VARS = {
        'HTo2X'        : {'FILE' : 'SignalMCSamples.dat'     , 'CLASS' : globals()['SignalSample'    ]},
        'BackgroundMC' : {'FILE' : 'BackgroundMCSamples.dat' , 'CLASS' : globals()['BackgroundSample']},
        'Data'         : {'FILE' : 'DataSamples.dat'         , 'CLASS' : globals()['DataSample'      ]}
    }
    FILE  = VARS[TYPE]['FILE' ]
    CLASS = VARS[TYPE]['CLASS']

    f = open(os.path.join(os.environ['CMSSW_BASE'], 'src/DisplacedDimuons/Tupler/dat/'+FILE))
    Parameters = []
    Entry = []
    for line in f:
        if line == '-\n':
            Parameters.append(list(Entry))
            Entry = []
            continue
        Entry.append(line.strip('\n'))
    f.close()
    
    samples = [CLASS(*Entry) for Entry in Parameters]
    return samples


# aliased wrapper for convenience
# get HTo2LongLivedTo4mu MC samples
def getHTo2XTo4MuSamples():
    return [s for s in getSamples('HTo2X') if s.name.startswith('HTo2XTo4Mu')]

# get HTo2LongLivedTo2mu2jets MC samples
def getHTo2XTo2Mu2JSamples():
    return [s for s in getSamples('HTo2X') if s.name.startswith('HTo2XTo2Mu2J')]

# aliased wrapper for convenience
# get background MC samples
def getBackgroundSamples():
    return getSamples('BackgroundMC')

# aliased wrapper for convenience
# get data samples
def getDataSamples():
    return getSamples('Data')

######################
# RUN AS MAIN MODULE #
######################

if __name__ == '__main__':

    print '\n\033[32m-----HTO2XTO4MU SIGNAL SAMPLES-----\n\033[m'
    HTo2XTo4MuSamples = getHTo2XTo4MuSamples()
    for ds in HTo2XTo4MuSamples:
        for process in ds.datasets:
            if 'AOD' in process:
                print process, ds.signalPoint()
                print '   ', ds.getFiles(dataset=process, instance='phys03')[0]

    print '\n\033[32m-----HTO2XTO2MU2J SIGNAL SAMPLES-----\n\033[m'
    HTo2XTo2Mu2JSamples = getHTo2XTo2Mu2JSamples()
    for ds in HTo2XTo2Mu2JSamples:
        for process in ds.datasets:
            if 'AOD' in process:
                print process, ds.signalPoint()
                print '   ', ds.getFiles(dataset=process, instance='phys03')[0]
    
    print '\n\033[32m-----BACKGROUND MC SAMPLES-----\n\033[m'
    BackgroundSamples = getBackgroundSamples()
    for ds in BackgroundSamples:
        print ds.name, ds.crossSection
        print '   ', ds.getFiles(dataset='EDM', instance='global')[0]

    print '\n\033[32m-----DATA SAMPLES-----\n\033[m'
    DataSamples = getDataSamples()
    for ds in DataSamples:
        print ds.name
        print '   ', ds.getFiles(dataset='PAT', instance='phys03')[0]
