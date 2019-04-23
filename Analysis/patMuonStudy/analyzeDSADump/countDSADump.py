f = open('/afs/cern.ch/user/a/adasgupt/public/Last21DataEventDumps.txt')
startRecording = False
for line in f:
    if '=====' in line:
        cols = line.strip('\n').split()
        event = int(cols[4])
        cosA = float(cols[-6])
    if '=== DSA MUON' in line:
        startRecording = True
    if startRecording and line == '\n':
        cols = prevLine.strip('\n').split()
        print event, cosA, int(cols[0]) + 1
        startRecording = False
        continue
    if startRecording:
        prevLine = line
