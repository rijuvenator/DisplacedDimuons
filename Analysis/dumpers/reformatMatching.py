import sys

try:
    f = open(sys.argv[1])
except:
    f = open('text/multipleMatchesAll.txt')

output = ''
for line in f:
    if 'cTau' in line:
        output += line
        continue
    if '----' in line:
        output += line
        continue

    cols = line.strip('\n').split()

    newline = '{:>4s} {:>3s} {:>4s} {:>5s} {:>6s}'.format(*cols[:5])

    percents = []
    nGM = int(cols[4])
    for col in cols[5:]:
        num = float(col)
        s = ' {:>5.2f}%'.format(num/nGM*100.)
        newline += s

    output += newline + '\n'
f.close()

print output

