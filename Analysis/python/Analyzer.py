import ROOT as R
import argparse
import DisplacedDimuons.Analysis.Constants as Constants
import DisplacedDimuons.Analysis.Primitives as Primitives
import DisplacedDimuons.Analysis.Utilities as Utilities

R.gROOT.SetBatch(True)

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--signalpoint', dest='SIGNALPOINT', type=int, nargs=3  , default=(125, 20, 13), help='the mH mX cTau tuple'         )
PARSER.add_argument('--develop'    , dest='DEVELOP'    , action='store_true',                        help='run test mode for 1000 events')

F_NTUPLE = Constants.DIR_WS + 'simple_ntuple_{}.root'
T_NTUPLE = 'SimpleNTupler/DDTree'

F_DEFAULT = F_NTUPLE
T_DEFAULT = T_NTUPLE

class Analyzer(object):
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

	def declareHistograms(self):
		pass

	def HistInit(self, NAME, *args):
		if len(args) == 4:
			HCLASS = 'TH1F'
		elif len(args) == 7:
			HCLASS = 'TH2F'
		self.HISTS[NAME] = getattr(R,HCLASS)(NAME+'_{}'.format(self.SP.SPStr()), *args)

	def releaseHistograms(self):
		for key in self.HISTS:
			self.HISTS[key].SetDirectory(0)

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
	
	def run(self):
		try:
			f = R.TFile.Open(self.FILE.format(self.SP.SPStr()))
		except:
			f = R.TFile.Open(self.FILE)
		t = f.Get(self.TREE)
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
	
	def begin(self):
		pass

	def end(self):
		pass

	def analyze(self, E):
		pass
