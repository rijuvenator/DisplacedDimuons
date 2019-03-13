#### current cut string

_Combined_NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M_CHI2_D0SIG


#### combining PDFs so that we don't have a billion files ####

{Full,Major,DY50toInf,QCD20toInf-ME,WJets,ttbar}

{chi2,highPurity,isGlobal,nPxlHit,nTrkLay}

for i in {Full,Major,DY50toInf,QCD20toInf-ME,WJets,ttbar}; do pdfunite ZEP_MC2D_{chi2,highPurity,isGlobal,nPxlHit,nTrkLay}_${i}.pdf       ZEP_MC2D_${i}.pdf; mv ZEP_MC2D_${i}.pdf ../; done
for i in {chi2,highPurity,isGlobal,nPxlHit,nTrkLay}      ; do pdfunite ZEP_MC2D_${i}_{Full,Major,DY50toInf,QCD20toInf-ME,WJets,ttbar}.pdf ZEP_MC2D_${i}.pdf; mv ZEP_MC2D_${i}.pdf ../; done

2Mu2J_{Global,400_50_800,400_50_80,400_50_8,400_20_400,400_20_40,400_20_4,400_150_4000,400_150_400,400_150_40,200_50_2000,200_50_200,200_50_20,200_20_700,200_20_70,200_20_7,125_50_5000,125_50_500,125_50_50,125_20_1300,125_20_130,125_20_13,1000_50_400,1000_50_40,1000_50_4,1000_350_3500,1000_350_350,1000_350_35,1000_20_200,1000_20_20,1000_20_2,1000_150_1000,1000_150_100,1000_150_10}

for i in {}                                              ; do pdfunite ZEP_2D_{chi2,highPurity,isGlobal,nPxlHit,nTrkLay}_${i}.pdf         ZEP_2D_${i}.pdf  ; mv ZEP_2D_${i}.pdf ../  ; done
for i in {chi2,highPurity,isGlobal,nPxlHit,nTrkLay}      ; do pdfunite ZEP_2D_${i}_{}.pdf                                                 ZEP_2D_${i}.pdf  ; mv ZEP_2D_${i}.pdf ../  ; done

# this is the above, but with the messy signal stuff put in where the {} are

for i in 2Mu2J_{Global,400_50_800,400_50_80,400_50_8,400_20_400,400_20_40,400_20_4,400_150_4000,400_150_400,400_150_40,200_50_2000,200_50_200,200_50_20,200_20_700,200_20_70,200_20_7,125_50_5000,125_50_500,125_50_50,125_20_1300,125_20_130,125_20_13,1000_50_400,1000_50_40,1000_50_4,1000_350_3500,1000_350_350,1000_350_35,1000_20_200,1000_20_20,1000_20_2,1000_150_1000,1000_150_100,1000_150_10}; do pdfunite ZEP_2D_{chi2,highPurity,isGlobal,nPxlHit,nTrkLay}_${i}.pdf ZEP_2D_${i}.pdf; mv ZEP_2D_${i}.pdf ../; done
for i in {chi2,highPurity,isGlobal,nPxlHit,nTrkLay}; do pdfunite ZEP_2D_${i}_2Mu2J_{Global,400_50_800,400_50_80,400_50_8,400_20_400,400_20_40,400_20_4,400_150_4000,400_150_400,400_150_40,200_50_2000,200_50_200,200_50_20,200_20_700,200_20_70,200_20_7,125_50_5000,125_50_500,125_50_50,125_20_1300,125_20_130,125_20_13,1000_50_400,1000_50_40,1000_50_4,1000_350_3500,1000_350_350,1000_350_35,1000_20_200,1000_20_20,1000_20_2,1000_150_1000,1000_150_100,1000_150_10}.pdf ZEP_2D_${i}.pdf; mv ZEP_2D_${i}.pdf ../; done


# 5 sets of cuts

{_Combined_NS_NH_FPTE_HLT_REP_PT_PC_LXYE_M,_Combined_NS_NH_FPTE_HLT_GLB_REP_PT_PC_LXYE_M,_Combined_NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M,_Combined_NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M_CHI2,_Combined_NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M_CHI2_D0SIG}

# mmhm
{NS_NH_FPTE_HLT_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M_CHI2,NS_NH_FPTE_HLT_GLB_NTL_REP_PT_PC_LXYE_M_CHI2_D0SIG}

# 10 MC samples

{DY10to50,DY50toInf,ttbar,tbarW,tW,WZ,ZZ,WW,WJets,QCD20toInf-ME}

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
