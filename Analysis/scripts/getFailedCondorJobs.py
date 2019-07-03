#!/usr/bin/env python2
import subprocess as bash
import re
import glob

def grab(cmd):
    try:
        return bash.check_output(cmd, shell=True).strip('\n')
    except bash.CalledProcessError:
        return ''

def specialGrab():
    try:
        return bash.check_output(['grep',
                                  '-zPl',
                                  '(?s)Could not find platform independent libraries <prefix>\\nCould not find platform dependent libraries <exec_prefix>\\nConsider setting \$PYTHONHOME to <prefix>\[:<exec_prefix>\]\\nTraceback \(most recent call last\):\\n  File ".*\\n    __boot\(\)\\n  File ".*\\n    import sys, os, os.path\\nImportError: No module named os\n.+'] + glob.glob('logs/run*/*.err')).strip('\n')
    except bash.CalledProcessError:
        return ''

def md5Grab():
    try:
        output = bash.check_output(['md5sum'] + glob.glob('logs/run*/*.err')).strip('\n')
        splitOutput = output.split('\n')
        returnList = []
        for line in splitOutput:
            md5, fn = line.split()
            if md5 != 'c61e3e08b799657320164417a3100eda' and md5 != 'd41d8cd98f00b204e9800998ecf8427e':
                returnList.append(fn)
        return '\n'.join(returnList)
    except bash.CalledProcessError:
        return ''

baseNames = {}

# grep for SYSTEM_PERIODIC_REMOVE in .log files
# the grepOutput is a number of lines in which the first column is 'logs/run*/*.log:'
grepOutput = grab('grep SYSTEM_PERIODIC_REMOVE logs/run*/*.log')
baseNames['overtime'] = []
if grepOutput != '':
    for line in grepOutput.split('\n'):
        # just logs/(run\d+/.*)\.log will match the beginning of each line
        baseNames['overtime'].append(re.match(r'logs/(run\d+/.*)\.log', line).group(1))

# find non-empty .err files
# the findOutput is a number of lines consisting of file names of the format 'logs/run*/*.err'
#findOutput = grab('find logs/run*/*.err -type f ! -empty')
#findOutput = specialGrab()
findOutput = md5Grab()
baseNames['errored'] = []
if findOutput != '':
    for line in findOutput.split('\n'):
        # just logs/(run\d+/.*)\.err will match the beginning of each line
        baseNames['errored'].append(re.match(r'logs/(run\d+/.*)\.err', line).group(1))

# print out the jobs found
allBaseNames = []
for key in baseNames:
    allBaseNames.extend(baseNames[key])
    if len(baseNames[key]) > 0:
        print '{} {} jobs found:{}'.format(len(baseNames[key]), key, '\n  '+'\n  '.join(baseNames[key])+'\n')
if len(allBaseNames) == 0:
    print '0 failed jobs found'

# now grep for baseName.err in any condorSubmit_* files and get the arguments line after it
# grepOutput is 2 lines: the first line is the .err, the second line is the arguments, so get the second line
# the second line is of the form 'filename-arguments = <args>', so get everything after the =, strip off the first character (a space)
for baseName in allBaseNames:
    runDir, realBaseName = baseName.split('/')
    grepOutput = grab('grep -A1 {}.err logs/{}/condorSubmit'.format(baseName, runDir))
    # more verbosely:
    #secondLine            = grepOutput          .split('\n')[1]
    #everythingAfterEquals = secondLine          .split('=', 1)[1] # second argument to split means do only 1 split
    #argsWithoutFirstSpace = everythingAfterEquals[1:]
    print grepOutput.split('\n')[1].split('=', 1)[1][1:]
