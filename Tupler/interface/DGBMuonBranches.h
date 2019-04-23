#ifndef DGBMUONBRANCHES_H
#define DGBMUONBRANCHES_H

// CMSSW includes
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/IPTools/interface/IPTools.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"
#include "DisplacedDimuons/Tupler/interface/DisplacedMuonFiller.h"

// muon branch collection
class DGBMuonBranches : public BranchCollection
{
 public:
  // constructor
 DGBMuonBranches(TreeContainer &tree, const bool DECLARE=true) :
  BranchCollection(tree, "reco::Track displacedGlobalMuon collection", "DGB Muon info will not be filled")
    {
      Reset();
      if (DECLARE) Declarations();
    }

  // members
  static bool alreadyPrinted_;

  std::vector<int  > dgbmu_idx          ;
  std::vector<float> dgbmu_px           ;
  std::vector<float> dgbmu_py           ;
  std::vector<float> dgbmu_pz           ;
  std::vector<float> dgbmu_ptError      ;
  std::vector<float> dgbmu_eta          ;
  std::vector<float> dgbmu_phi          ;
  std::vector<int  > dgbmu_charge       ;
  std::vector<float> dgbmu_chi2         ;
  std::vector<int>   dgbmu_ndof         ;

  std::vector<float> dgbmu_x            ;
  std::vector<float> dgbmu_y            ;
  std::vector<float> dgbmu_z            ;
  std::vector<float> dgbmu_x_fhit       ;
  std::vector<float> dgbmu_y_fhit       ;
  std::vector<float> dgbmu_z_fhit       ;

  std::vector<int  > dgbmu_nMuonHits    ;
  std::vector<int  > dgbmu_nDTHits      ;
  std::vector<int  > dgbmu_nCSCHits     ;
  std::vector<int  > dgbmu_nDTStations  ;
  std::vector<int  > dgbmu_nCSCStations ;

  std::vector<float> dgbmu_d0_pv        ;
  std::vector<float> dgbmu_d0_bs        ;
  std::vector<float> dgbmu_d0_pv_lin    ;
  std::vector<float> dgbmu_d0_bs_lin    ;
  std::vector<float> dgbmu_d0sig_pv     ;
  std::vector<float> dgbmu_d0sig_bs     ;
  std::vector<float> dgbmu_d0sig_pv_lin ;
  std::vector<float> dgbmu_d0sig_bs_lin ;

  std::vector<float> dgbmu_dz_pv        ;
  std::vector<float> dgbmu_dz_bs        ;
  std::vector<float> dgbmu_dz_pv_lin    ;
  std::vector<float> dgbmu_dz_bs_lin    ;
  std::vector<float> dgbmu_dzsig_pv     ;
  std::vector<float> dgbmu_dzsig_bs     ;
  std::vector<float> dgbmu_dzsig_pv_lin ;
  std::vector<float> dgbmu_dzsig_bs_lin ;

