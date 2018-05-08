import DisplacedDimuons.Tupler.Utilities.dataHandler as DH

AODDatasetStrings = DH.DASQueryList('dataset=/HTo2LongLivedTo4mu*/*/* instance=prod/phys03')

f = open('HTo2XTo4MuSignalMCSamples.dat', 'w')
for ds in AODDatasetStrings:
	f.write(ds           + '\n')
	f.write('_'          + '\n')
	f.write('HTo2XTo4Mu' + '\n')
	f.write('-'          + '\n')
f.close()
