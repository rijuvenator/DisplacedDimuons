import DisplacedDimuons.Tupler.Utilities.dataHandler as DH

FINALSTATE  = '4Mu'
SIGNALPOINT = (125, 20, 13)
PROCESS     = 'AODSIM-ReHLT_V37-v1'

datasets = getattr(DH, 'getHTo2XTo'+FINALSTATE+'Samples')()
for data in datasets:
    if data.signalPoint() == SIGNALPOINT:
        if PROCESS in data.datasets:
            fleList = DH.DASQueryList('file,lumi,events dataset={} instance={}'.format(data.datasets[PROCESS], data.instances[PROCESS]))
            totalE = 0
            for rstring in fleList:
                cols = rstring.split()
                f = cols[0]
                l = map(int, cols[1].strip('[').strip(']').split(','))
                e = map(int, cols[2].strip('[').strip(']').split(','))
                totalE += sum(e)
            print 'HTo2XTo{} : {} : {} :: {} events'.format(FINALSTATE, SIGNALPOINT, PROCESS, totalE)
        else:
            raise Exception('No HTo2XTo{} dataset found with signal point {} and process {}'.format(FINALSTATE, SIGNALPOINT, PROCESS))
