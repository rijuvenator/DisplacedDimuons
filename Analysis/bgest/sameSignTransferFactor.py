import math
import itertools
import argparse

# opens up the dumps from studyAsymmetryWithCuts and does various counting things
# I sort of grossly combined two similar scripts with the STYLE flag, either QCD style or DY style
# it'll count SS, OS, SR, CR type regions, do various efficiencies, etc.

parser = argparse.ArgumentParser()
parser.add_argument('--style', dest='STYLE', choices=['QCD', 'DY'], default='DY')
args = parser.parse_args()

if args.STYLE == 'QCD':
    counts = {
        'SS' : {
            'SR' : {},
            'CR' : {}
        },
        'OS' : {
            'SR' : {},
            'CR' : {}
        }
    }

    massCounts = {
        'SS' : {
            'SR' : {},
            'CR' : {}
        },
        'OS' : {
            'SR' : {},
            'CR' : {}
        }
    }

    nBins = 1
    bins = [(60.+(115.-60.)/nBins*i, 60.+(115.-60.)/nBins*(i+1)) for i in xrange(nBins)]

    fname = 'DaddyDSA_DataOnly_LxySig60-115.txt'

elif args.STYLE == 'DY':
    #    'SS' : {
    #        'SR' : {},
    #        'CR' : {}
    #    },
        'OS' : {
            'SR' : {},
            'CR' : {}
        }
    }

    massCounts = {
    #    'SS' : {
    #        'SR' : {},
    #        'CR' : {}
    #    },
        'OS' : {
            'SR' : {},
            'CR' : {}
        }
    }


    bins = [(0., 0.5), (0.5, 1.), (1., 1.5)]
    #bins = [(0., 1./3.), (1./3., 2./3.), (2./3., 1.)]

    fname = 'DaddyDSA_DataOnly_LxySig1.txt'

def whichRegion(deltaPhi):
    if   deltaPhi <    math.pi/4.: return 'SR'
    elif deltaPhi > 3.*math.pi/4.: return 'CR'
    return None

massBins = [
     (10., 32.),
     (20., 80.),
     (35., 245.),
     (65., float('inf')),
]

for sign in counts:
    for region in counts[sign]:
        for mybin in bins:
            counts[sign][region][mybin] = 0
        for mybin in massBins:
            massCounts[sign][region][mybin] = 0

for line in open(fname):

    cols = line.strip('\n').split()
    PATLxySig = float(cols[14])
    DSALxySig = float(cols[15])
    deltaPhi  = float(cols[18])
    mass      = float(cols[-4])
    sign      = cols[-1]

    if args.STYLE == 'DY':
        if sign == 'SS': continue

    region = whichRegion(deltaPhi)

    if region is None: continue

    for mybin in bins:
        if 6. < DSALxySig and mybin[0] <= PATLxySig < mybin[1]:
            counts[sign][region][mybin] += 1

    for mybin in massBins:
        if 6. < DSALxySig and mybin[0] < mass < mybin[1] and (True if args.STYLE == 'QCD' else PATLxySig < 1.:
            massCounts[sign][region][mybin] += 1

def safeDivide(a, b):
    try:
        return a/float(b)
    except:
        return 0.

if args.STYLE == 'QCD':
    for region in counts['SS']:
        if region == 'CR': continue

        print ''
        print '=== {} ::: DSA LxySig > 6 ==='.format(region)
        for mybin in bins:
            print '    {:5.1f} < PATLxySig < {:5.1f} : {:3d} {:3d} ::: {:6.4f} +/- {:6.4f}'.format(
                mybin[0], mybin[1],
                counts['SS'][region][mybin], counts['OS'][region][mybin],
                safeDivide(counts['OS'][region][mybin], counts['SS'][region][mybin]),
                safeDivide(counts['OS'][region][mybin], counts['SS'][region][mybin]) * math.sqrt( safeDivide(1., counts['SS'][region][mybin]) + safeDivide(1., counts['OS'][region][mybin]) )
            )

        print ''
        for mybin in massBins:
            print '    {:3.0f} < mass < {:3s} : {:3d} {:3d} ::: {:6.4f} +/- {:6.4f}'.format(
                mybin[0], '{:3.0f}'.format(mybin[1]) if mybin[1] < float('inf') else 'inf',
                massCounts['SS'][region][mybin], massCounts['OS'][region][mybin],
                safeDivide(massCounts['OS'][region][mybin], massCounts['SS'][region][mybin]),
                safeDivide(massCounts['OS'][region][mybin], massCounts['SS'][region][mybin]) * math.sqrt( safeDivide(1., massCounts['SS'][region][mybin]) + safeDivide(1., massCounts['OS'][region][mybin]) )
                #math.sqrt( safeDivide(1., massCounts['SS'][region][mybin]) + safeDivide(1., massCounts['OS'][region][mybin]) )

            )
elif args.STYLE == 'DY':
    if True:
        sign = 'OS'
        print '=== OS ::: DSA LxySig > 6 ==='
        for mybin in bins:
            print '    {:5.1f} < PATLxySig < {:5.1f} : {:3d} {:3d} ::: {:6.4f} +/- {:6.4f}'.format(
                mybin[0], mybin[1],
                counts['OS']['SR'][mybin], counts['OS']['CR'][mybin],
                safeDivide(counts['OS']['CR'][mybin], counts['OS']['SR'][mybin]),
                safeDivide(counts['OS']['CR'][mybin], counts['OS']['SR'][mybin]) * math.sqrt( safeDivide(1., counts['OS']['CR'][mybin]) + safeDivide(1., counts['OS']['SR'][mybin]) )
            )

        print ''
        for mybin in massBins:
            print '    {:3.0f} < mass < {:3s} : {:3d} {:3d} ::: {:6.4f} +/- {:6.4f}'.format(
                mybin[0], '{:3.0f}'.format(mybin[1]) if mybin[1] < float('inf') else 'inf',
                massCounts['OS']['SR'][mybin], massCounts['OS']['CR'][mybin],
                safeDivide(massCounts['OS']['CR'][mybin], massCounts['OS']['SR'][mybin]),
                safeDivide(massCounts['OS']['CR'][mybin], massCounts['OS']['SR'][mybin]) * math.sqrt( safeDivide(1., massCounts['OS']['CR'][mybin]) + safeDivide(1., massCounts['OS']['SR'][mybin]) )

            )
