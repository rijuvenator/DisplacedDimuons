#!usr/bin/python
import os
import optparse 
import sys 
import subprocess
import datetime 
import re

basedir_path = os.path.dirname(os.path.realpath(__file__))
#print basedir_path

madgraph_dir = "" #working here (not needed here)
#card_dir = "HiggsPortalLongLivedDarkPhoton_Cards/"
prod_dirname = "HiggsPortalLongLivedDarkPhoton_Cards/"

usage = ""
parser = optparse.OptionParser(usage='\nExample: python %prog -i template_cards/TrijetRes_g_ggg_BP1 -n TrijetRes_g_ggg_BP1 \n1) Create template_cards/TrijetRes_g_ggg_BP1 directory containing config files for madgraph (i.e. PROCESSNAME_customizecards.dat, PROCESSNAME_proc_card.dat, PROCESSNAME_extramodels.dat, PROCESSNAME_run_card.dat) \n2) Edit %prog to specify the parameters of the samples to be produced (i.e. DP and EPSILON) \n3) Launch the script %prog')
parser.add_option("-i","--inputCardDir",action="store",type="string",dest="INPUTCARDDIR",default="")
parser.add_option("-n","--genProcessName",action="store",type="string",dest="GENPROCESSNAME",default="")

#Example:  python createGridpacks_darkPhoton.py -i HiggsPortalLongLivedDarkPhoton_TemplateCards -n LL_HAHM_MS_400_kappa_0p01

(options, args) = parser.parse_args()
INPUTCARDDIR = options.INPUTCARDDIR
GENPROCESSNAME = options.GENPROCESSNAME

if not options.INPUTCARDDIR:   
    parser.error('ERROR: Input card directory is not given')
if not options.GENPROCESSNAME:   
    parser.error('ERROR: Gen process name is not given')

# Create outputgridpack dir
current_time = datetime.datetime.now()
#GENPROCESSDIRNAME = GENPROCESSNAME+"_%04d%02d%02d_%02d%02d%02d" % (current_time.year,current_time.month,current_time.day,current_time.hour,current_time.minute,current_time.second)
#OUTPROCESSDIR = basedir_path+"/"+prod_dirname+"/"+GENPROCESSDIRNAME
OUTPROCESSDIR = basedir_path+"/"+prod_dirname+"/"
print ("mkdir -p %s" % OUTPROCESSDIR)
os.system("mkdir -p %s" % OUTPROCESSDIR)

print "The input card directory is:", INPUTCARDDIR
print "The output gridpacks directory is:", OUTPROCESSDIR
print "The gen process name is:", GENPROCESSNAME

# Create cards and run gridpacks

#Here one defines the grin in dark photon mass and epsilon
#10 GeV -> [1e-06, 1e-07, 1e-08]
#20 GeV -> [7e-07, 5e-08, 5e-09]
#30 GeV -> [1e-07, 5e-08, 5e-09]
#40 GeV -> [1e-07, 5e-08, 1e-09]
#50 GeV -> [1e-07, 1e-08, 1e-09]
#60 GeV -> [1e-07, 1e-08, 1e-09, 1e-10] 

##PARAMETERValues = []
#PARAMETERValues.append({"DP": 10, "EPSILON":[1e-8]}) # Masess are in GeV   
#PARAMETERValues.append({"DP": 20, "EPSILON":[2.04e-8, 6.46e-8, 2.04e-7]})
#PARAMETERValues.append({"DP": 50, "EPSILON":[5.95e-9, 1.88e-8, 5.95e-8]})

PARAMETERValues = []
PARAMETERValues.append({"DP": 10, "EPSILON":["1e-06", "5e-07", "1e-07", "3e-08"]})
PARAMETERValues.append({"DP": 20, "EPSILON":["5e-07", "2e-07", "5e-08", "1e-08"]})
PARAMETERValues.append({"DP": 30, "EPSILON":["3e-07", "1e-07", "3e-08", "7e-09"]})
PARAMETERValues.append({"DP": 40, "EPSILON":["2e-07", "8e-08", "2e-08", "5e-09"]})
PARAMETERValues.append({"DP": 50, "EPSILON":["2e-07", "6e-08", "1e-08", "4e-09"]})
PARAMETERValues.append({"DP": 60, "EPSILON":["1e-07", "4e-08", "7e-09", "2e-09"]})

