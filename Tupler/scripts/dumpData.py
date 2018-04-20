import DisplacedDimuons.Tupler.Utilities.dataHandler as DH
import itertools

datasets = DH.get_H2X4M_Datasets()

datasets.sort(key=lambda x: x.signalPoint())

for key, group in itertools.groupby(datasets, key=lambda x: x.signalPoint()):
	print 'HTo2LongLivedTo4mu MC : mH = {}, mX = {}, cTau = {}'.format(*key)
	for data in group:
		print ' ', data.process
