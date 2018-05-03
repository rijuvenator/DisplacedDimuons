import subprocess as bash
import os, re

#########################
# GENERAL DATASET TOOLS #
#########################

ROOT_PREFIX      = 'root://cms-xrd-global.cern.ch/'

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
# name is a short key that refers to the dataset
class Dataset(object):
	def __init__(self, dataset, name):
		self.dataset = dataset
		self.name     = name
		self.files    = None
		self.isMC     = None
		self.instance = 'prod/global'

	def getFiles(self, prefix=''):
		# set self.files if it's not set
		if not self.files:
			self.files = DASQueryList('file dataset={} instance={}'.format(self.dataset, self.instance))
			self.files.sort()
		if prefix == '':
			return self.files
		else:
			return [prefix + fn for fn in self.files]

# derived class for any MC dataset
class MCSample(Dataset):
	def __init__(self, dataset, name):
		Dataset.__init__(self, dataset, name)
		self.isMC = True

# derived class for a background sample
# in this implementation, takes its input from a data file
# so all of the inputs are in that file, and the code for running over the file is below
class BackgroundSample(MCSample):
	def __init__(self, dataset, name, nEvents, color, systFrac, crossSection, kFactor=1.):
		MCSample.__init__(self, dataset, name)
		self.isSignal     = False
		self.nEvents      = int(nEvents)
		self.color        = int(color)
		self.systFrac     = float(systFrac)
		self.crossSection = float(crossSection)
		self.kFactor      = float(kFactor)
		self.isMadgraph   = 'amcatnlo' in self.dataset

		if self.name.startswith('DY'):
			match = PATTERNS['DY_MBIN'].match(self.name)
			self.massRange = (int(match.group(1)), float('inf') if match.group(2) == 'Inf' else int(match.group(2)))

# derived class for a signal sample
# in this implementation, takes its input from a DAQ query and parses it
# maybe a bit unstable since it relies on the state of DAS being what I expect it to be
class SignalSample(MCSample):
	def __init__(self, dataset, name):
		MCSample.__init__(self, dataset, name)
		self.isSignal = True

		if self.name.startswith('HTo2XTo4Mu'):
			match = PATTERNS['HTo2XTo4Mu'].match(self.dataset)

			self.instance = 'prod/phys03'
			self.mH       = int(match.group(1))
			self.mX       = int(match.group(2))
			self.cTau     = int(match.group(3))
			self.process  =     match.group(4)
			self.ID       =     match.group(5)

			self.name = 'HTo2XTo4Mu' + '_'.join(map(str,(self.mH, self.mX, self.cTau)))
	
	def signalPoint(self):
		if self.name.startswith('HTo2XTo4Mu'):
			return (self.mH, self.mX, self.cTau)

###############
# GET SAMPLES #
###############

# get HTo2LongLivedTo4mu MC samples
# wrapped in a function so that it can be called from other scripts
# a DAS query is run, giving a list of datasets which match the regex above
# and a list of datasets is formed accordingly
def getHTo2XTo4MuSamples():
	datasetStrings = DASQueryList('dataset=/HTo2LongLivedTo4mu*/*/* instance=prod/phys03')
	samples = [SignalSample(ds, 'HTo2XTo4Mu') for ds in datasetStrings]
	return samples

# get background MC samples
# wrapped in a function so that it can be called from other scripts
# the success of this code relies on BackgroundMCSamples.dat
# having records separated by a - alone on a line, and
# having the positional arguments of the BackgroundSample constructor 
# be in the same order as the records in BackgroundMCSamples.dat
# then the parameters are stored in a list, and can be unpacked with *
def getBackgroundSamples():
	f = open(os.path.join(os.environ['CMSSW_BASE'], 'src/DisplacedDimuons/Tupler/python/Utilities/BackgroundMCSamples.dat'))
	BackgroundParameters = []
	Entry = []
	for line in f:
		if line == '-\n':
			BackgroundParameters.append(list(Entry))
			Entry = []
			continue
		Entry.append(line.strip('\n'))
	f.close()
	
	samples = [BackgroundSample(*Entry) for Entry in BackgroundParameters]
	return samples

######################
# RUN AS MAIN MODULE #
######################

if __name__ == '__main__':
	HTo2XTo4MuSamples = getHTo2XTo4MuSamples()

	for ds in HTo2XTo4MuSamples:
		if 'AOD' in ds.process:
			print ds.process, ds.signalPoint()
			print '   ', ds.getFiles()[0]
	
	BackgroundSamples = getBackgroundSamples()

	for ds in BackgroundSamples:
		print ds.name, ds.crossSection
		print '   ', ds.getFiles()[0]

# HTo2LongLivedTo4mu MC signal points: (mH, mX, cTau)
signalpoints = [
	(1000, 350,   35),
	(1000, 350,  350),
	(1000, 350, 3500),
	(1000, 150,   10),
	(1000, 150,  100),
	(1000, 150, 1000),
	(1000,  50,    4),
	(1000,  50,   40),
	(1000,  50,  400),
	(1000,  20,    2),
	(1000,  20,   20),
	(1000,  20,  200),
	( 400, 150,   40),
	( 400, 150,  400),
	( 400, 150, 4000),
	( 400,  50,    8),
	( 400,  50,   80),
	( 400,  50,  800),
	( 400,  20,    4),
	( 400,  20,   40),
	( 400,  20,  400),
	( 200,  50,   20),
	( 200,  50,  200),
	( 200,  50, 2000),
	( 200,  20,    7),
	( 200,  20,   70),
	( 200,  20,  700),
	( 125,  50,   50),
	( 125,  50,  500),
	( 125,  50, 5000),
	( 125,  20,   13),
	( 125,  20,  130),
	( 125,  20, 1300),
]
