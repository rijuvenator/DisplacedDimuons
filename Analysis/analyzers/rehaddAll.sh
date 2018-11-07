#!/bin/bash

# Mode: start with option C when newly produced root files from batch
read -p '[C]ombine final split files, or [R]ehadd Main files? [CR] '
echo

if [ "$REPLY" == "C" ]
then

    # These tags will be hadded together sample_0 ... sample_N
    read -p $'Split tags to combine...\ndefault : RecoMuon Dimuon nMinusOne nMinusOneEff\nsomething else? '
    if [ -z "$REPLY" ]
    then
        SPLITTAGS="RecoMuon Dimuon nMinusOne nMinusOneEff"
    else
        SPLITTAGS="$REPLY"
    fi
    echo

    # These are the samples to be hadded above
    read -p $'Samples to combine...\ndefault : DY50toInf ttbar DoubleMuonRun2016B-07Aug17-v2 DoubleMuonRun2016{C,D,E,F,G,H}-07Aug17\nsomething else? '
    if [ -z "$REPLY" ]
    then
        SAMPLES=$(echo DY50toInf ttbar DoubleMuonRun2016B-07Aug17-v2 DoubleMuonRun2016{C,D,E,F,G,H}-07Aug17)
    else
        SAMPLES=$(eval echo $REPLY)
    fi
    echo

    # This hadds together sample_0 ... sample_N
    # This only needs to be done for data, DY50toInf, and ttbar
    pushd roots
    for i in $SPLITTAGS
    do
        for s in $SAMPLES
        do
            ./rehadd ${i}Plots_${s}
        done
    done
    echo

    # This directory will be where all the split files go
    read -p $'Directory to move all the split samples...\ndefault : tmp\nsomething else? '
    if [ -z "$REPLY" ]
    then
        TMP='tmp'
    else
        TMP="$REPLY"
    fi
    echo

    # Move all the sample_* to a directory, so that they do not interfere with hadd
    mkdir -p $TMP
    for i in $SPLITTAGS
    do
        for s in $SAMPLES
        do
            mv ${i}Plots_${s}_* $TMP
        done
    done

# at this point, move data files to data, MC BG, Signal4Mu, and Signal2Mu2J to appropriate directories
# then rerun with option R instead of option C

elif [ "$REPLY" == "R" ]
then

    pushd roots
    # Give an explicit list of directories
    read -p $'Directories to look for files to hadd?\ndefault : Data_Prompt MC_Prompt Signal\nsomething else? '
    if [ -z "$REPLY" ]
    then
        DIRS='Data_Prompt MC_Prompt Signal'
    else
        DIRS="$REPLY"
    fi
    echo

    # Give an explicit list of tags
    read -p $'Tags to rehadd?\ndefault : RecoMuon Dimuon nMinusOne nMinusOneEff SignalRecoEff SignalVertexFitEff SignalRecoRes TailCumulative\nsomething else? '
    if [ -z "$REPLY" ]
    then
        TAGS='RecoMuon Dimuon nMinusOne nMinusOneEff SignalRecoEff SignalVertexFitEff SignalRecoRes TailCumulative'
    else
        TAGS="$REPLY"
    fi
    echo

    # rehadd
    for i in $TAGS
    do
        FILES=""
        for d in $DIRS
        do
            FILES+="${d}/${i}Plots* "
        done
        echo "Rehadding ${i}Plots.root with $DIRS"
        hadd ${i}Plots.root $FILES
    done
    echo

    # Rename output file
    read -p $'Optional output file suffix?\ndefault : <none> (e.g. Blind)\nsomething else? '
    if [ -z "$REPLY" ]
    then
        :
    else
        for i in $TAGS
        do
            echo "Moving ${i}Plots.root to ${i}Plots_${REPLY}.root"
            mv ${i}Plots.root ${i}Plots_${REPLY}.root
        done
    fi
    popd

fi
