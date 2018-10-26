import subprocess as bash

# wrapper for shell=True
def run(command):
    bash.call(command, shell=True)

# script template
bashScript = '''
MAINDIR='../analyzers/roots/Main/'
PLOTTERDIR='../../../plotters/'

cd $MAINDIR
../relink {tag} {cutstring}
if [ ! -e "{tag}.root" ]
then
    echo "Bad symlink"
    cd $PLOTTERDIR
    exit
fi
cd $PLOTTERDIR
python {scriptName}.py {realcutstring} {mconly} {trigger}
'''

# file name tag : plotter script name
MCBGscripts = (
    ('DimuonPlots'  , 'makeDimuonPlots'  ),
    ('RecoMuonPlots', 'makeRecoMuonPlots'),
)

# file name cutstring : trigger flag : mconly flag : real cutstring
MCBGcutstrings = (
    ('Prompt_NoSignal'            , '', ''        , '--cutstring _Prompt'             ),
    ('Prompt_NS_NoSignal'         , '', ''        , '--cutstring _NS_Prompt'          ),
    ('Prompt_NS_NH_NoSignal'      , '', ''        , '--cutstring _NS_NH_Prompt'       ),
    ('Prompt_NS_NH_FPTE_NoSignal' , '', ''        , '--cutstring _NS_NH_FPTE_Prompt'  ),

    ('NoPrompt_MCOnly'            , '', '--mconly', '--cutstring _NoPrompt'           ),
    ('NoPrompt_NS_MCOnly'         , '', '--mconly', '--cutstring _NS_NoPrompt'        ),
    ('NoPrompt_NS_NH_MCOnly'      , '', '--mconly', '--cutstring _NS_NH_NoPrompt'     ),
    ('NoPrompt_NS_NH_FPTE_MCOnly' , '', '--mconly', '--cutstring _NS_NH_FPTE_NoPrompt'),
)

# file name tag : plotter script name
Signalscripts = (
    ('SignalRecoResPlots', 'makeSignalRecoResPlots')
)

# file name cutstring : trigger flag : mconly flag : real cutstring
Signalcutstrings = (
    ('Full', ''         , '', ''),
    ('Trig', '--trigger', '', '')
)


# actual for loop
#for scripts, cutstrings in ((MCBGscripts, MCBGcutstrings), (Signalscripts, Signalcutstrings))
for scripts, cutstrings in ((MCBGscripts, MCBGcutstrings),)
for tag, scriptName in scripts:
    for cutstring, trigger, mconly, realcutstring in cutstrings:
        f = open('script.sh', 'w')
        f.write(bashScript.format(**locals()))
        f.close()
        run('bash script.sh')
        run('rm script.sh')
