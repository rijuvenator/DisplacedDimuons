#include <vector>
#include <iostream>
#include "TFile.h"
#include "TTree.h"
#include "TString.h"

// compile once with root -l -q -b "SplitData.C+()"
// make a wrapper script with root -l -q -b "SplitData.C+("$1")"
// This script runs in packets of 50000 to match the breakdown in runAll.py
// That means 291 jobs
// so do parallel ./wrapper.sh ::: $(seq 0 290)

void SplitData(Long64_t globaljob=0)
{
  TString era;
  Long64_t job;
  if (globaljob < 43)
  {
    era = "B";
    job = globaljob;
  }
  else if (globaljob < 43+20)
  {
    era = "C";
    job = globaljob - (43);
  }
  else if (globaljob < 43+20+34)
  {
    era = "D";
    job = globaljob - (43+20);
  }
  else if (globaljob < 43+20+34+32)
  {
    era = "E";
    job = globaljob - (43+20+34);
  }
  else if (globaljob < 43+20+34+32+26)
  {
    era = "F";
    job = globaljob - (43+20+34+32);
  }
  else if (globaljob < 43+20+34+32+26+63)
  {
    era = "G";
    job = globaljob - (43+20+34+32+26);
  }
  else
  {
    era = "H";
    job = globaljob - (43+20+34+32+26+63);
  }

  TFile *f;
  if (era == "B")
  {
    f = TFile::Open("/eos/cms/store/user/valuev/DisplacedDimuons/Tupler/Jun23/ntuple_DoubleMuonRun2016B-07Aug17-v2.root");
  }
  else
  {
    f = TFile::Open("/eos/cms/store/user/valuev/DisplacedDimuons/Tupler/Jun23/ntuple_DoubleMuonRun2016"+era+"-07Aug17.root");
  }
  TTree *t = (TTree*) f->Get("SimpleNTupler/DDTree");

  Long64_t nEntries = t->GetEntries();
  Long64_t range0 = job*50000;
  Long64_t range1 = std::min((job+1)*50000, nEntries);

  unsigned long long evt_event;
  t->SetBranchAddress("evt_event", &evt_event);

  TString fname("~/eos/DisplacedDimuons/skim_data_");
  //TString fname("skim_data_");
  fname += era;
  fname += "_";
  fname += std::to_string(job);
  fname += ".root";

  TFile *f_new = new TFile(fname, "RECREATE");
  f_new->mkdir("SimpleNTupler");
  f_new->cd("SimpleNTupler");
  TTree *t_new = t->CloneTree(0);

  size_t count = 0;
  for (Long64_t i=range0; i<range1; i++)
  {
    t->GetEntry(i);

    if (i%50000==0)
    {
      std::cout << "Doing " << i << std::endl;
    }

    if (evt_event % 10 == 7)
    {
      t_new->Fill();
    }

  }
  
  t_new->AutoSave();

  delete f;
  delete f_new;
}
