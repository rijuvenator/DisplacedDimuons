# Signal Samples

Last updated: 29th January 2019

This folder contains the pythia fragments used to generate the different signal samples used in the analysis. As of today, two different models are used in the analysis: The Hidden Abelian Higgs Model [HAHM](https://arxiv.org/abs/1412.0018) and the Benchmark Pythia model model.

## Benchmark Samples used in 2018 Trigger studies

The folder `2018TriggerStudies/Fragments/` contains the Pythia8 fragments used to develop the signal, monitor and backup triggers.

The GEN-SIM samples were tested in CMSSW_9_2_8 and the final AOD with reHLT in CMSSW_9_2_10.

[9_0_21_HTo2LongLivedTo4Mu_reHLT_AOD Samples_Trigger_V37](https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fphys03&input=dataset%3D%2FHTo2LongLivedTo4mu*_MH-*_MFF-*_CTau-*mm_TuneCUETP8M1_13TeV_pythia8%2Fescalant-crab_HTo2LongLivedTo*_MH-*_MFF-*_CTau-*mm_TuneCUETP8M1_13TeV_pythia8_*AODSIM*V37*%2F*USER)

## Benchmark Samples used in 2016 Analysis search

The folder `2016Search/Fragments/` contains the Pythia8 fragments used for the search with 2016 data. 

The GEN-SIM samples were tested in CMSSW_7_1_32 and the final AOD are produced with CMSSW_8_0_21.

[8_0_21_HTo2LongLivedTo4mu_AOD Samples](https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fphys03&input=dataset%3D%2FHTo2LongLivedTo4mu*_MH-*_MFF-*_CTau-*mm_TuneCUETP8M1_13TeV_pythia8%2Fescalant-crab_HTo2LongLivedTo*_MH-*_MFF-*_CTau-*mm_TuneCUETP8M1_13TeV_pythia8_May2018-AOD-v1-*%2F*USER)

[8_0_21_HTo2LongLivedTo2mu2jets_AOD Samples](https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fphys03&input=dataset%3D%2FHTo2LongLivedTo2mu2jets*_MH-*_MFF-*_CTau-*mm_TuneCUETP8M1_13TeV_pythia8%2Fescalant-crab_HTo2LongLivedTo*_MH-*_MFF-*_CTau-*mm_TuneCUETP8M1_13TeV_pythia8_May2018-AOD-v1-*%2F*USER)

## HAHM Samples used in 2016 Analysis search

The folders `2016Search/*HAHM*/` contain all the relevant fragments used as to generate the samples for the search. In particular, this production uses aMC@NLO for the generation (gridpack is required) and PYTHIA 8 for the decay.

The GEN-SIM samples were tested in CMSSW_7_1_32 and the final AOD are produced with CMSSW_8_0_21.

[8_0_21_HTo2ZdTo2mu2x_AODSamples](https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fphys03&input=dataset%3D%2FHTo2ZdTo2mu2x_MZd-*_Epsilon-*_TuneCUETP8M1_13TeV_pythia8%2Fescalant-MC2016_HAHM_2Mu2x_Dec2018-AOD-v1-*%2FUSE)

##### Grid
The following dark photon - kinetic mixing was generated:

| M_Zd [GeV] | Epsilon        |
|------------|----------------|
| 10  | 1e-06, 5e-07, 1e-07, 3e-08 |
| 20 | 5e-07, 2e-07, 5e-08, 1e-08 |
| 30 | 3e-07, 1e-07, 3e-08, 7e-09 | 
| 40 | 2e-07, 6e-08, 1e-08, 4e-09 | 
| 50 | 2e-07, 6e-08, 1e-08, 4e-09 | 
| 60 | 1e-07, 4e-08, 7e-09, 2e-09 | 

##### Madgraph cards
The folder `2016Search/scriptsForHAHM_Cards/` contains the scripts needed to generate the aMC@NLO cards from template cards. The template cards are stored in `2016Search/scriptsForHAHM_Cards/HiggsPortalLongLivedDarkPhoton_TemplateCards`.

> *Example:* `python createGridpacks_darkPhoton.py -i HiggsPortalLongLivedDarkPhoton_TemplateCards -n LL_HAHM_MS_400_kappa_0p01` 

Will create the cards for the grid specified in the `createGridpacks_darkPhoton.py` script in the folder: `HiggsPortalLongLivedDarkPhoton_TemplateCards`

##### Gridpacks

The cards can be later used to create gridpacks. Examples of gridpacks can be found here: /afs/cern.ch/work/e/escalant/public/gridpacks/

##### Model files
The model files can be downloaded from [Original_Source](http://insti.physics.sunysb.edu/~curtin/hahm_mg.html) or [Gen_repository](https://cms-project-generators.web.cern.ch/cms-project-generators/).

##### Pythia fragments
* The folder `2016Search/FragmentsHAHM/` contains all the PYTHIA 8 fragments. **In order to produced GEN-SIM events it is needed to produce and provide a gridpack first**.


