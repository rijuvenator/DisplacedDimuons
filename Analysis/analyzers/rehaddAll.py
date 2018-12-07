#!/usr/bin/env python2
import os, argparse, glob
import subprocess as bash
from DisplacedDimuons.Common.Utilities import SPStr
from DisplacedDimuons.Common.Constants import SIGNALPOINTS

# some constants
MCBGLIST = ('WJets', 'WW', 'WZ', 'ZZ', 'tW', 'tbarW', 'ttbar', 'QCD20toInf-ME', 'DY10to50', 'DY50toInf')
ROOTSDIR = os.environ['CMSSW_BASE']+'/src/DisplacedDimuons/Analysis/analyzers/roots/'
COLORS = {'black':0, 'red':31, 'green':32, 'yellow':33, 'blue':34, 'magenta':35, 'teal':36, 'gray':37}

# functions for interacting with the command line and file system
def cd(d):
    os.chdir(d)
def run(cmd):
    if type(cmd) == str:
        bash.call(cmd, shell=True)
    else:
        bash.call(cmd)
def get(cmd):
    try:
        return bash.check_output(cmd, shell=True).strip('\n').split('\n')
    except bash.CalledProcessError:
        return []
def colstring(string, col='black'):
    if col == 'black':
        return string
    else:
        return '\033['+str(COLORS[col])+'m'+string+'\033[m'
def msg(string, col='red'):
    print colstring(string, col)

# parser
# modes:      split  = rehadd the split up roots from big samples;
#             move   = move files from roots/ to subfolders;
#             rehadd = grab files from subfolders and make hadded roots
# tags:       e.g. Dimuon, RecoMuon, etc.
#             specify --noPlots if adding Plots onto the end of each tag is not desired
# samples:    sample names, or codes such as "bigMC", "data", "all4Mu", "all2Mu2J"
# dirs:       in split mode, 1-2 directories to which to move the _* numbered split files and to which to cd
#             in rehadd mode, directories from which to look for tags and hadd together
# cutstrings: in move mode, string in between tag and sample, i.e. tag_CS_sample.root
#             specifies what directories to make, what files to move into them

parser = argparse.ArgumentParser()
parser.add_argument('--mode'      , dest='MODE'      ,            default='split'               , choices=['split', 'rehadd', 'move'])
parser.add_argument('--tags'      , dest='TAGS'      , nargs='+', default=['RecoMuon', 'Dimuon']                                     )
parser.add_argument('--samples'   , dest='SAMPLES'   , nargs='+', default=['bigMC', 'data']                                          )
parser.add_argument('--dirs'      , dest='DIRS'      , nargs='+', default=['tmp']                                                    )
parser.add_argument('--cutstrings', dest='CUTSTRINGS', nargs='+', default=[]                                                         )
parser.add_argument('--suffix'    , dest='SUFFIX'    ,            default=''                                                         )
parser.add_argument('--noPlots'   , dest='NOPLOTS'   ,                                            action='store_true'                )
ARGS = parser.parse_args()

# for convenience
MODE       = ARGS.MODE
TAGS       = ARGS.TAGS
DIRS       = ARGS.DIRS
SUFFIX     = ARGS.SUFFIX
CUTSTRINGS = ARGS.CUTSTRINGS

# bigMC, data, etc. are codes for a certain collection of sample names
# tuples are given in case short tags are desired someday, e.g. D, B, S, S2
SAMPLES = []
if any([test in ARGS.SAMPLES for test in ('bigMC',)]):
    SAMPLES.extend(['DY50toInf', 'ttbar'])
if any([test in ARGS.SAMPLES for test in ('data',)]):
    SAMPLES.extend(['DoubleMuonRun2016{}-07Aug17{}'.format(era, '-v2' * (era=='B')) for era in ('B', 'C', 'D', 'E', 'F', 'G', 'H')])