DHMASS = 400 # above mH>125 GeV
KAPPA = 0.01 # does not play a role in the kinematics

#Set dark-photon mass
#set param_card hidden 1 DPMASS
#Set dark-higgs mass
#set param_card hidden 2 DHMASS
#Set mixing parameter epsilon
#set param_card hidden 3 EPSILON
#Set mixing parameter kappa
#set param_card hidden 4 KAPPA
#recompute  widths of higgs
#set param_card DECAY  25 AUTO
#recompute width of dark-higgs
#set param_card DECAY  35 AUTO 
#recompute width of dark-photon

for PARAMETER in PARAMETERValues: #loop over dark photon masses
    for kEPSILON in PARAMETER["EPSILON"]: #Loop over epsilon bins for a given mass
        DPMASS = int(PARAMETER["DP"])
        EPSILON = kEPSILON
        print DPMASS, EPSILON

        EPSILONmod = str(EPSILON)   
        EPSILONmod = re.sub("\.","p",EPSILONmod)
        
        CURRENTPROCESS = GENPROCESSNAME+"_"+"MZd_"+str(DPMASS)+"_eps_"+EPSILONmod
        print ("mkdir -p %s/%s" % (OUTPROCESSDIR,CURRENTPROCESS))
        os.system("mkdir -p %s/%s" % (OUTPROCESSDIR,CURRENTPROCESS))

        ##        
        RUNCARD = OUTPROCESSDIR+"/"+CURRENTPROCESS+"/"+CURRENTPROCESS+"_run_card.dat"
        template_runcard = INPUTCARDDIR+"/"+"PROCESSNAME_run_card.dat"
        with open(RUNCARD, "wt") as fout:            
            with open(template_runcard, "rt") as fin:
                for line in fin:
                    ## EDIT CARD
                    ##
                    fout.write(line)

        ##   
        PROCCARD = OUTPROCESSDIR+"/"+CURRENTPROCESS+"/"+CURRENTPROCESS+"_proc_card.dat"
        template_proccard = INPUTCARDDIR+"/"+"PROCESSNAME_proc_card.dat"
        with open(PROCCARD, "wt") as fout:            
            with open(template_proccard, "rt") as fin:
                for line in fin:
                    ## EDIT CARD
                    line = re.sub("PROCESSNAME",CURRENTPROCESS,line)                
                    ##
                    fout.write(line)

        ##
        EXTRAMODCARD = OUTPROCESSDIR+"/"+CURRENTPROCESS+"/"+CURRENTPROCESS+"_extramodels.dat"
        template_extramod = INPUTCARDDIR+"/"+"PROCESSNAME_extramodels.dat"
        with open(EXTRAMODCARD, "wt") as fout:            
            with open(template_extramod, "rt") as fin:
                for line in fin:
                    ## EDIT CARD
                    ##
                    fout.write(line)

        ##
        CUSTOMCARD = OUTPROCESSDIR+"/"+CURRENTPROCESS+"/"+CURRENTPROCESS+"_customizecards.dat"
        template_custom = INPUTCARDDIR+"/"+"PROCESSNAME_customizecards.dat"
        with open(CUSTOMCARD, "wt") as fout:            
            with open(template_custom, "rt") as fin:
                for line in fin:
                    ## EDIT CARD
                    line = re.sub("DPMASS",str(DPMASS),line) 
                    line = re.sub("EPSILON",str(EPSILON),line) 
                    line = re.sub("DHMASS",str(DHMASS),line) 
                    line = re.sub("KAPPA",str(KAPPA),line) 
                    ##
                    fout.write(line)



