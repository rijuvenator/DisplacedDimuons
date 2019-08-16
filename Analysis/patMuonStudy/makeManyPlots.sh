# the content of this is saved in workflows
# use the brace expanded cutstrings list

parallel python makeZephyrPlots.py --cutstring ::: NS_NH_FPTE_HLT_REP_PT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_LXYSIG_TRK_NDT_{DPHI,IDPHI}
parallel python makeZephyrPlots.py --zoomed --cutstring ::: NS_NH_FPTE_HLT_REP_PT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_LXYSIG_TRK_NDT_{DPHI,IDPHI}

for cs in NS_NH_FPTE_HLT_REP_PT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_LXYSIG_TRK_NDT_{DPHI,IDPHI}
do
    mkdir -p pdfs/${cs}/
    mv pdfs/ZEP*${cs}_{MC,2Mu2J}*.pdf pdfs/${cs}/
done

