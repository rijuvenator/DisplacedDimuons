import ROOT as R
import argparse, os
import DisplacedDimuons.Common.Constants as Constants
import DisplacedDimuons.Common.Utilities as Utilities
import DisplacedDimuons.Analysis.Primitives as Primitives

R.gROOT.SetBatch(True)

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--signalpoint', dest='SIGNALPOINT', type=int, nargs=3  , default=(125, 20, 13), help='the mH mX cTau tuple'         )
PARSER.add_argument('--develop'    , dest='DEVELOP'    , action='store_true',                        help='run test mode for 1000 events')

F_NTUPLE = os.path.join(Constants.DIR_WS_RIJU, 'simple_ntuple_{}.root')
T_NTUPLE = 'SimpleNTupler/DDTree'

F_DEFAULT = F_NTUPLE
T_DEFAULT = T_NTUPLE

# Analyzer class, one instance per signal point, runs over a tree, calls analysis functions
class Analyzer(object):
	# constructor:
	#  SIGNALPOINT: SignalPoint object
	#  BRANCHKEYS: from Primitives (for ETree)
	#  FILE: either a file or a string with {} in it where the SPString should go
	#  TREENAME: name of tree
	#  DEVELOP: the result of the parser's develop; whether or not run in test mode
	#  MAX_EVENTS: if something other than 1000; only does anything if DEVELOP is true
	def __init__(self,
			SIGNALPOINT = None,
			BRANCHKEYS  = Primitives.BRANCHKEYS,
			FILE        = F_DEFAULT,
			TREENAME    = T_DEFAULT,
			DEVELOP     = False,
			MAX_EVENTS  = 1000
		):
		if SIGNALPOINT is None:
			exit()
		self.SP         = SIGNALPOINT
		self.BRANCHKEYS = BRANCHKEYS
		self.FILE       = FILE
		self.TREE       = TREENAME
		self.DEVELOP    = DEVELOP
		self.MAX        = MAX_EVENTS

		self.HISTS      = {}

		self.run()

	# initialized a TH1F or TH2F given NAME as NAME+_SPString and args to rest of constructor
	# don't have to use this function of course if HISTS is more complicated
	# but is probably useful, to use in declareHistograms
	def HistInit(self, NAME, *args):
		if len(args) == 4:
			HCLASS = 'TH1F'
		elif len(args) == 7:
			HCLASS = 'TH2F'
		self.HISTS[NAME] = getattr(R,HCLASS)(NAME+'_{}'.format(self.SP.SPStr()), *args)

	# sets all histograms in HISTS directory to 0
	# this is called in run, so I protected it with a try. if HISTS[key]
	# isn't a histogram, nothing will happen. then the user is responsible
	# for the memory management.
	def releaseHistograms(self):
		for key in self.HISTS:
			try:
				self.HISTS[key].SetDirectory(0)
			except:
				break

	# writes all histograms in HISTS to FILE
	# don't have to use this function of course if HISTS is more complicated
	# user is responsible for calling this
	def writeHistograms(self, FILE):
		if not self.DEVELOP:
			try:
				FNAME = FILE.format(self.SP.SPStr())
			except:
				FNAME = FILE
		else:
			FNAME = 'test.root'
		f = R.TFile.Open(FNAME, 'RECREATE')
		for key in self.HISTS:
			self.HISTS[key].Write()
		f.Close()
	
	# opens the file, gets the tree, checks if they're valid
	# declares histograms, sets directory 0
	# runs begin, loops over tree, declares ETree, runs analyze, runs end
	def run(self):
		try:
			f = R.TFile.Open(self.FILE.format(self.SP.SPStr()))
			if not f:
				raise IOError
		except:
			f = R.TFile.Open(self.FILE)
			if not f:
				raise IOError
		t = f.Get(self.TREE)
		if not t:
			raise ReferenceError
		self.declareHistograms()
		self.releaseHistograms()
		self.begin()
		for INDEX, EVENT in enumerate(t):
			if self.DEVELOP:
				if INDEX == self.MAX:
					break
			E = Primitives.ETree(t, self.BRANCHKEYS)
			self.analyze(E)
		self.end()
		f.Close()
	
	# functions to be written by the specific analyzer script
	# declareHistograms should define the plots to be filled and written
	# begin runs before the loop, end runs after, analyze runs during
	def declareHistograms(self):
		pass

	def begin(self):
		pass

	def end(self):
		pass

	def analyze(self, E):
		pass
