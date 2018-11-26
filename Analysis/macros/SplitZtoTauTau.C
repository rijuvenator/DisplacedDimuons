#include <vector>
#include <iostream>
#include "TFile.h"
#include "TTree.h"
#include "TString.h"

// compile once with root -l -q -b "SplitZtoTauTau.C+()"
// make a wrapper script with root -l -q -b "SplitZtoTauTau.C+("$1")"
// DY50toInf has 6757713 events; this script runs in packets of 100000
// so do parallel ./wrapper.sh ::: $(seq 0 67)

void SplitZtoTauTau(Long64_t job=0)
{
  TFile *f = TFile::Open("~/eos/DisplacedDimuons/NTuples/ntuple_DY50toInf.root");
  TTree *t = (TTree*) f->Get("SimpleNTupler/DDTree");

  Long64_t nEntries = t->GetEntries();
  Long64_t range0 = job*100000;
  Long64_t range1 = std::min((job+1)*100000, nEntries);

  std::vector<int> *gen_pdgID  = 0;
  std::vector<int> *gen_mother = 0;
  t->SetBranchAddress("gen_pdgID" , &gen_pdgID );
  t->SetBranchAddress("gen_mother", &gen_mother);

  TString fname_emu("~/eos/DisplacedDimuons/skim_emu_");
  fname_emu += std::to_string(job);
  fname_emu += ".root";

  TString fname_tau("~/eos/DisplacedDimuons/skim_tau_");
  fname_tau += std::to_string(job);
  fname_tau += ".root";

  TFile *f_emu = new TFile(fname_emu, "RECREATE");
  f_emu->mkdir("SimpleNTupler");
  f_emu->cd("SimpleNTupler");
  TTree *t_emu = t->CloneTree(0);

  TFile *f_tau = new TFile(fname_tau, "RECREATE");
  f_tau->mkdir("SimpleNTupler");
  f_tau->cd("SimpleNTupler");
  TTree *t_tau = t->CloneTree(0);

  size_t count = 0;
  for (Long64_t i=range0; i<range1; i++)
  {
    t->GetEntry(i);
    if (i%100000==0)
    {
      std::cout << "Doing " << i << std::endl;
    }
    int nGen = gen_pdgID->size();
    bool tauFound = false;
    for (int i=0; i<nGen; ++i)
    {
      if (abs(gen_pdgID->at(i)) == 15)
      {
        int motherIdx = i;
        while (motherIdx != -1)
        {
          if (gen_pdgID->at(motherIdx) == 23)
          {
            tauFound = true;
            break;
          }
          motherIdx = gen_mother->at(motherIdx);
        }
      }
      if (tauFound) break;
    }

    if (tauFound)
    {
      t_tau->Fill();
    }
    else
    {
      t_emu->Fill();
    }
  }

  t_emu->AutoSave();
  t_tau->AutoSave();
  delete f;
  delete f_emu;
  delete f_tau;
}
