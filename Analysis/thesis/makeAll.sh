###########################
#### PLOTTING SCRIPTS #####
###########################

# vertex fit efficiencies
python makeVertexFitPlots.py --square

# comparing DSA and RSA efficiencies
python makeDSAvsRSAPlots.py --square --trigger
python makeDSAvsRSAPlots.py --square

# quality cut resolutions and PAT replacements
# For the MC replacement numbers, run printIntegrals for Lxy-before and Lxy-after
# python ../dumpers/printIntegrals.py -f roots/RepEffectPlots_MC.root -k Lxy-after -m
# python ../dumpers/printIntegrals.py -f roots/RepEffectPlots_MC.root -k Lxy-before -m
python makeQualityCutResolutionsAndReplacementEffectPlots.py --square
python makeReplacementEffectSignalPlots.py

# pairing criteria plots
python makePairingCriteriaPlots.py --square

# HLT RECO efficiencies -- not a plot anymore
echo -e "\033[1m***** HLT RECO MATCHING EFFICIENCIES *****\033[m"
python makeHLTRECOPlots.py
echo -e "\033[1m***** HLT RECO MATCHING EFFICIENCIES *****\033[m"

#################
#### HADDING ####
#################

#
# (just saving them here)
#
# hadd RepEffectPlots_Signal.root RepEffectPlots_Trig_HTo2XTo2Mu2J_*; mv RepEffectPlots_Trig_HTo2XTo2Mu2J_* tmp/
# hadd RepEffectPlots_MC.root RepEffectPlots_{DY10to50,DY50toInf,ttbar,tbarW,tW,WZ,ZZ,WW,WJets,QCD20toInf-ME}*.root; mv {DY10to50,DY50toInf,ttbar,tbarW,tW,WZ,ZZ,WW,WJets,QCD20toInf-ME}*.root tmp/;
# for fs in 2Mu2J 4Mu; do hadd PairingCriteriaPlots_Trig_HTo2XTo${fs}.root PairingCriteriaPlots_Trig_HTo2XTo${fs}_*.root; mv PairingCriteriaPlots_Trig_HTo2XTo${fs}_*.root tmp/; done
