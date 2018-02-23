import subprocess as bash
import re

#########################
# GENERAL DATASET TOOLS #
#########################

ROOT_PREFIX      = 'root://cms-xrd-global.cern.ch/'
DEFAULT_INSTANCE = 'prod/phys03'

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

# class for storing information about data
# dataset is a dataset string from DAS: /*/*/*
class Dataset(object):
	def __init__(self, dataset):
		self.dataset = dataset
		self.files   = None
		self.isMC    = None

	def getFiles(self, prefix='', instance=None):
		# set self.files if it's not set
		if not self.files:
			if not instance:
				instance = DEFAULT_INSTANCE
			self.files = DASQueryList('file dataset={} instance={}'.format(self.dataset, instance))
			self.files.sort()
		if prefix == '':
			return self.files
		else:
			return [prefix + fn for fn in self.files]

#########################
# HTo2LongLivedTo4mu MC #
#########################

# derived class for HTo2LongLivedTo4mu MC
# dataset is a dataset string from DAS: /*/*/*
class MCData(Dataset):
	def __init__(self, dataset, regex):
		Dataset.__init__(self, dataset)

		self.isMC = True

		# the regex is a constant for this class (see below), but
		# just so that there aren't global dependencies
		match = regex.match(self.dataset)

		self.mH      = int(match.group(1))
		self.mX      = int(match.group(2))
		self.cTau    = int(match.group(3))
		self.process =     match.group(4)
		self.ID      =     match.group(5)
	
	# I foresee returning this tuple a lot
	def signalPoint(self):
		return (self.mH, self.mX, self.cTau)

# get HTo2LongLivedTo4mu MC data
# wrapped in a function because it's a module
def getMCDatasets():
	datasetStrings = DASQueryList('dataset=/HTo2LongLivedTo4mu*/*/* instance={instance}'.format(instance=DEFAULT_INSTANCE))

	# regex to match dataset
	# five groups: mH, mX, cTau (digits 1-4), process string (\S*), weird hash ID (\w*)
	datasetPatternString = r'/HTo2LongLivedTo4mu_MH-(\d{1,4})_MFF-(\d{1,4})_CTau-(\d{1,4})mm\S*pythia8_(\S*)-(\w*)/USER'
	datasetRegex = re.compile(datasetPatternString)

	# make dataset objects
	mcDatasets = [MCData(ds, datasetRegex) for ds in datasetStrings]

	return mcDatasets

######################
# RUN AS MAIN MODULE #
######################

if __name__ == '__main__':
	mcDatasets = getMCDatasets()

	for mc in mcDatasets:
		if 'AOD' in mc.process:
			print mc.process, mc.signalPoint()

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
