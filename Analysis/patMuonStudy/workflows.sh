#### current cut string

_Combined_NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M_CHI2_D0SIG

# for 2D plots

{Full,Major,DY50toInf,QCD20toInf-ME,WJets,ttbar}

{chi2,highPurity,isGlobal,nPxlHit,nTrkLay}

2Mu2J_{Global,400_50_800,400_50_80,400_50_8,400_20_400,400_20_40,400_20_4,400_150_4000,400_150_400,400_150_40,200_50_2000,200_50_200,200_50_20,200_20_700,200_20_70,200_20_7,125_50_5000,125_50_500,125_50_50,125_20_1300,125_20_130,125_20_13,1000_50_400,1000_50_40,1000_50_4,1000_350_3500,1000_350_350,1000_350_35,1000_20_200,1000_20_20,1000_20_2,1000_150_1000,1000_150_100,1000_150_10}

# 5 sets of cuts
Combined_{NS_NH_FPTE_HLT_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M_CHI2,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M_CHI2_D0SIG}

# 10 MC samples

{DY10to50,DY50toInf,ttbar,tbarW,tW,WZ,ZZ,WW,WJets,QCD20toInf-ME}

# 10 MC -> one MC file

for i in Combined_{}; do hadd ZephyrPlots${i}_MC.root ZephyrPlots_${i}_{DY10to50,DY50toInf,ttbar,tbarW,tW,WZ,ZZ,WW,WJets,QCD20toInf-ME}.root; mv ZephyrPlots_${i}_{DY10to50,DY50toInf,ttbar,tbarW,tW,WZ,ZZ,WW,WJets,QCD20toInf-ME}.root tmp/; done

# signal -> one file

for i in Trig_Combined_{}_HTo2XTo2Mu2J; do rehadd ZephyrPlots_${i}; mv ZephyrPlots_${i}_HTo2XTo2Mu2J_*.root tmp/; done

# combining PDFs of distributions for various cuts
for rt in DSA HYB PAT
do
    for qt in LxySig d0Sig vtxChi2
    do
        for pt in 2Mu2J MC
        do pdfunite {NS_NH_FPTE_HLT_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M_CHI2,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M_CHI2_D0SIG}/ZEP_${qt}_${rt}_*_${pt}.pdf Combo_${qt}_${rt}_${pt}.pdf
        done
    done
done

# parallel plots + organize into subdirectories

parallel python makeZephyrPlots.py --cutstring ::: {NS_NH_FPTE_HLT_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M_CHI2,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M_CHI2_D0SIG}

for cs in {NS_NH_FPTE_HLT_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M_CHI2,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M_CHI2_D0SIG};
do
    mkdir -p pdfs/${cs}/
    mv pdfs/ZEP*${cs}_{MC,2Mu2J}*.pdf pdfs/${cs}/
done
