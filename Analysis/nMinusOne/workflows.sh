# rehadd

rehaddAll.py --mode split --tags NM1Plots --dirs tmp mcbg --samples bigMC data --noPlots --noMove

# 10 MC samples

{DY10to50,DY50toInf,ttbar,tbarW,tW,WZ,ZZ,WW,WJets,QCD20toInf-ME}

# 10 MC -> one MC file

for i in ""
do
    hadd NM1Plots${i}_MC.root NM1Plots${i}_{DY10to50,DY50toInf,ttbar,tbarW,tW,WZ,ZZ,WW,WJets,QCD20toInf-ME}.root
    mv NM1Plots${i}_{DY10to50,DY50toInf,ttbar,tbarW,tW,WZ,ZZ,WW,WJets,QCD20toInf-ME}.root tmp/
done

# signal -> one file

for i in _Trig_HTo2XTo2Mu2J
do
    rehadd NM1Plots${i}
    mv NM1Plots${i}_*.root tmp/
done

# data -> one file

for i in ""
do
    hadd NM1Plots${i}_DATA.root NM1Plots${i}_DoubleMuon*.root
    mv NM1Plots${i}_DoubleMuon*.root tmp/
done

##########
##########

# rehadd

rehaddAll.py --mode split --tags NM1Distributions_IDPHI --dirs tmp mcbg --samples bigMC data --noPlots --noMove
rehaddAll.py --mode split --tags NM1Distributions       --dirs tmp mcbg --samples bigMC data --noPlots --noMove

# 10 MC samples

{DY10to50,DY50toInf,ttbar,tbarW,tW,WZ,ZZ,WW,WJets,QCD20toInf-ME}

# 10 MC -> one MC file

for i in "" "_IDPHI"
do
    hadd NM1Distributions${i}_MC.root NM1Distributions${i}_{DY10to50,DY50toInf,ttbar,tbarW,tW,WZ,ZZ,WW,WJets,QCD20toInf-ME}.root
    mv NM1Distributions${i}_{DY10to50,DY50toInf,ttbar,tbarW,tW,WZ,ZZ,WW,WJets,QCD20toInf-ME}.root tmp/
done

# signal -> one file

for i in _Trig_HTo2XTo2Mu2J
do
    rehadd NM1Distributions${i}
    mv NM1Distributions${i}_*.root tmp/
done

# data -> one file

for i in "" "_IDPHI"
do
    hadd NM1Distributions${i}_DATA.root NM1Distributions${i}_DoubleMuon*.root
    mv NM1Distributions${i}_DoubleMuon*.root tmp/
done

