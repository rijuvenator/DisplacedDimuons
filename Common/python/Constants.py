import os

# set directory strings
if 'stempl' in os.environ['USER']:
    DIR_WS = '/afs/cern.ch/work/s/stempl/public/DisplacedDimuons/'
    DIR_EOS = '/eos/user/s/stempl/public/DisplacedDimuons/'

    PREFIX_CERN='root://eoscms.cern.ch/'
    PREFIX_FNAL='root://cmseos.fnal.gov/'
    PREFIX_HEPHY = 'root://hephyse.oeaw.ac.at/'
else:
    DIR_WS= '/afs/cern.ch/work/a/adasgupt/DisplacedDimuons/'
    DIR_EOS= '/eos/cms/store/user/adasgupt/DisplacedDimuons/'

    PREFIX_CERN  = 'root://eoscms.cern.ch/'
    PREFIX_FNAL  = 'root://cmseos.fnal.gov/'
    PREFIX_HEPHY = 'root://hephyse.oeaw.ac.at/'


# set paths to ntuple root directories of the different users
NTUPLES_ROOTDIR = {
    'adasgupt': '/eos/cms/store/user/adasgupt/DisplacedDimuons/NTuples/',
    'valuev'  : '/eos/cms/store/user/valuev/DisplacedDimuons/Tupler/Aug1/',
    'stempl'  : '/eos/user/s/stempl/public/DisplacedDimuons/NTuples/',
}

CMSSW_BASE = os.environ['CMSSW_BASE']
DIR_DD     = os.path.join(os.environ['CMSSW_BASE'], 'src/DisplacedDimuons')

# pdg IDs
LLX_PDGID = 6000113
ABS_MUON_PDGID = 13

# signal points as list of tuples
SIGNALPOINTS = [
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

# signal points for which reco/aod is available
RECOSIGNALPOINTS = [
#	(1000, 350,   35),
#	(1000, 350,  350),
#	(1000, 350, 3500),
#	(1000, 150,   10),
#	(1000, 150,  100),
#	(1000, 150, 1000),
#	(1000,  50,    4),
#	(1000,  50,   40),
#	(1000,  50,  400),
	(1000,  20,    2),
	(1000,  20,   20),
	(1000,  20,  200),
	( 400, 150,   40),
	( 400, 150,  400),
	( 400, 150, 4000),
#	( 400,  50,    8),
#	( 400,  50,   80),
#	( 400,  50,  800),
	( 400,  20,    4),
	( 400,  20,   40),
	( 400,  20,  400),
#	( 200,  50,   20),
#	( 200,  50,  200),
#	( 200,  50, 2000),
#	( 200,  20,    7),
#	( 200,  20,   70),
#	( 200,  20,  700),
	( 125,  50,   50),
	( 125,  50,  500),
	( 125,  50, 5000),
	( 125,  20,   13),
	( 125,  20,  130),
	( 125,  20, 1300),
]

# signal points for which PAT tuples are available
# be careful about 4Mu vs 2Mu2J availability
PATSIGNALPOINTS = [
#   (1000, 350,   35),
#   (1000, 350,  350),
#   (1000, 350, 3500),
#   (1000, 150,   10),
#   (1000, 150,  100),
    (1000, 150, 1000),
#   (1000,  50,    4),
#   (1000,  50,   40),
#   (1000,  50,  400),
#   (1000,  20,    2),
#   (1000,  20,   20),
#   (1000,  20,  200),
#   ( 400, 150,   40),
#   ( 400, 150,  400),
#   ( 400, 150, 4000),
#   ( 400,  50,    8),
#   ( 400,  50,   80),
#   ( 400,  50,  800),
#   ( 400,  20,    4),
#   ( 400,  20,   40),
#   ( 400,  20,  400),
#   ( 200,  50,   20),
#   ( 200,  50,  200),
#   ( 200,  50, 2000),
#   ( 200,  20,    7),
#   ( 200,  20,   70),
#   ( 200,  20,  700),
#   ( 125,  50,   50),
#   ( 125,  50,  500),
#   ( 125,  50, 5000),
    ( 125,  20,   13),
#   ( 125,  20,  130),
#   ( 125,  20, 1300),
]

# signal points as list of tuples
REHLT_SIGNALPOINTS = [
	# (1000, 350,   35),
	# (1000, 350,  350),
	# (1000, 350, 3500),
	# (1000, 150,   10),
	# (1000, 150,  100),
	# (1000, 150, 1000),
	# (1000,  50,    4),
	# (1000,  50,   40),
	# (1000,  50,  400),
	# (1000,  20,    2),
	# (1000,  20,   20),
	# (1000,  20,  200),
	# ( 400, 150,   40),
	# ( 400, 150,  400),
	# ( 400, 150, 4000),
	# ( 400,  50,    8),
	# ( 400,  50,   80),
	# ( 400,  50,  800),
	# ( 400,  20,    4),
	# ( 400,  20,   40),
	# ( 400,  20,  400),
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



# signal points as nested dictionaries
# SIGNALS[mH] is a dictionary of mX:list(cTau)
# SIGNALS[mH][mX] is a list of cTau
SIGNALS = {
	125 : {
		20 : [
			13,  
			130, 
			1300,
		],
		50 : [
			50,   
			500,  
			5000, 
		]
	},
	200 : {
		20 : [
			7,    
			70,   
			700,  
		],
		50 : [
			20,   
			200,  
			2000, 
		]
	},
	400 : {
		20 : [
			4,    
			40,   
			400,  
		],
		50 : [
			8,    
			80,   
			800,  
		],
		150 : [
			40,   
			400,  
			4000, 
		]
	},
	1000 : {
		20 : [
			2,    
			20,   
			200,  
		],
		50 : [
			4,    
			40,   
			400,  
		],
		150 : [
			10,   
			100,  
			1000, 
		],
		350 : [
			35,   
			350,  
			3500, 
		]
	}
}

# order of background samples from weakest to strongest
# used for making stack plots and etc.
BGORDER = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf')
