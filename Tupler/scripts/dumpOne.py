import DisplacedDimuons.Tupler.Utilities.dataHandler as DH

FINALSTATE  = '4Mu'
SIGNALPOINT = (125, 20, 13)
PROCESS     = 'May2018-AOD-v1'
ALLFILES    = False

datasets = getattr(DH, 'getHTo2XTo'+FINALSTATE+'Samples')()
for data in datasets:
    if data.signalPoint() == SIGNALPOINT:
        if PROCESS in data.datasets:
            print 'HTo2XTo{} : {} : {}'.format(FINALSTATE, SIGNALPOINT, PROCESS)
            files = data.getFiles(prefix=DH.ROOT_PREFIX, dataset=PROCESS, instance=PROCESS)
            if ALLFILES:
                for f in files:
                    print '  ', f
            else:
                print '  ', files[0]
            break
        else:
            raise Exception('No HTo2XTo{} dataset found with signal point {} and process {}'.format(FINALSTATE, SIGNALPOINT, PROCESS))
