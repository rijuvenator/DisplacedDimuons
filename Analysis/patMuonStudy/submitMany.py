import subprocess as bash

if False:
    for key, suffix in (
        ('_Combined_NS_NH_FPTE_HLT_REP_PT_PC_LXYE_MASS_CHI2_VTX_COSA_SFPTE', ''),
        ('_Combined_NS_NH_FPTE_HLT_REP_PT_PC_LXYE_MASS_CHI2_VTX_COSA_SFPTE_NDSA', '_N'),
        ('_Combined_NS_NH_FPTE_HLT_REP_PT_PC_LXYE_MASS_CHI2_VTX_COSA_SFPTE_NDSA_LXYSIG', '_NL'),
        ):
        #bash.call('python zephyrPlots.py --test --name DY50toInf --cuts {}; mv test.root cutTest{}.root'.format(key, suffix), shell=True)
        bash.call('python zephyrPlots.py --test --signalpoint 1000 150 100 --trigger --cuts {}; mv test.root cutTest{}.root'.format(key, suffix), shell=True)

if False:
    for cmd in (
        '--samples D --flavour longlunch --extra           __cuts {}',
        '--samples 2 --flavour longlunch --extra __trigger __cuts {}',
#       '--samples S --flavour longlunch --extra __trigger __cuts {}',
        '--samples B --flavour workday   --extra           __cuts {}',
    ):
        for key in (
            '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_LXYSIG_OS_DPHI',
            '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_LXYSIG_OS_IDPHI',
            ):
            realKey = key
            if '_DPHI' in key and 'samples D' in cmd: realKey = key + ' __skim'
            bash.call('runAll.py zephyrPlots.py '+cmd.format(realKey), shell=True)

if True:
    for cmd in (
        '--samples D --flavour microcentury --extra           __cuts {}',
#       '--samples 2 --flavour microcentury --extra __trigger __cuts {}',
#       '--samples S --flavour microcentury --extra __trigger __cuts {}',
#       '--samples B --flavour microcentury --extra           __cuts {}',
    ):
        for key in (
#           '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_LXYSIG_OS_DPHI',
#           '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_LXYSIG_OS_IDPHI',
            '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_LXYSIG_DPHI',
            '_Combined_NS_NH_FPTE_HLT_REP_PT_TRK_NDT_DCA_PC_LXYE_MASS_CHI2_VTX_COSA_NPP_LXYSIG_IDPHI',
            ):
            realKey = key
            if '_DPHI' in key and 'samples D' in cmd: realKey = key + ' __skim'
            bash.call('runAll.py DSADump.py '+cmd.format(realKey), shell=True)

