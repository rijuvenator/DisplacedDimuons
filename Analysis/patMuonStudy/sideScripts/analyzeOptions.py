from __future__ import division
from DisplacedDimuons.Common.Constants import SIGNALPOINTS

# Mar 1, 2019 -- look at the state of SelectObjectsReordered in Selector
#
# the data file is made by running studyMatchesWithPCOptions.py with --pcoption 1 2 3 4 and --hybrids,
# as well as no --hybrids (PAT) and no REP in the cutstring (DSA)
# each run gives 4 columns of numbers (+ the signalpoints)
# for 2Mu2J, the 4th column is identical to the 3rd, so get rid of it
# put the columns together with cut and paste and pr and column
# this should produce 22 columns: FS mH mX cTau (events dims gens) * 6

data = {}

with open('text/matchesWithOptions.txt') as f:
    for line in f:
        cols = line.strip('\n').split()
        info = map(int, cols[1:])
        sp = tuple(info[:3])
        counts = info[3:]
        keys = ('Option1', 'Option2', 'Option3', 'Option4', 'PAT', 'DSA')
        data[sp] = {key:{} for key in keys}
        for i in xrange(0, len(counts), 3):
            chunk = counts[i:i+3]
            data[sp][keys[i//3]]['events'] = chunk[0]
            data[sp][keys[i//3]]['dims'  ] = chunk[1]
            data[sp][keys[i//3]]['gens'  ] = chunk[2]

for field in ('events', 'gens'):
    print '{:>4s} {:>3s} {:>4s} {:>7s} {:>7s} {:>7s} {:>7s} {:>7s}'.format('mH', 'mX', 'cTau', 'Option1', 'Option2', 'Option3', 'Option4', 'PAT')
    print '-' * (4+3+4+(7*5)+8-1)
    for sp in SIGNALPOINTS:
        print '{:4d} {:3d} {:4d}'.format(*sp),
        iters = ['Option'+str(i+1) for i in xrange(4)] + ['PAT']
        vals  = [data[sp][key][field]/data[sp]['DSA'][field] for key in iters]
        fstring = ''
        for v in vals:
            if v == max(vals): fstring += '\033[31m{:7.2%}\033[m '
            else:              fstring +=         '{:7.2%} '
        print fstring.format(*vals)
    print ''
