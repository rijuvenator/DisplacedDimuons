import DisplacedDimuons.Tupler.Utilities.dataHandler as DH
import itertools

SIGNALPOINT = (125, 20, 1300)
PROCESS     = 'AODSIM-ReHLT_V13-v1'
ALLFILES    = False

SIGNALPOINT = (1000, 350, 3500)
PROCESS     = 'GS-v1'
ALLFILES    = False

SIGNALPOINT = (125, 20, 13)
PROCESS     = 'mAODSIM-ReHLT_V37-v1'
ALLFILES    = False

SIGNALPOINT = (1000, 20, 200)
PROCESS     = 'GSR-v1'
ALLFILES    = False

SIGNALPOINT = (1000, 350, 3500)
PROCESS     = 'GSR-v1'
ALLFILES    = False

datasets = DH.getMCDatasets()

datasets.sort(key=lambda x: x.signalPoint())

for key, group in itertools.groupby(datasets, key=lambda x: x.signalPoint()):
	if key == SIGNALPOINT:
		for data in group:
			if data.process == PROCESS:
				files = data.getFiles(prefix=DH.ROOT_PREFIX)
				if ALLFILES:
					for f in files:
						print f
				else:
					print files[0]
				break
		break

