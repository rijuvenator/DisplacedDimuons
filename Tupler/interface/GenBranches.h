#ifndef GENBRANCHES_H
#define GENBRANCHES_H

// ROOT includes
#include "TVector3.h"

// CMSSW includes
#include "FWCore/Framework/interface/ESHandle.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/HepMCCandidate/interface/GenParticleFwd.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"
#include "TrackPropagation/SteppingHelixPropagator/interface/SteppingHelixPropagator.h"

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

  // True number of primary vertices for pileup reweighting
  float               gen_tnpv     ;

  std::vector<int   > gen_status   ;
  std::vector<int   > gen_pdgID    ;
  std::vector<float > gen_px       ;
  std::vector<float > gen_py       ;
  std::vector<float > gen_pz       ;
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

  std::vector<float > gen_px_bs    ;
  std::vector<float > gen_py_bs    ;
  std::vector<float > gen_pz_bs    ;
  std::vector<float > gen_pt_bs    ;
  std::vector<float > gen_eta_bs   ;
  std::vector<float > gen_phi_bs   ;
  std::vector<float > gen_energy_bs;
  std::vector<float > gen_x_bs     ;
  std::vector<float > gen_y_bs     ;
  std::vector<float > gen_z_bs     ;
  std::vector<float > gen_d0_bs    ;
  std::vector<float > gen_dz_bs    ;

  std::vector<float > gen_cosAlpha ;
  std::vector<float > gen_Lxy      ;
  std::vector<float > gen_d0       ;
  std::vector<float > gen_dz       ;
  std::vector<float > gen_deltaR   ;

  // methods
  void Declarations()
  {
    Declare("gen_weight"   , gen_weight, "F");

    Declare("gen_tnpv"     , gen_tnpv,   "F");

    Declare("gen_status"   , gen_status     );
    Declare("gen_pdgID"    , gen_pdgID      );
    Declare("gen_px"       , gen_px         );
    Declare("gen_py"       , gen_py         );
    Declare("gen_pz"       , gen_pz         );
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

    Declare("gen_px_bs"    , gen_px_bs      );
    Declare("gen_py_bs"    , gen_py_bs      );
    Declare("gen_pz_bs"    , gen_pz_bs      );
    Declare("gen_pt_bs"    , gen_pt_bs      );
    Declare("gen_eta_bs"   , gen_eta_bs     );
    Declare("gen_phi_bs"   , gen_phi_bs     );
    Declare("gen_energy_bs", gen_energy_bs  );
    Declare("gen_x_bs"     , gen_x_bs       );
    Declare("gen_y_bs"     , gen_y_bs       );
    Declare("gen_z_bs"     , gen_z_bs       );
    Declare("gen_d0_bs"    , gen_d0_bs      );
    Declare("gen_dz_bs"    , gen_dz_bs      );

    Declare("gen_cosAlpha" , gen_cosAlpha   );
    Declare("gen_Lxy"      , gen_Lxy        );
    Declare("gen_d0"       , gen_d0         );
    Declare("gen_dz"       , gen_dz         );
    Declare("gen_deltaR"   , gen_deltaR     );
  }

  void Reset()
  {
    gen_weight = 0;

    gen_tnpv   = -999.;

    gen_status   .clear();
    gen_pdgID    .clear();
    gen_px       .clear();
    gen_py       .clear();
    gen_pz       .clear();
    gen_pt       .clear();
    gen_eta      .clear();
    gen_phi      .clear();
    gen_mass     .clear();
    gen_energy   .clear();
    gen_charge   .clear();
    gen_x        .clear();
    gen_y        .clear();
    gen_z        .clear();
    gen_mother   .clear();

    gen_px_bs    .clear();
    gen_py_bs    .clear();
    gen_pz_bs    .clear();
    gen_pt_bs    .clear();
    gen_eta_bs   .clear();
    gen_phi_bs   .clear();
    gen_energy_bs.clear();
    gen_x_bs     .clear();
    gen_y_bs     .clear();
    gen_z_bs     .clear();
    gen_d0_bs    .clear();
    gen_dz_bs    .clear();

    gen_cosAlpha .clear();
    gen_Lxy      .clear();
    gen_d0       .clear();
    gen_dz       .clear();
    gen_deltaR   .clear();
  }

  void Fill(const edm::Handle<reco::GenParticleCollection> &gensHandle,
	    const edm::Handle<GenEventInfoProduct> &GEIPHandle,
	    const edm::Handle<std::vector<PileupSummaryInfo> > &pileupInfo,
	    const bool isSignal, const std::string finalState,
	    const edm::Handle<reco::BeamSpot> &beamspotHandle,
	    const edm::ESHandle<Propagator>& propagator,
	    const edm::ESHandle<MagneticField>& magfield);

  void Fill4Mu(const reco::GenParticleCollection &gens);
  void Fill2Mu2J(const reco::GenParticleCollection &gens);
  void FillOther(const reco::GenParticleCollection &gens);

  FreeTrajectoryState PropagateToBeamSpot(unsigned int idx,
			   const reco::BeamSpot& beamspot,
			   const edm::ESHandle<Propagator>& propagator,
			   const edm::ESHandle<MagneticField>& magfield);

  bool FailedToGet(const edm::Handle<reco::GenParticleCollection> &gensHandle,
		   const edm::Handle<GenEventInfoProduct> &GEIPHandle);

  virtual bool alreadyPrinted() { return alreadyPrinted_ && alreadyPrinted_GEIP; }
  virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
