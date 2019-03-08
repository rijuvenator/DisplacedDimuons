#ifndef PATMUONBRANCHES_H
#define PATMUONBRANCHES_H

// CMSSW includes
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/IPTools/interface/IPTools.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"
#include "DisplacedDimuons/Tupler/interface/DisplacedMuonFiller.h"

// muon branch collection
class PATMuonBranches : public BranchCollection
{
 public:
  // constructor
 PATMuonBranches(TreeContainer &tree, const bool DECLARE=true) :
  BranchCollection(tree, "pat::Muon", "PAT Muon info will not be filled")
    {
      Reset();
      if (DECLARE) Declarations();
    }

  // members
  static bool alreadyPrinted_;

  std::vector<int  > patmu_idx             ;
  std::vector<float> patmu_px              ;
  std::vector<float> patmu_py              ;
  std::vector<float> patmu_pz              ;
  std::vector<float> patmu_ptError         ;
  std::vector<float> patmu_eta             ;
  std::vector<float> patmu_phi             ;
  std::vector<int  > patmu_charge          ;
  std::vector<float> patmu_chi2            ;
  std::vector<int>   patmu_ndof            ;

  std::vector<float> patmu_x               ;
  std::vector<float> patmu_y               ;
  std::vector<float> patmu_z               ;

  std::vector<int  > patmu_nMuonHits       ;
  std::vector<int  > patmu_nDTHits         ;
  std::vector<int  > patmu_nCSCHits        ;
  std::vector<int  > patmu_nDTStations     ;
  std::vector<int  > patmu_nCSCStations    ;

  std::vector<int  > patmu_nMatchedStations;
  std::vector<int  > patmu_isGlobal        ;
  std::vector<int  > patmu_isTracker       ;
  std::vector<int  > patmu_isMedium        ;
  std::vector<int  > patmu_nPixelHits      ;
  std::vector<int  > patmu_nTrackerHits    ;
  std::vector<int  > patmu_nTrackerLayers  ;
  std::vector<float> patmu_trackIso        ;
  std::vector<float> patmu_ecalIso         ;
  std::vector<float> patmu_hcalIso         ;
  std::vector<int  > patmu_hpur            ;

  std::vector<float> patmu_d0_pv           ;
  std::vector<float> patmu_d0_bs           ;
  std::vector<float> patmu_d0_pv_lin       ;
  std::vector<float> patmu_d0_bs_lin       ;
  std::vector<float> patmu_d0sig_pv        ;
  std::vector<float> patmu_d0sig_bs        ;
  std::vector<float> patmu_d0sig_pv_lin    ;
  std::vector<float> patmu_d0sig_bs_lin    ;

  std::vector<float> patmu_dz_pv           ;
  std::vector<float> patmu_dz_bs           ;
  std::vector<float> patmu_dz_pv_lin       ;
  std::vector<float> patmu_dz_bs_lin       ;
  std::vector<float> patmu_dzsig_pv        ;
  std::vector<float> patmu_dzsig_bs        ;
  std::vector<float> patmu_dzsig_pv_lin    ;
  std::vector<float> patmu_dzsig_bs_lin    ;

  std::vector<int  > patmu_gen_pdgID       ;
  std::vector<float> patmu_gen_pt          ;
  std::vector<float> patmu_gen_eta         ;
  std::vector<float> patmu_gen_phi         ;
  std::vector<float> patmu_gen_mass        ;
  std::vector<float> patmu_gen_energy      ;
  std::vector<int  > patmu_gen_charge      ;
  std::vector<float> patmu_gen_x           ;
  std::vector<float> patmu_gen_y           ;
  std::vector<float> patmu_gen_z           ;

