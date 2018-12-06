import subprocess as bash

# Configuration for piloting a plotting script
# Contains a template bash script which relinks the root file and
# runs the plotting script with the right arguments
# ftag = "file name tag", e.g. DimuonPlots, SignalRecoEffPlots
# plottingScriptName: usually make + ftag
# fcutstring: the file name "cut string", i.e. stuff at the end
# args: the args to be passed to the plotting script
# script: wrapper for formatting the template bash script with the parameters
# str: summary of what will be done
# run: writes the script, runs it, and deletes it
class Configuration(object):

    bashScript = '''
MAINDIR='../analyzers/roots/Main/'
PLOTTERDIR='../../../plotters/'

cd $MAINDIR
../relink {ftag} {fcutstring}
if [ ! -e "{ftag}.root" ]
then
    echo "Bad symlink"
    cd $PLOTTERDIR
    exit
fi
cd $PLOTTERDIR
python {plottingScriptName}.py {args}
'''

    def __init__(self, ftag, plottingScriptName, fcutstring, args):
        self.ftag               = ftag
        self.plottingScriptName = plottingScriptName
        self.fcutstring         = fcutstring
        self.args               = args

    def script(self):
        return Configuration.bashScript.format(**self.__dict__)

    def __str__(self):
        return 'Link {ftag} with {fcutstring}, then do python {plottingScriptName}.py {args}'.format(**self.__dict__)

    def run(self):
        f = open('script.sh', 'w')
        f.write(self.script())
        f.close()
        bash.call('bash script.sh', shell=True)
        bash.call('rm script.sh'  , shell=True)

# list of configs. All of them will be run at the bottom of the file
CONFIGS = []

# section for MC/Data type plots, e.g. dimuon, recoMuon, with
# various sets of cuts, for prompt and not prompt, etc.
# loops over bits of strings and puts them together in the right way
# comment out the FTAGS, MCBGCutsets, etc. that sort of thing to run a subset
if False:
    FTAGS = (
        'Dimuon',
        'RecoMuon',
    )
    MCBGRegions = (
        ('Prompt'  , '_NoSignal'),
        ('NoPrompt', '_MCOnly'  ),
    )
    MCBGCutsets = (
        ''                     ,
        '_NS'                  ,
        '_NS_NH'               ,
        '_NS_NH_FPTE'          ,
        '_NS_NH_FPTE_HLT'      ,
        '_NS_NH_FPTE_HLT_PT'   ,
        '_NS_NH_FPTE_HLT_PT_PC',
    )
    for ftagroot in FTAGS:
        ftag   = ftagroot+'Plots'
        psname = 'make'+ftag
        for region, regionTag in MCBGRegions:
            for cutset in MCBGCutsets:
                fcutstring = region + cutset + regionTag
                rcutstring = '--cutstring {}_{}'.format(cutset, region)
                mconly     = '--mconly' if region == 'NoPrompt' else ''
                args       = '{} {}'.format(mconly, rcutstring)

                CONFIGS.append(Configuration(ftag, psname, fcutstring, args))

# section for signal type plots
# most signal plotters only care about trigger vs. not trigger
# signal reco res splits final state over two instances
if False:
    ARGS = (
        ('Full', ''         ),
        ('Trig', '--trigger'),
    )
    SIGS = (
        'Dimuon',
        'RecoMuon',
        'SignalRecoRes',
        'SignalRecoEff',
        'SignalVertexFitEff',
    )
    for sig in SIGS:
        ftag   = sig+'Plots'
        psname = 'make'+ftag
        for fcutstring, args in ARGS:
            fcs = fcutstring
            if 'Signal' not in sig:
                fcs += '_SignalOnly'
            if sig == 'SignalRecoRes':
                for fs in ('2Mu2J', '4Mu'):
                    margs = args + ' --fs ' + fs
                    CONFIGS.append(Configuration(ftag, psname, fcs, margs))
            else:
                CONFIGS.append(Configuration(ftag, psname, fcs, args))

# run everything
for c in CONFIGS:
    print c
    c.run()
