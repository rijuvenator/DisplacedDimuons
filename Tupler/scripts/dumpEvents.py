import DisplacedDimuons.Tupler.Utilities.dataHandler as DH

datasets = DH.getMCDatasets()

for data in datasets:
	if data.mH == 125 and data.process == 'AODSIM-ReHLT_V37-v1':
		fleList = DH.DASQueryList('file,lumi,events dataset={} instance={}'.format(data.dataset, DH.DEFAULT_INSTANCE))
		totalE = 0
		for rstring in fleList:
			cols = rstring.split()
			f = cols[0]
			l = map(int, cols[1].strip('[').strip(']').split(','))
			e = map(int, cols[2].strip('[').strip(']').split(','))

			totalE += sum(e)

		print 'HTo2LongLivedTo4mu {:4d} {:3d} {:4d} : {:d} events'.format(data.mH, data.mX, data.cTau, totalE)

