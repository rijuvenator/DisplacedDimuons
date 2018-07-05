import os
import subprocess as bash
import ROOT as R

DIR = '/eos/cms/store/user/adasgupt/DisplacedDimuons/NTuples/'
COMMAND = r'''echo 't=tt("SimpleNTupler/DDTree",_file0);cout << t->GetEntries() << endl;' | \root -l {FNAME}'''

fileList = os.listdir(DIR)[2:]
tagList = [fname.replace('ntuple_','').replace('.root','') for fname in fileList]
maxLen = max([len(t) for t in tagList])

def humanSize(size):
    if   size >= 2**10 and size < 2**20:
        return '{:>6.2f}K'.format(float(size)/(2**10))
    elif size >= 2**20 and size < 2**30:
        return '{:>6.2f}M'.format(float(size)/(2**20))
    elif size >= 2**30 and size < 2**40:
        return '{:>6.2f}G'.format(float(size)/(2**30))
    elif size >= 2**40 and size < 2**50:
        return '{:>6.2f}T'.format(float(size)/(2**40))

for tag, fname in zip(tagList, fileList):
    size = os.path.getsize(DIR+fname)
    friendlySize = humanSize(size)

    nEntries = int(bash.check_output(COMMAND.format(FNAME=DIR+fname), shell=True).split('\n')[-2])
    print '{FNAME:{LEN:d}s} {SIZE:6s} {N:>8d}'.format(FNAME=tag, LEN=maxLen, SIZE=friendlySize, N=nEntries)