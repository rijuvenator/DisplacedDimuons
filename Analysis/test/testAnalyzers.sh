#!/bin/bash

pstring='\033[32mANALYZER TEST: Testing \033[34m%s\033[32m%s\033[m'
sstring='\033[32mSuccess.\033[m\n'
fstring='\033[31mFail.\033[m\n'

### TEST ANALYZERS ###
pushd ../analyzers/ >/dev/null

# these scripts run on S B D
for s in dimuonPlots recoMuonPlots nMinusOnePlots tailCumulativePlots
do
    printf "$pstring" $s " on SIGNAL... "
    python ${s}.py --name HTo2XTo4Mu --test >/dev/null 2>&1
    if [ $? -ne 0 ]; then printf $fstring; else printf $sstring; fi

    printf "$pstring" $s " on BACKGROUND... "
    python ${s}.py --name DY100to200 --test >/dev/null 2>&1
    if [ $? -ne 0 ]; then printf $fstring; else printf $sstring; fi

    printf "$pstring" $s " on DATA... "
    python ${s}.py --name DoubleMuonRun2016D-07Aug17 --test >/dev/null 2>&1
    if [ $? -ne 0 ]; then printf $fstring; else printf $sstring; fi

done

# these scripts run on S
for s in signalMatchEffPlots signalMatchResPlots signalMiscPlots
do
    printf "$pstring" $s "... "
    python ${s}.py --name HTo2XTo4Mu --test >/dev/null 2>&1
    if [ $? -ne 0 ]; then printf $fstring; else printf $sstring; fi
done

popd >/dev/null

### TEST DUMPERS ###
pushd ../dumpers/ >/dev/null

# these scripts run on S
for s in cutEfficiencies
do
    printf "$pstring" $s "... "
    python ${s}.py --name HTo2XTo4Mu --test >/dev/null >/dev/null 2>&1
    if [ $? -ne 0 ]; then printf $fstring; else printf $sstring; fi
done

popd >/dev/null