if any([test in ARGS.SAMPLES for test in ('all4Mu',)]):
    SAMPLES.extend(['HTo2XTo4Mu_'+SPStr(sp) for sp in SIGNALPOINTS])
if any([test in ARGS.SAMPLES for test in ('all2Mu2J',)]):
    SAMPLES.extend(['HTo2XTo2Mu2J_'+SPStr(sp) for sp in SIGNALPOINTS])
if True:
    SAMPLES.extend([s for s in ARGS.SAMPLES if s not in ['bigMC', 'data', 'all4Mu', 'all2Mu2J']])

# if --noPlots is given, don't add Plots onto the end of every tag
if not ARGS.NOPLOTS:
    TAGS = [t+'Plots' for t in TAGS]

# make sure this is what is desired
if MODE == 'split':
    FOLDER = '' if len(DIRS) < 2 else DIRS[1]
    answer = raw_input('''Will
  cd to {}
  rehadd {}{} for {}
  move all _* to {}
OK? [y/n] '''.format(
        colstring('roots/'+FOLDER                        , col='blue'   ),
        colstring(' '.join(ARGS.TAGS)                    , col='green'  ),
        colstring(' (+Plots)' if not ARGS.NOPLOTS else '', col='red'    ),
        colstring(' '.join(ARGS.SAMPLES)                 , col='teal'   ),
        colstring(DIRS[0]                                , col='magenta'))
    )

elif MODE == 'move':
    answer = raw_input('''Will
  cd to {}
  for {}
  move all Data/MC/Signal to {}
OK? [y/n] '''.format(
        colstring('roots/'                 , col='blue' ),
        colstring(' '.join(ARGS.TAGS)      , col='green'),
        colstring(' '.join(ARGS.CUTSTRINGS), col='teal' ))
    )

elif MODE == 'rehadd':
    answer = raw_input('''Will
  cd to {}
  get files from {}
  hadd {}{} with all of them
  rename by adding {}
OK? [y/n] '''.format(
        colstring('roots/'                                         , col='blue'   ),
        colstring(' '.join(ARGS.DIRS)                              , col='teal'   ),
        colstring(' '.join(ARGS.TAGS)                              , col='green'  ),
        colstring(' (+Plots)' if not ARGS.NOPLOTS else ''          , col='red'    ),
        colstring(ARGS.SUFFIX if ARGS.SUFFIX != '' else '<nothing>', col='magenta'))
    )
if answer.lower() == 'y':
    pass
elif answer.lower() == 'n':
    print 'OK, exiting now.'
    exit()
else:
    print 'Please type y or n; exiting now.'
    exit()

# run the commands

# rehadd split files
if MODE == 'split':
    FOLDER = '' if len(DIRS) < 2 else DIRS[1]
    msg('cd to roots/{} and making {}'.format(FOLDER, DIRS[0]))
    cd('roots/'+FOLDER)
    dirs = DIRS[0]
    run(['mkdir', '-p', dirs])
    for tag in TAGS:
        for sample in SAMPLES:
            msg('rehadding {} for {}'.format(sample, tag))
            run('{}rehadd {}'.format(ROOTSDIR, tag+'_'+sample))
            msg('moving {} for {} _* splits to {}'.format(sample, tag, dirs))
            run(['mv'] + glob.glob(tag+'_'+sample+'_*') + [dirs])
            if FOLDER != '':
                msg('moving hadded {} {} to roots/'.format(tag, sample))
                run(['mv', tag+'_'+sample+'.root', ROOTSDIR])

