#!/usr/bin/env python
import subprocess as bash
import re

def grab(cmd):
    try:
        return bash.check_output(cmd, shell=True).strip('\n')
    except bash.CalledProcessError:
        return ''

# grep for SYSTEM_PERIODIC_REMOVE
# the grepOutput is a number of lines in which the first column is 'logs/*.log:'
grepOutput = grab('grep SYSTEM_PERIODIC_REMOVE logs/run*/*.log')
baseNames = []
if grepOutput != '':
    for line in grepOutput.split('\n'):
        # line.split('\n')[0] is the first column
        baseNames.append(re.match(r'logs/(run\d+/.*)\.log', line.split('\n')[0]).group(1))

# print out the jobs found
print '{} removed jobs found:{}'.format(len(baseNames), '\n  '+'\n  '.join(baseNames)+'\n')

# now grep for baseName.err in any condorSubmit_* files and get the arguments line after it
# grepOutput is 2 lines: the first line is the .err, the second line is the arguments, so get the second line
# the second line is of the form 'filename-arguments = <args>', so get everything after the =, strip off the first character (a space)
for baseName in baseNames:
    runDir, realBaseName = baseName.split('/')
    grepOutput = grab('grep -A1 {}.err logs/{}/condorSubmit'.format(baseName, runDir))
    # more verbosely:
    #secondLine            = grepOutput          .split('\n')[1]
    #everythingAfterEquals = secondLine          .split('=')[1]
    #argsWithoutFirstSpace = everythingAfterEquals[1:]
    print grepOutput.split('\n')[1].split('=')[1][1:]
