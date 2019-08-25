from DisplacedDimuons.Common.Constants import SIGNALPOINTS, SIGNALS
import re

# from makeLimits.py, there's an option to just print the sp, :::, exp, obs
# this takes in that file (with .2e as number format for limit) and outputs a latex table
# for my thesis

data = {}
with open('table2') as f:
    for line in f:
        cols = line.strip('\n').split()
        sp = tuple(map(int, cols[:3]))
        data[sp] = cols[4:]

fstring = '${} \\times 10^{{{}}}$ & ${} \\times 10^{{{}}}$'
for sp in SIGNALPOINTS:
    if sp not in data:
        print '- & -'
        continue
    tokens = []
    for text in data[sp]:
        m = re.match(r'(\d\.\d\d)e([-+]\d\d)', text)
        tokens.append(m.group(1))
        tokens.append(int(m.group(2))-2)
    print fstring.format(*tokens)
    if sp[-1] == SIGNALS[sp[0]][sp[1]][-1]:
        print ''
