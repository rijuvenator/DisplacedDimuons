import ROOT as R
import argparse, os
import DisplacedDimuons.Common.Constants as Constants
import DisplacedDimuons.Common.Utilities as Utilities
import DisplacedDimuons.Analysis.Primitives as Primitives

R.gROOT.SetBatch(True)

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--signalpoint', dest='SIGNALPOINT', type=int, nargs=3  , default=(125, 20, 13), help='the mH mX cTau tuple'         )
PARSER.add_argument('--test'       , dest='TEST'       , action='store_true',                        help='run test mode for 1000 events')
PARSER.add_argument('--splitting'  , dest='SPLITTING'  , type=int, nargs=2  , default=None         , help='splitting parameter'          )
PARSER.add_argument('--name'       , dest='NAME'       ,                      default='HTo2XTo4Mu' , help='sample name'                  )

F_NTUPLE     = os.path.join(Constants.DIR_EOS, 'NTuples/ntuple_{}.root')
F_GEN_NTUPLE = os.path.join(Constants.DIR_EOS, 'NTuples/genOnly_ntuple_{}.root')
F_AOD_NTUPLE = os.path.join(Constants.DIR_EOS, 'NTuples/aodOnly_ntuple_{}.root')

T_NTUPLE = 'SimpleNTupler/DDTree'

def setFNAME(ARGS, GEN=False, NOPAT=False):
    # if this is a signal sample, use the aodOnly version
    if ARGS.NAME.startswith('HTo2X'):
        ARGS.FNAME = F_AOD_NTUPLE

    # otherwise, use the full PAT version
    else:
        ARGS.FNAME = F_NTUPLE

    # if this is a signal sample that has a full PAT version, use it unless explictly told not to
    # this criteria will evolve slowly over the next few days to weeks as we produce more PAT Tuples
    if not NOPAT and ARGS.NAME == 'HTo2XTo2Mu2J' and ARGS.SIGNALPOINT in Constants.PATSIGNALPOINTS:
        ARGS.FNAME = F_NTUPLE

    # use the genOnly version if explictly required
    if GEN:
        ARGS.FNAME = F_GEN_NTUPLE

    # add a root protocol if we are not on lxplus
    if not 'lxplus' in os.environ['HOSTNAME']:
        ARGS.FNAME = Constants.PREFIX_CERN + ARGS.FNAME

F_DEFAULT = F_NTUPLE
T_DEFAULT = T_NTUPLE

# Analyzer class, one instance per signal point, runs over a tree, calls analysis functions
class Analyzer(object):
    # constructor:
    #  NAME: sample name
    #  SIGNALPOINT: SignalPoint object
    #  BRANCHKEYS: from Primitives (for ETree)
    #  FILE: either a file or a string with {} in it where the SPString should go
    #  TREENAME: name of tree
    #  TEST: the result of the parser's test; whether or not run in test mode
    #  MAX_EVENTS: if something other than 1000; only does anything if TEST is true
    #  SPLITTING: a tuple: (number of events per job, job number 0-indexed)
    #  TREELOOP: whether to actually loop over the tree (usually True)
    #  PARAMS: any additional parameters that can't be obtained any other way
    def __init__(self,
            NAME        = None,
            SIGNALPOINT = None,
            BRANCHKEYS  = Primitives.BRANCHKEYS,
            FILE        = F_DEFAULT,
            TREENAME    = T_DEFAULT,
            TEST        = False,
            MAX_EVENTS  = 1000,
            SPLITTING   = None,
            TREELOOP    = True,
            PARAMS      = None
        ):

        # if this is a signal sample, make sure there's a signal point
        # then set NAME unambiguously to HTo2XTo**_mH_mX_cTau
        if NAME.startswith('HTo2X'):
            if SIGNALPOINT is None:
                raise Exception('Need a signal point for HTo2X MC signal.')
            NAME = NAME + '_' + SIGNALPOINT.SPStr()

        # if this is NOT a signal sample, make sure SIGNALPOINT is None
        if not NAME.startswith('HTo2XTo'):
            SIGNALPOINT = None

        self.NAME       = NAME
        self.SP         = SIGNALPOINT
        self.BRANCHKEYS = BRANCHKEYS
        self.FILE       = FILE
        self.TREE       = TREENAME
        self.TEST       = TEST
        self.MAX        = MAX_EVENTS
        self.SPLITTING  = SPLITTING
        self.TREELOOP   = TREELOOP
        self.PARAMS     = PARAMS

        self.HISTS      = {}

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
    
    # opens the file, gets the tree, checks if they're valid
    # declares histograms, sets directory 0
    # runs begin, loops over tree, declares ETree, runs analyze, runs end
    def run(self):
        try:
            f = R.TFile.Open(self.FILE.format(self.NAME))
            if not f:
                raise IOError
        except:
            f = R.TFile.Open(self.FILE)
            if not f:
                raise IOError
        t = f.Get(self.TREE)
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
