import ROOT as R
import argparse, os
import DisplacedDimuons.Common.Constants as Constants
import DisplacedDimuons.Common.Utilities as Utilities
import DisplacedDimuons.Common.DataHandler as DH
import DisplacedDimuons.Analysis.Primitives as Primitives

R.gROOT.SetBatch(True)

# common interface to all Analyzers
# name is the sample name
# signalpoint is the signal point if sample is a signal sample
# test is a flag for testing the analyzer
# splitting is 2 numbers CHUNK JOB defining splitting parameters:
#    - CHUNK is how many events to process for this instance
#    - JOB is which job number this is (so that the Analyzer knows which part of the tree to access)
# maxevents is the maximum number of events to run on, if --test is set
# trigger is whether or not to apply the trigger selection to signal samples
# In any given Analyzer, one may add a few extra parameters to PARSER
# in case any additional command-line parameters are desired
PARSER = argparse.ArgumentParser()
PARSER.add_argument('--name'       , dest='NAME'       ,                      default='HTo2XTo2Mu2J', help='sample name'                  )
PARSER.add_argument('--signalpoint', dest='SIGNALPOINT', type=int, nargs=3  , default=(125, 20, 13) , help='the mH mX cTau tuple'         )
PARSER.add_argument('--test'       , dest='TEST'       , action='store_true'                        , help='run test mode for 1000 events')
PARSER.add_argument('--splitting'  , dest='SPLITTING'  , type=int, nargs=2  , default=None          , help='splitting parameter'          )
PARSER.add_argument('--maxevents'  , dest='MAXEVENTS'  , type=int,            default=1000          , help='max events for test mode'     )
PARSER.add_argument('--trigger'    , dest='TRIGGER'    , action='store_true'                        , help='apply trigger to signal'      )
PARSER.add_argument('--cuts'       , dest='CUTS'       ,                      default=''            , help='cut string'                   )
PARSER.add_argument('--skim'       , dest='SKIM'       , action='store_true'                        , help='whether to use the skim file' )

# important setSample function
# this function takes the inputs from ARGS and selects the unique matching Dataset from DataHandler
# this Dataset object contains many important parameters: nEvents, negFrac, systFrac, etc
# and they are available to the Analyzer object through the member variable SAMPLE
# so if e.g. a weight in the analyze() function is desired, it is as simple as
# using self.SAMPLE.nEvents or self.SAMPLE.negFrac
SAMPLES = DH.getAllSamples()
def setSample(ARGS):
    if ARGS.NAME.startswith('HTo2X'):
        if ARGS.SIGNALPOINT is None:
            raise Exception('Need a signal point for HTo2X MC signal.')
        ARGS.SAMPLE = SAMPLES[ARGS.NAME + '_' + Utilities.SPStr(ARGS.SIGNALPOINT)]
    else:
        ARGS.SAMPLE = SAMPLES[ARGS.NAME]

