import subprocess as bash
import os, re
import DisplacedDimuons.Common.Constants as Constants

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
    # matches Drell-Yan MC "name" with two groups: mLow (digits 2-4) and mHigh (digits 2-4 OR "Inf")
    'DY_MBIN'    : re.compile(r'DY(\d{2,4})to(Inf|\d{2,4})'),
    # matches QCD MC "name" with three groups: ptLow (digits 2), ptHigh (digits 2-3 OR "Inf"), and possibly -ME
    'QCD_MBIN'   : re.compile(r'QCD(\d{2})to(Inf|\d{2,3})(-ME)*'),
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
            print '[DATAHANDLER ERROR]: Invalid dataset _, likely a PATTuple set not created yet. Please try --aodonly for sample', self.name
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

    # set nTuple info
    def setNTupleInfo(self, key):
        try:
            self.nTupleInfo = NTUPLEDICT[key]
        except:
            self.nTupleInfo = '_'
            return

        # validate nTupleInfo now
        # see getNTuples for handling this info
        NTUPLEERRORSTRING = '''[DATAHANDLER ERROR]: NTuples.dat must be a list of strings of one of the following formats:
                     - <FILE>.root
                     - <FILE1>.root <FILE2>.root ...
                     - <FILE>.root NFILES
                     - <FILE>.root N1 N2
'''
        if type(self.nTupleInfo) == str:
            return
        else:
            if '.root' in self.nTupleInfo[1]:
                return
            elif len(self.nTupleInfo) == 2:
                try:
                    int(self.nTupleInfo[1])
                except:
                    raise Exception(NTUPLEERRORSTRING)
                return
            elif len(self.nTupleInfo) == 3:
                try:
                    int(self.nTupleInfo[1])
                    int(self.nTupleInfo[2])
                except:
                    raise Exception(NTUPLEERRORSTRING)
                return
            raise Exception(NTUPLEERRORSTRING)


    # get list of nTuple files
    def getNTuples(self):
        # if nTupleInfo (from NTuples.dat) is just a string,
        # assume there is just 1 file and return the string
        # add a root protocol if we are not on lxplus or on a CONDOR worker
        # (TODO: generalize)
        if type(self.nTupleInfo) == str:
            if 'cern.ch' in os.environ['HOSTNAME']:
                return self.nTupleInfo
            else:
                return Constants.PREFIX_CERN + self.nTupleInfo

        # if nTupleInfo is a list, we have a few options
        # - if it's a list of .root files, i.e. [1] is something.root,
        #   return the entire list as a list of strings
        # - if it's a string (file.root) and 1 integer N
        #   assume you want a list [file_1.root, ... file_N.root]
        # - if it's a string (file.root) and 2 integers N1 N2
        #   assume you want a list [file_N1.root, ... file_N2.root]
        # otherwise, raise an error
        else:
            if '.root' in self.nTupleInfo[1]:
                return self.nTupleInfo
            elif len(self.nTupleInfo) == 2:
                template = self.nTupleInfo[0].replace('.root', '_{}.root')
                N = int(self.nTupleInfo[1])
                return [template.format(i) for i in xrange(1, N+1)]
            elif len(self.nTupleInfo) == 3:
                template = self.nTupleInfo[0].replace('.root', '_{}.root')
                N1 = int(self.nTupleInfo[1])
                N2 = int(self.nTupleInfo[2])
                return [template.format(i) for i in xrange(N1, N2+1)]

# derived class for any MC dataset
class MCSample(Dataset):
    def __init__(self, name, EDMDataset, PATDataset):
        Dataset.__init__(self, name, EDMDataset, PATDataset)

        self.isMC = True

# derived class for a background sample
# in this implementation, takes its input from a data file
# so all of the inputs are in that file, and the code for running over the file is below
class BackgroundSample(MCSample):
    def __init__(self, name, EDMDataset, PATDataset, nEvents, negFrac, systFrac, crossSection, kFactor=1.):
        MCSample.__init__(self, name, EDMDataset, PATDataset)

        self.isSignal     = False
        self.nEvents      = int(nEvents)
        self.negFrac      = float(negFrac)
        self.systFrac     = float(systFrac)
        self.crossSection = float(crossSection)
        self.kFactor      = float(kFactor)
        self.isMadgraph   = 'amcatnlo' in self.datasets['EDM']

        if self.name.startswith('DY'):
            match = PATTERNS['DY_MBIN'].match(self.name)
            self.massRange = (int(match.group(1)), float('inf') if match.group(2) == 'Inf' else int(match.group(2)))

        if self.name.startswith('QCD'):
            match = PATTERNS['QCD_MBIN'].match(self.name)
            self.pTRange = (int(match.group(1)), float('inf') if match.group(2) == 'Inf' else int(match.group(2)))

        # set nTuple info
        self.setNTupleInfo(self.name)

# derived class for a signal sample
# in this implementation, takes its input from a data file
# so all of the inputs are in that file, and the code for running over the file is below
class SignalSample(MCSample):
    def __init__(self, name, SP, nEvents, PATDataset, *PROC):
        MCSample.__init__(self, name, '_', PATDataset)

        mH, mX, cTau = map(int, SP.split())

        self.nEvents     = int(nEvents)
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

        # set nTuple info
        # note, at this point, self.name is HTo2XTo(FS)_(SP)
        self.setNTupleInfo(self.name)

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

        # set nTuple info
        self.setNTupleInfo(self.name)

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

    f = open(os.path.join(os.environ['CMSSW_BASE'], 'src/DisplacedDimuons/Common/dat/'+FILE))
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

# aliased wrapper for convenience
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

# aliased wrapper for convenience
# get all samples, return as dictionary
def getAllSamples():
    return {s.name:s for s in getHTo2XTo4MuSamples() + getHTo2XTo2Mu2JSamples() + getBackgroundSamples() + getDataSamples()}

# get NTuple info
# this loads the information in NTuples.dat into a dictionary at module level
# then all the samples reference it
def getNTuples():
    f = open(os.path.join(os.environ['CMSSW_BASE'], 'src/DisplacedDimuons/Common/dat/NTuples.dat'))
    nTupleDict = {}
    for line in f:
        cols = line.strip('\n').split()
        name = cols[0]
        rest = cols[1:] if len(cols) > 2 else cols[1]
        nTupleDict[name] = rest
    f.close()
    return nTupleDict
NTUPLEDICT = getNTuples()

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
        print '   ', ds.nTupleInfo

    print '\n\033[32m-----HTO2XTO2MU2J SIGNAL SAMPLES-----\n\033[m'
    HTo2XTo2Mu2JSamples = getHTo2XTo2Mu2JSamples()
    for ds in HTo2XTo2Mu2JSamples:
        for process in ds.datasets:
            if 'AOD' in process:
                print process, ds.signalPoint()
                print '   ', ds.getFiles(dataset=process, instance='phys03')[0]
        print '   ', ds.nTupleInfo

    print '\n\033[32m-----BACKGROUND MC SAMPLES-----\n\033[m'
    BackgroundSamples = getBackgroundSamples()
    for ds in BackgroundSamples:
        print ds.name, ds.crossSection
        print '   ', ds.getFiles(dataset='EDM', instance='global')[0]
        print '   ', ds.nTupleInfo

    print '\n\033[32m-----DATA SAMPLES-----\n\033[m'
    DataSamples = getDataSamples()
    for ds in DataSamples:
        print ds.name
        print '   ', ds.getFiles(dataset='PAT', instance='phys03')[0]
        print '   ', ds.nTupleInfo