# move data, MC, Signal files to subfolders
elif MODE == 'move':
    msg('cd to roots/')
    cd('roots/')
    def CS(cs):
        return '' if cs == '' else '_'+cs
    for tag in TAGS:
        for cutstring in CUTSTRINGS:
            cs = CS(cutstring)
            dname = 'Data'+cs
            # try data
            if glob.glob('{}{}_DoubleMuon*.root'.format(tag, cs)) != []:
                msg('making {} and moving files to it'.format(dname))
                run(['mkdir', '-p', dname])
                run(['mv'] + glob.glob(tag+cs+'_DoubleMuon*.root') + [dname])

            # try MC
            files = []
            for sample in MCBGLIST:
                if os.path.isfile('{}{}_{}.root'.format(tag, cs, sample)):
                    files.append('{}{}_{}.root'.format(tag, cs, sample))
            if len(files) > 0:
                dname = 'MC'+cs
                msg('making {} and moving files to it'.format(dname))
                run(['mkdir', '-p', dname])
                for f in files:
                    run(['mv', f, dname])

            # try signal
            if glob.glob('{}{}_HTo2XTo*.root'.format(tag, cs)) != []:
                dname = 'Signal'+cs
                msg('making {} and moving files to it'.format(dname))
                run(['mkdir', '-p', dname])
                run(['mv'] + glob.glob(tag+cs+'_HTo2XTo*.root') + [dname])

            # try trig-signal
            if glob.glob('{}{}_Trig-HTo2XTo*.root'.format(tag, cs)) != []:
                msg('making {} and moving files to it'.format(dname))
                run(['mkdir', '-p', dname])
                run(['mv'] + glob.glob(tag+cs+'_Trig-HTo2XTo*.root') + [dname])

# rehadd the Main files
elif MODE == 'rehadd':
    msg('cd to roots/')
    cd('roots/')
    for tag in TAGS:
        files = []
        for dirs in DIRS:
            files.extend(glob.glob('{}/{}*'.format(dirs, tag)))
        msg('hadding {} with {}'.format(tag, ' '.join(DIRS)))
        run(['hadd', tag+'.root'] + files)
        if SUFFIX != '':
            msg('renaming {} to {}'.format(tag+'.root', tag+'_'+SUFFIX+'.root'))
            run(['mv', tag+'.root', tag+'_'+SUFFIX+'.root'])


''' EXAMPLE WORKFLOW

=== HADD SPLIT ===

python rehaddAll.py --mode split --tags {Dimuon,RecoMuon}Plots_Prompt_NS_NH{,_FPTE} --dirs tmp mcbg --samples bigMC data --noPlots

This will
  - cd to roots/mcbg
  - make tmp
  - hadd together the bigMC and the data samples for each tag
  - tags include the cutstring
  - since the Plots are already in the tag, --noPlots is specified
  - since mcbg is given, the resulting root file will be moved

Any remaining root files can be moved with mv *.root ~/DDAnalysis/roots/

=== MOVE ===

python rehaddAll.py --mode move --tags Dimuon RecoMuon --cutstrings Prompt_NS_NH{,FPTE}

This will
  - cd to roots/
  - make a Data/MC/Signal_cutstring folder for each cutstring
  - move tag_cutstring_DoubleMuon* to Data
  - move tag_cutstring_MCs (explicit) to MC
  - move tag_cutstring_Signals to Signal

One command is enough for all unique cutstrings

=== HADD MAIN ===

python rehaddAll.py --mode rehadd --tags Dimuon RecoMuon --dirs {Data,MC}_Prompt --suffix Prompt_NoSignal

This will
  - cd to roots/
  - gather all the files from Data_Prompt/ and MC_Prompt/
  - hadd them together
  - rename the file by adding _Prompt_NoSignal before the .root

This needs one command for each cutstring. So one should do for example:

for cs in {NS,NS_{NH,NH_{FPTE,FPTE_{HLT,HLT_PT}}}}
do
    python rehaddAll.py --mode rehadd --tags Dimuon RecoMuon --dirs {Data,MC}_Prompt_${cs} --suffix   Prompt_${cs}_NoSignal
    python rehaddAll.py --mode rehadd --tags Dimuon RecoMuon --dirs      MC_NoPrompt_${cs} --suffix NoPrompt_${cs}_MCOnly
done
'''
