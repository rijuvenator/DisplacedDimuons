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
		if 'voms-proxy-init' in e.output:
			print '[DATAHANDLER ERROR]: did you forget to initialize your grid certificate?'
		print '[DATAHANDLER ERROR]: Error message from dasgoclient below\n'
		print e.output
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
	# matches dataset string with five groups: mH, mX, cTau (digits 1-4), process string (\S*), weird hash ID (\w*)
	'HTo2XTo4Mu' : re.compile(r'/HTo2LongLivedTo4mu_MH-(\d{1,4})_MFF-(\d{1,4})_CTau-(\d{1,4})mm\S*pythia8_(\S*)-(\w*)/USER')
}

# class for storing information about data
# dataset is a dataset string from DAS: /*/*/*
# AODDataset is for the AOD sample that produced the PAT Tuples
# PATDataset is for the PAT Tuples
# name is a short key that refers to the dataset
class Dataset(object):
	def __init__(self, AODDataset, PATDataset, name):
		self.AODDataset  = AODDataset
		self.PATDataset  = PATDataset
		self.name        = name
		self.files       = None
		self.isMC        = None
		self.AODInstance = 'prod/global'
		self.PATInstance = 'prod/phys03'

	# gets a list of files as strings
	# prefix: prepends something to each string (e.g. "file:")
	# dataset and instance: have complete control over the DAS query
	# force: by default if self.files is set, a DAS query will not be run again
	# set force to True to force a re-write of self.files
	def getFiles(self, prefix=None, dataset=None, instance=None, force=False):
		# set dataset: dataset can be None, "PAT", "AOD", or some other string
		if dataset is None:
			dataset = self.PATDataset
		else:
			try:
				dataset = getattr(self, dataset + 'Dataset')
			except:
				pass

		# set instance: instance can be None, "PAT", "AOD", or some other string
		# probably prod/global or prod/phys03, or global or phys03
		if instance is None:
			instance = self.PATInstance
		else:
			try:
				instance = getattr(self, instance + 'Instance')
			except:
				pass
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
	def __init__(self, AODDataset, PATDataset, name):
		Dataset.__init__(self, AODDataset, PATDataset, name)
		self.isMC = True

# derived class for a background sample
# in this implementation, takes its input from a data file
# so all of the inputs are in that file, and the code for running over the file is below
class BackgroundSample(MCSample):
	def __init__(self, AODDataset, PATDataset, name, nEvents, color, systFrac, crossSection, kFactor=1.):
		MCSample.__init__(self, AODDataset, PATDataset, name)
		self.isSignal     = False
		self.nEvents      = int(nEvents)
		self.color        = int(color)
		self.systFrac     = float(systFrac)
		self.crossSection = float(crossSection)
		self.kFactor      = float(kFactor)
		self.isMadgraph   = 'amcatnlo' in self.AODDataset

		if self.name.startswith('DY'):
			match = PATTERNS['DY_MBIN'].match(self.name)
			self.massRange = (int(match.group(1)), float('inf') if match.group(2) == 'Inf' else int(match.group(2)))

# derived class for a signal sample
# in this implementation, takes its input from a data file
# so all of the inputs are in that file, and the code for running over the file is below
class SignalSample(MCSample):
	def __init__(self, AODDataset, PATDataset, name):
		MCSample.__init__(self, AODDataset, PATDataset, name)
		self.isSignal = True

		if self.name.startswith('HTo2XTo4Mu'):
			match = PATTERNS['HTo2XTo4Mu'].match(self.AODDataset)

			self.AODInstance = 'prod/phys03'
			self.mH          = int(match.group(1))
			self.mX          = int(match.group(2))
			self.cTau        = int(match.group(3))
			self.process     =     match.group(4)
			self.ID          =     match.group(5)

			self.name = 'HTo2XTo4Mu' + '_'.join(map(str,(self.mH, self.mX, self.cTau)))
	
	def signalPoint(self):
		if self.name.startswith('HTo2XTo4Mu'):
			return (self.mH, self.mX, self.cTau)

# derived class for any data dataset
# in this implementation, takes its input from a data file
# so all of the inputs are in that file, and the code for running over the file is below
class DataSample(Dataset):
	def __init__(self, AODDataset, PATDataset, name):
		Dataset.__init__(self, AODDataset, PATDataset, name)
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
		'HTo2XTo4Mu'   : {'FILE' : 'HTo2XTo4MuSignalMCSamples.dat', 'CLASS' : globals()['SignalSample'    ]},
		'BackgroundMC' : {'FILE' : 'BackgroundMCSamples.dat'      , 'CLASS' : globals()['BackgroundSample']},
		'Data'         : {'FILE' : 'DataSamples.dat'              , 'CLASS' : globals()['DataSample'      ]}
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
	return getSamples('HTo2XTo4Mu')

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
		if 'AOD' in ds.process:
			print ds.process, ds.signalPoint()
			print '   ', ds.getFiles(dataset='AOD', instance='phys03')[0]
	
	print '\n\033[32m-----BACKGROUND MC SAMPLES-----\n\033[m'
	BackgroundSamples = getBackgroundSamples()
	for ds in BackgroundSamples:
		print ds.name, ds.crossSection
		print '   ', ds.getFiles(dataset='AOD', instance='global')[0]

	print '\n\033[32m-----DATA SAMPLES-----\n\033[m'
	DataSamples = getDataSamples()
	for ds in DataSamples:
		print ds.name
		print '   ', ds.getFiles()[0]
