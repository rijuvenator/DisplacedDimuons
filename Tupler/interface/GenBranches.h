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
  std::vector<float > gen_d0       ;
  std::vector<float > gen_dz       ;
  std::vector<int   > gen_mother   ;

  std::vector<float > gen_bs_px    ;
  std::vector<float > gen_bs_py    ;
  std::vector<float > gen_bs_pz    ;
  std::vector<float > gen_bs_pt    ;
  std::vector<float > gen_bs_eta   ;
  std::vector<float > gen_bs_phi   ;
  std::vector<float > gen_bs_energy;
  std::vector<float > gen_bs_x     ;
  std::vector<float > gen_bs_y     ;
  std::vector<float > gen_bs_z     ;
  std::vector<float > gen_bs_d0    ;
  std::vector<float > gen_bs_dz    ;

  std::vector<float > gen_cosAlpha ;
  std::vector<float > gen_Lxy      ;
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
    Declare("gen_d0"       , gen_d0         );
    Declare("gen_dz"       , gen_dz         );
    Declare("gen_mother"   , gen_mother     );

    Declare("gen_bs_px"    , gen_bs_px      );
    Declare("gen_bs_py"    , gen_bs_py      );
    Declare("gen_bs_pz"    , gen_bs_pz      );
    Declare("gen_bs_pt"    , gen_bs_pt      );
    Declare("gen_bs_eta"   , gen_bs_eta     );
    Declare("gen_bs_phi"   , gen_bs_phi     );
    Declare("gen_bs_energy", gen_bs_energy  );
    Declare("gen_bs_x"     , gen_bs_x       );
    Declare("gen_bs_y"     , gen_bs_y       );
    Declare("gen_bs_z"     , gen_bs_z       );
    Declare("gen_bs_d0"    , gen_bs_d0      );
    Declare("gen_bs_dz"    , gen_bs_dz      );

    Declare("gen_cosAlpha" , gen_cosAlpha   );
    Declare("gen_Lxy"      , gen_Lxy        );
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
    gen_d0       .clear();
    gen_dz       .clear();
    gen_mother   .clear();

    gen_bs_px    .clear();
    gen_bs_py    .clear();
    gen_bs_pz    .clear();
    gen_bs_pt    .clear();
    gen_bs_eta   .clear();
    gen_bs_phi   .clear();
    gen_bs_energy.clear();
    gen_bs_x     .clear();
    gen_bs_y     .clear();
    gen_bs_z     .clear();
    gen_bs_d0    .clear();
    gen_bs_dz    .clear();

    gen_cosAlpha .clear();
    gen_Lxy      .clear();
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
