from __future__ import division
import numpy as np

data = []
f = open('pairingCriteria.txt')
for line in f:
    cols = line.strip('\n').split()
    if '===' in line:
        data.append([])
        data[-1].extend(map(int, [cols[i] for i in (3, 4, 5, 8, 11, 16)]))
    if 'all' in line:
        if '100.00' in line:
            data[-1].extend(map(int, [cols[i] for i in (3, 7, 12)]))
        else:
            data[-1].extend(map(int, [cols[i] for i in (3, 8, 13)]))
    if 'loose' in line:
        data[-1].extend(map(int, [cols[i] for i in (3, 8, 13)]))

data = np.array(data)
print data

# 0  1  2    3     4       5     6      7        8       9        10         11
# mH mX cTau total trigger pairs dimAll matchAll corrAll dimLoose matchLoose corrLoose

mH,mX,cTau,total,trigger,pairs,dimAll,matchAll,corrAll,dimLoose,matchLoose,corrLoose = data[:,0],data[:,1],data[:,2],data[:,3],data[:,4],data[:,5],data[:,6],data[:,7],data[:,8],data[:,9],data[:,10],data[:,11],

trigEff  = trigger/total
looseEff = pairs/trigger
pairEff  = pairs/total

dimEff   = corrLoose/dimLoose
lossEff  = 1-(dimLoose/dimAll)
matchEff = 1-(matchLoose/dimLoose)
wrongEff = 1-(corrLoose/matchLoose)

allEff   = corrAll/dimAll

temp = np.array([trigEff, looseEff, pairEff, dimEff, lossEff, matchEff, wrongEff, allEff])
nCols = len(temp)
temp = np.transpose(temp)
temp = temp[temp[:,7].argsort()]
for i in range(33):
    fString = '{:7.4f} ' * nCols
    print fString.format(*(temp[i,j] for j in xrange(nCols)))
