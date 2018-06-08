#ifndef GENBRANCHES_H
#define GENBRANCHES_H

// ROOT includes
#include "TVector3.h"

// CMSSW includes
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/HepMCCandidate/interface/GenParticleFwd.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// gen particle branch collection
class GenBranches : public BranchCollection
{
 public:
  // constructor
 GenBranches(TreeContainer &tree, const bool DECLARE=true) :
  BranchCollection(tree, "reco::GenParticle collection", "gen info will not be filled")
    {
      Reset();
      if (DECLARE) Declarations();
    }

  // members
  static bool alreadyPrinted_;
  static bool alreadyPrinted_GEIP;

  float               gen_weight   ;

  std::vector<int   > gen_status   ;
  std::vector<int   > gen_pdgID    ;
  std::vector<float > gen_pt       ;
  std::vector<float > gen_eta      ;
  std::vector<float > gen_phi      ;
  std::vector<float > gen_mass     ;
  std::vector<float > gen_energy   ;
  std::vector<float > gen_charge   ;
  std::vector<float > gen_x        ;
  std::vector<float > gen_y        ;
  std::vector<float > gen_z        ;
  std::vector<int   > gen_mother   ;

  std::vector<float > gen_cosAlpha ;
  std::vector<float > gen_Lxy      ;
  std::vector<float > gen_d0       ;
  std::vector<float > gen_dz       ;
  std::vector<float > gen_deltaR   ;

  // methods
  void Declarations()
  {
    Declare("gen_weight"   , gen_weight, "F");

    Declare("gen_status"   , gen_status     );
    Declare("gen_pdgID"    , gen_pdgID      );
    Declare("gen_pt"       , gen_pt         );
    Declare("gen_eta"      , gen_eta        );
    Declare("gen_phi"      , gen_phi        );
    Declare("gen_mass"     , gen_mass       );
    Declare("gen_energy"   , gen_energy     );
    Declare("gen_charge"   , gen_charge     );
    Declare("gen_x"        , gen_x          );
    Declare("gen_y"        , gen_y          );
    Declare("gen_z"        , gen_z          );
    Declare("gen_mother"   , gen_mother     );

    Declare("gen_cosAlpha" , gen_cosAlpha   );
    Declare("gen_Lxy"      , gen_Lxy        );
    Declare("gen_d0"       , gen_d0         );
    Declare("gen_dz"       , gen_dz         );
    Declare("gen_deltaR"   , gen_deltaR     );
  }

  void Reset()
  {
    gen_weight = 0;

    gen_status  .clear();
    gen_pdgID   .clear();
    gen_pt      .clear();
    gen_eta     .clear();
    gen_phi     .clear();
    gen_mass    .clear();
    gen_energy  .clear();
    gen_charge  .clear();
    gen_x       .clear();
    gen_y       .clear();
    gen_z       .clear();
    gen_mother  .clear();

    gen_cosAlpha.clear();
    gen_Lxy     .clear();
    gen_d0      .clear();
    gen_dz      .clear();
    gen_deltaR  .clear();
  }

  void Fill(const edm::Handle<reco::GenParticleCollection> &gensHandle,
	    const edm::Handle<GenEventInfoProduct> &GEIPHandle,
	    const bool isSignal,
	    const std::string finalState);

  void Fill4Mu(const reco::GenParticleCollection &gens);
  void Fill2Mu2J(const reco::GenParticleCollection &gens);
  void FillOther(const reco::GenParticleCollection &gens);

  bool FailedToGet(const edm::Handle<reco::GenParticleCollection> &gensHandle,
		   const edm::Handle<GenEventInfoProduct> &GEIPHandle);

  virtual bool alreadyPrinted() { return alreadyPrinted_ && alreadyPrinted_GEIP; }
  virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
