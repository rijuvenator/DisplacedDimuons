# this script takes the output of studyPATMuons for MC
# makes a summary table "replaceMC" but adds DY and ttbar together
# in the process

f = open('text/MCDump.txt')
data = {}
order = []
for line in f:
    line = line.strip('\n')
    cols = line.split()
    ints = map(int, cols[1:3]+cols[4:8])
    if cols[0] not in data:
        data[cols[0]] = ints
        order.append(cols[0])
    else:
        for di, addVal in enumerate(ints):
            data[cols[0]][di] += addVal

for key in order:
    print '{:13s} {:9d} {:9d} {:7.4f} {:9d} {:9d} {:9d} {:9d}'.format(
        key,
        data[key][0],
        data[key][1],
        100.*float(data[key][1])/data[key][0],
        data[key][2],
        data[key][3],
        data[key][4],
        data[key][5],
    )