# Analyzer class, one instance per sample, runs over a tree, calls analysis functions
class Analyzer(object):
    # constructor:
    #  ARGS: the output of PARSER
    #    Contains NAME, SIGNALPOINT, TEST, SPLITTING, and SAMPLE. Required.
    #  FILES: ONLY for overriding the default nTuples. Use with caution.
    #  BRANCHKEYS: from Primitives (for ETree)
    #  TREELOOP: whether to actually loop over the tree (usually True)
    #  PARAMS: any additional parameters that can't be obtained any other way
    def __init__(self,
            ARGS,
            BRANCHKEYS  = Primitives.BRANCHKEYS,
            FILES       = None,
            TREELOOP    = True,
            PARAMS      = None
        ):

        self.ARGS = ARGS

        # if this is NOT a signal sample, make sure SIGNALPOINT is None
        # SP will be None if it's not signal, can serve as a test of signal
        if not ARGS.NAME.startswith('HTo2XTo'):
            ARGS.SIGNALPOINT = None

        # ARGS.NAME is always either:
        #  - the name of the sample (BG, Data)
        #  - HTo2XTo(FS)_(mH)_(mX)_(cTau) (Signal)

        # several important parameters are contained within the ARGS namespace
        self.NAME       = ARGS.SAMPLE.name
        self.SP         = None if ARGS.SIGNALPOINT is None else Utilities.SignalPoint(ARGS.SIGNALPOINT)
        self.TEST       = ARGS.TEST
        self.SPLITTING  = ARGS.SPLITTING
        self.MAX        = ARGS.MAXEVENTS
        self.SAMPLE     = ARGS.SAMPLE
        self.TRIGGER    = ARGS.TRIGGER
        self.CUTS       = ARGS.CUTS

        # if TREELOOP was explicitly False, ensure that SPLITTING is None
        if not TREELOOP:
            self.SPLITTING = None

        # set the input tree or list of input trees; see the getNTuples function in DataHandler
        # set it to FILES if FILES is specified, as a special override
        if FILES is None:
            self.FILES  = ARGS.SAMPLE.getNTuples()
        else:
            self.FILES  = FILES

        # cludge for replacing an nTuple with the skimmed version
        if ARGS.SKIM and 'DoubleMuon' in self.NAME:
            if type(self.FILES) == str:
                self.FILES = self.FILES.replace('ntuple', 'skim')
            elif type(self.FILES) == list:
                self.FILES = [i.replace('ntuple', 'skim') for i in self.FILES]

        # these are constants and the rest of the parameters from the constructor
        self.TREE       = 'SimpleNTupler/DDTree'
        self.BRANCHKEYS = BRANCHKEYS
        self.TREELOOP   = TREELOOP
        self.PARAMS     = PARAMS

        # initialize a histograms dictionary automatically
        self.HISTS      = {}

        # run the analysis
        self.run()

    # initialize a TH1F or TH2F given NAME as NAME_self.NAME
    # and args to rest of constructor
    # don't have to use this function of course if HISTS is more complicated
    # but is probably useful, to use in declareHistograms
    def HistInit(self, NAME, *args):
        # set HCLASS based on number of arguments
        if len(args) == 4:
            HCLASS = 'TH1F'
        elif len(args) == 7:
            HCLASS = 'TH2F'
        else:
            raise Exception('Invalid signature: expecting 5 or 8 arguments')

        # set HNAME to NAME_SampleName
        # remember NAME is HTo2XTo**_SPStr for signal
        HNAME = NAME+'_{}'.format(self.NAME)

        # declare the histogram
        self.HISTS[NAME] = getattr(R,HCLASS)(HNAME, *args)

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
        if not self.TEST:
            try:
                FNAME = FILE.format(self.NAME)
            except:
                FNAME = FILE
            # add a suffix if we're splitting output
            if self.SPLITTING is not None:
                FNAME = FNAME.replace('.root', '_{}.root'.format(self.SPLITTING[1]))
        else:
            FNAME = 'test.root'
        f = R.TFile.Open(FNAME, 'RECREATE')
        for key in self.HISTS:
            self.HISTS[key].Write()
        f.Close()
    
    # opens files, gets the tree, checks if they're valid
    # declares histograms, sets directory 0
    # runs begin, loops over tree, declares ETree, runs analyze, runs end
    def run(self):
        # if FILES is a string, treat it as a single file and get the tree
        if type(self.FILES) == str:
            f = R.TFile.Open(self.FILES)
            if not f:
                raise IOError
            t = f.Get(self.TREE)
            if not t:
                raise ReferenceError
        # if FILES is a list, create a TChain and add all the files
        elif type(self.FILES) == list:
            t = R.TChain(self.TREE)
            for f in self.FILES:
                t.Add(f)
            if not t:
                raise ReferenceError

        self.declareHistograms(self.PARAMS)
        self.releaseHistograms()
        self.begin(self.PARAMS)

        # only turn on the branches required
        Primitives.SelectBranches(t, DecList=self.BRANCHKEYS)

        # either run over the whole tree,
        # tree gets addressed with the for loop, or
        # split the output into several files,
        # and tree gets addressed with GetEntry
        # either way, end at MAX if TEST, declare ETree, and analyze()
        if self.TREELOOP:
            if self.SPLITTING is not None:
                CHUNK, JOB = self.SPLITTING
                ELOW, EHIGH = JOB*CHUNK, min((JOB+1)*CHUNK, t.GetEntries())
                for INDEX in xrange(ELOW, EHIGH):
                    self.INDEX = INDEX
                    if self.TEST:
                        if INDEX == self.MAX:
                            break
                    t.GetEntry(INDEX)
                    E = Primitives.ETree(t, self.BRANCHKEYS)
                    self.analyze(E, self.PARAMS)
            else:
                for INDEX, EVENT in enumerate(t):
                    self.INDEX = INDEX
                    if self.TEST:
                        if INDEX == self.MAX:
                            break
                    E = Primitives.ETree(t, self.BRANCHKEYS)
                    self.analyze(E, self.PARAMS)

        self.end(self.PARAMS)
        f.Close()
    
    # functions to be written by the specific analyzer script
    # declareHistograms should define the plots to be filled and written
    # begin runs before the loop, end runs after, analyze runs during
    def declareHistograms(self, PARAMS=None):
        pass

    def begin(self, PARAMS=None):
        pass

    def end(self, PARAMS=None):
        pass

    def analyze(self, E, PARAMS=None):
        pass