  // methods
  void Declarations()
  {
    Declare("patmu_idx"             , patmu_idx             );
    Declare("patmu_px"              , patmu_px              );
    Declare("patmu_py"              , patmu_py              );
    Declare("patmu_pz"              , patmu_pz              );
    Declare("patmu_ptError"         , patmu_ptError         );
    Declare("patmu_eta"             , patmu_eta             );
    Declare("patmu_phi"             , patmu_phi             );
    Declare("patmu_charge"          , patmu_charge          );
    Declare("patmu_chi2"            , patmu_chi2            );
    Declare("patmu_ndof"            , patmu_ndof            );

    Declare("patmu_x"               , patmu_x               );
    Declare("patmu_y"               , patmu_y               );
    Declare("patmu_z"               , patmu_z               );

    Declare("patmu_nMuonHits"       , patmu_nMuonHits       );
    Declare("patmu_nDTHits"         , patmu_nDTHits         );
    Declare("patmu_nCSCHits"        , patmu_nCSCHits        );
    Declare("patmu_nDTStations"     , patmu_nDTStations     );
    Declare("patmu_nCSCStations"    , patmu_nCSCStations    );

    Declare("patmu_nMatchedStations", patmu_nMatchedStations);
    Declare("patmu_isGlobal"        , patmu_isGlobal        );
    Declare("patmu_isTracker"       , patmu_isTracker       );
    Declare("patmu_isMedium"        , patmu_isMedium        );
    Declare("patmu_nPixelHits"      , patmu_nPixelHits      );
    Declare("patmu_nTrackerHits"    , patmu_nTrackerHits    );
    Declare("patmu_nTrackerLayers"  , patmu_nTrackerLayers  );
    Declare("patmu_trackIso"        , patmu_trackIso        );
    Declare("patmu_ecalIso"         , patmu_ecalIso         );
    Declare("patmu_hcalIso"         , patmu_hcalIso         );
    Declare("patmu_hpur"            , patmu_hpur            );

    Declare("patmu_d0_pv"           , patmu_d0_pv           );
    Declare("patmu_d0_bs"           , patmu_d0_bs           );
    Declare("patmu_d0_pv_lin"       , patmu_d0_pv_lin       );
    Declare("patmu_d0_bs_lin"       , patmu_d0_bs_lin       );
    Declare("patmu_d0sig_pv"        , patmu_d0sig_pv        );
    Declare("patmu_d0sig_bs"        , patmu_d0sig_bs        );
    Declare("patmu_d0sig_pv_lin"    , patmu_d0sig_pv_lin    );
    Declare("patmu_d0sig_bs_lin"    , patmu_d0sig_bs_lin    );

    Declare("patmu_dz_pv"           , patmu_dz_pv           );
    Declare("patmu_dz_bs"           , patmu_dz_bs           );
    Declare("patmu_dz_pv_lin"       , patmu_dz_pv_lin       );
    Declare("patmu_dz_bs_lin"       , patmu_dz_bs_lin       );
    Declare("patmu_dzsig_pv"        , patmu_dzsig_pv        );
    Declare("patmu_dzsig_bs"        , patmu_dzsig_bs        );
    Declare("patmu_dzsig_pv_lin"    , patmu_dzsig_pv_lin    );
    Declare("patmu_dzsig_bs_lin"    , patmu_dzsig_bs_lin    );
       
    Declare("patmu_gen_pdgID"       , patmu_gen_pdgID       );
    Declare("patmu_gen_pt"          , patmu_gen_pt          );
    Declare("patmu_gen_eta"         , patmu_gen_eta         );
    Declare("patmu_gen_phi"         , patmu_gen_phi         );
    Declare("patmu_gen_mass"        , patmu_gen_mass        );
    Declare("patmu_gen_energy"      , patmu_gen_energy      );
    Declare("patmu_gen_charge"      , patmu_gen_charge      );
    Declare("patmu_gen_x"           , patmu_gen_x           );
    Declare("patmu_gen_y"           , patmu_gen_y           );
    Declare("patmu_gen_z"           , patmu_gen_z           );
  }

  void Reset()
  {
    patmu_idx             .clear();
    patmu_px              .clear();
    patmu_py              .clear();
    patmu_pz              .clear();
    patmu_ptError         .clear();
    patmu_eta             .clear();
    patmu_phi             .clear();
    patmu_charge          .clear();
    patmu_chi2            .clear();
    patmu_ndof            .clear();


    patmu_x               .clear();
    patmu_y               .clear();
    patmu_z               .clear();

    patmu_nMuonHits       .clear();
    patmu_nDTHits         .clear();
    patmu_nCSCHits        .clear();
    patmu_nDTStations     .clear();
    patmu_nCSCStations    .clear();

    patmu_nMatchedStations.clear();
    patmu_isGlobal        .clear();
    patmu_isTracker       .clear();
    patmu_isMedium        .clear();
    patmu_nPixelHits      .clear();
    patmu_nTrackerHits    .clear();
    patmu_nTrackerLayers  .clear();
    patmu_trackIso        .clear();
    patmu_ecalIso         .clear();
    patmu_hcalIso         .clear();
    patmu_hpur            .clear();

    patmu_d0_pv           .clear();
    patmu_d0_bs           .clear();
    patmu_d0_pv_lin       .clear();
    patmu_d0_bs_lin       .clear();
    patmu_d0sig_pv        .clear();
    patmu_d0sig_bs        .clear();
    patmu_d0sig_pv_lin    .clear();
    patmu_d0sig_bs_lin    .clear();

    patmu_dz_pv           .clear();
    patmu_dz_bs           .clear();
    patmu_dz_pv_lin       .clear();
    patmu_dz_bs_lin       .clear();
    patmu_dzsig_pv        .clear();
    patmu_dzsig_bs        .clear();
    patmu_dzsig_pv_lin    .clear();
    patmu_dzsig_bs_lin    .clear();
 
    patmu_gen_pdgID       .clear();
    patmu_gen_pt          .clear();
    patmu_gen_eta         .clear();
    patmu_gen_phi         .clear();
    patmu_gen_mass        .clear();
    patmu_gen_energy      .clear();
    patmu_gen_charge      .clear();
    patmu_gen_x           .clear();
    patmu_gen_y           .clear();
    patmu_gen_z           .clear();
  }

  void Fill(const edm::Handle<pat::MuonCollection> &muonsHandle,
	    const edm::ESHandle<TransientTrackBuilder>& ttB,
	    const edm::Handle<reco::VertexCollection> &verticesHandle,
	    const edm::Handle<reco::BeamSpot> &beamspotHandle,
	    const edm::ESHandle<Propagator>& propagator,
	    const edm::ESHandle<MagneticField>& magfield);

  bool isMediumMuon(const pat::Muon & mu);

  virtual bool alreadyPrinted() { return alreadyPrinted_; }
  virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
