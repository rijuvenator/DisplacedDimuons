import DisplacedDimuons.Tupler.Utilities.dataHandler as DH
import itertools
import re

datasets = DH.get_H2X4M_Datasets()

datasets.sort(key=lambda x: x.signalPoint())

matchProcess = 'AODSIM'
#matchProcess = 'mAODSIM'

print matchProcess
for key, group in itertools.groupby(datasets, key=lambda x: x.signalPoint()):
	sets = list(group)
	if sum([True if re.match(matchProcess, data.process) else False for data in sets])>0:
		print 'HTo2LongLivedTo4mu MC : mH = {}, mX = {}, cTau = {}'.format(*key)
