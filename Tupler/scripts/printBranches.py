#!/usr/bin/python -u

NOCOLOR = False

COLS       =                ('Type'    , 'Module'  , 'Label'   , 'Process' )

maxLengths = dict(zip(COLS, (        50,         50,         30,          7)))
tempCols   = dict(zip(COLS, (        '',         '',         '',         '')))
colorCodes = dict(zip(COLS, ('\033[31m', '\033[32m', '\033[34m', '\033[35m')))

FSTRING  = ' '.join(['{START}' + colorCodes[key] + '{' + key + ':' + str(maxLengths[key]) + 's}' + '\033[m' for key in COLS])
TFSTRING = FSTRING.replace('{START}','\033[1m')
DFSTRING = FSTRING.replace('{START}','')

if NOCOLOR:
	for key in COLS:
		TFSTRING = TFSTRING.replace(colorCodes[key], '')
		DFSTRING = DFSTRING.replace(colorCodes[key], '')
	TFSTRING = TFSTRING.replace('\033[1m', '')
	
def printContent(cols):
	FFSTRING = TFSTRING if cols['Type'] == 'Type' else DFSTRING
	print FFSTRING.format(**cols)

printContent(dict(zip(COLS,COLS)))
with open('fullAODBranchListRaw.txt') as f:
	for line in f:
		if line[0:4] == 'Type': continue
		if '----------' in line: continue

		cols = line.rstrip('\n').split()

		for i,key in enumerate(COLS):
			tempCols[key] = cols[i].strip('"')
			if len(tempCols[key]) > maxLengths[key]:
				tempCols[key] = tempCols[key][0:maxLengths[key]-3] + '...'

		printContent(tempCols)