  // methods
  void Declarations()
  {
    Declare("dgbmu_idx"          , dgbmu_idx          );
    Declare("dgbmu_px"           , dgbmu_px           );
    Declare("dgbmu_py"           , dgbmu_py           );
    Declare("dgbmu_pz"           , dgbmu_pz           );
    Declare("dgbmu_ptError"      , dgbmu_ptError      );
    Declare("dgbmu_eta"          , dgbmu_eta          );
    Declare("dgbmu_phi"          , dgbmu_phi          );
    Declare("dgbmu_charge"       , dgbmu_charge       );
    Declare("dgbmu_chi2"         , dgbmu_chi2         );
    Declare("dgbmu_ndof"         , dgbmu_ndof         );

    Declare("dgbmu_x"            , dgbmu_x            );
    Declare("dgbmu_y"            , dgbmu_y            );
    Declare("dgbmu_z"            , dgbmu_z            );
    Declare("dgbmu_x_fhit"       , dgbmu_x_fhit       );
    Declare("dgbmu_y_fhit"       , dgbmu_y_fhit       );
    Declare("dgbmu_z_fhit"       , dgbmu_z_fhit       );

    Declare("dgbmu_nMuonHits"    , dgbmu_nMuonHits    );
    Declare("dgbmu_nDTHits"      , dgbmu_nDTHits      );
    Declare("dgbmu_nCSCHits"     , dgbmu_nCSCHits     );
    Declare("dgbmu_nDTStations"  , dgbmu_nDTStations  );
    Declare("dgbmu_nCSCStations" , dgbmu_nCSCStations );

    Declare("dgbmu_d0_pv"        , dgbmu_d0_pv        );
    Declare("dgbmu_d0_bs"        , dgbmu_d0_bs        );
    Declare("dgbmu_d0_pv_lin"    , dgbmu_d0_pv_lin    );
    Declare("dgbmu_d0_bs_lin"    , dgbmu_d0_bs_lin    );
    Declare("dgbmu_d0sig_pv"     , dgbmu_d0sig_pv     );
    Declare("dgbmu_d0sig_bs"     , dgbmu_d0sig_bs     );
    Declare("dgbmu_d0sig_pv_lin" , dgbmu_d0sig_pv_lin );
    Declare("dgbmu_d0sig_bs_lin" , dgbmu_d0sig_bs_lin );

    Declare("dgbmu_dz_pv"        , dgbmu_dz_pv        );
    Declare("dgbmu_dz_bs"        , dgbmu_dz_bs        );
    Declare("dgbmu_dz_pv_lin"    , dgbmu_dz_pv_lin    );
    Declare("dgbmu_dz_bs_lin"    , dgbmu_dz_bs_lin    );
    Declare("dgbmu_dzsig_pv"     , dgbmu_dzsig_pv     );
    Declare("dgbmu_dzsig_bs"     , dgbmu_dzsig_bs     );
    Declare("dgbmu_dzsig_pv_lin" , dgbmu_dzsig_pv_lin );
    Declare("dgbmu_dzsig_bs_lin" , dgbmu_dzsig_bs_lin );
  }

  void Reset()
  {
    dgbmu_idx          .clear();
    dgbmu_px           .clear();
    dgbmu_py           .clear();
    dgbmu_pz           .clear();
    dgbmu_ptError      .clear();
    dgbmu_eta          .clear();
    dgbmu_phi          .clear();
    dgbmu_charge       .clear();
    dgbmu_chi2         .clear();
    dgbmu_ndof         .clear();

    dgbmu_x            .clear();
    dgbmu_y            .clear();
    dgbmu_z            .clear();
    dgbmu_x_fhit       .clear();
    dgbmu_y_fhit       .clear();
    dgbmu_z_fhit       .clear();

    dgbmu_nMuonHits    .clear();
    dgbmu_nDTHits      .clear();
    dgbmu_nCSCHits     .clear();
    dgbmu_nDTStations  .clear();
    dgbmu_nCSCStations .clear();

    dgbmu_d0_pv        .clear();
    dgbmu_d0_bs        .clear();
    dgbmu_d0_pv_lin    .clear();
    dgbmu_d0_bs_lin    .clear();
    dgbmu_d0sig_pv     .clear();
    dgbmu_d0sig_bs     .clear();
    dgbmu_d0sig_pv_lin .clear();
    dgbmu_d0sig_bs_lin .clear();

    dgbmu_dz_pv        .clear();
    dgbmu_dz_bs        .clear();
    dgbmu_dz_pv_lin    .clear();
    dgbmu_dz_bs_lin    .clear();
    dgbmu_dzsig_pv     .clear();
    dgbmu_dzsig_bs     .clear();
    dgbmu_dzsig_pv_lin .clear();
    dgbmu_dzsig_bs_lin .clear();
  }

  void Fill(const edm::Handle<reco::TrackCollection> &muonsHandle,
	    const edm::ESHandle<TransientTrackBuilder>& ttB,
	    const edm::Handle<reco::VertexCollection> &verticesHandle,
	    const edm::Handle<reco::BeamSpot> &beamspotHandle);

  virtual bool alreadyPrinted() { return alreadyPrinted_; }
  virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
