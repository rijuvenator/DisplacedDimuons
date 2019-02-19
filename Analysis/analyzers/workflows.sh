# submitting dimuon and recoMuon jobs
if ! grep -q mcbg dimuonPlots.py
then
    echo "No mcbg found in dimuonPlots.py"
fi

if ! grep -q mcbg recoMuonPlots.py
then
    echo "No mcbg found in recoMuonPlots.py"
fi

for s in dimuon recoMuon
do
    #for c in _NS_NH _NS_NH_FPTE
    for c in _NS_NH_FPTE_PT _NS_NH_FPTE_PT_HLT _NS_NH_FPTE_PT_HLT_PC _NS_NH_FPTE_PT_HLT_PC_LXYE _NS_NH_FPTE_PT_HLT_PC_LXYE_M
    do
        python runAll.py ${s}Plots.py --samples BD --flavour workday --extra __cuts   _Prompt${c}
        python runAll.py ${s}Plots.py --samples B  --flavour workday --extra __cuts _NoPrompt${c}
    done
done

# correlation plots workflows -- step by step
python runAll.py correlationPlots.py --samples B  --flavour workday --extra __cuts   _Prompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M
python runAll.py correlationPlots.py --samples B  --flavour workday --extra __cuts _NoPrompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M
python runAll.py correlationPlots.py --samples S2 --flavour workday --extra __cuts   _Prompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M __trigger
python runAll.py correlationPlots.py --samples S2 --flavour workday --extra __cuts _NoPrompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M __trigger

python rehaddAll.py --mode split --tags CorrelationPlots_{,No}Prompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M --dirs tmp mcbg --samples bigMC --noPlots

for i in Prompt NoPrompt; do mv CorrelationPlots_Trig_${i}_*HTo*.root Signal_Trig_${i}_BS8/; done
python rehaddAll.py --mode move --tags Correlation --cutstrings {,No}Prompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M

python rehaddAll.py --mode rehadd --tags Correlation --dirs MC_Prompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M --suffix Prompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M_MCOnly --batch &
python rehaddAll.py --mode rehadd --tags Correlation --dirs MC_NoPrompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M --suffix NoPrompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M_MCOnly --batch &
python rehaddAll.py --mode rehadd --tags Correlation --dirs Signal_Trig_Prompt_BS8 --suffix Trig_Prompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M_SignalOnly --batch &
python rehaddAll.py --mode rehadd --tags Correlation --dirs Signal_Trig_NoPrompt_BS8 --suffix Trig_NoPrompt_NS_NH_FPTE_PT_HLT_PC_LXYE_M_SignalOnly --batch &
