#ifndef DSAMUONBRANCHES_H
#define DSAMUONBRANCHES_H

// CMSSW includes
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "Geometry/CSCGeometry/interface/CSCGeometry.h"
#include "Geometry/DTGeometry/interface/DTGeometry.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/IPTools/interface/IPTools.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"
#include "DisplacedDimuons/Tupler/interface/DisplacedMuonFiller.h"

// muon branch collection
class DSAMuonBranches : public BranchCollection
{
 public:
  // constructor
 DSAMuonBranches(TreeContainer &tree, const bool DECLARE=true) :
  BranchCollection(tree, "reco::Track displacedStandAloneMuon collection", "DSA Muon info will not be filled")
    {
      Reset();
      if (DECLARE) Declarations();
    }

  // members
  static bool alreadyPrinted_;

  std::vector<int  > dsamu_idx             ;
  std::vector<float> dsamu_px              ;
  std::vector<float> dsamu_py              ;
  std::vector<float> dsamu_pz              ;
  std::vector<float> dsamu_ptError         ;
  std::vector<float> dsamu_eta             ;
  std::vector<float> dsamu_phi             ;
  std::vector<int  > dsamu_charge          ;
  std::vector<float> dsamu_chi2            ;
  std::vector<int>   dsamu_ndof            ;

  std::vector<float> dsamu_x               ;
  std::vector<float> dsamu_y               ;
  std::vector<float> dsamu_z               ;
  std::vector<float> dsamu_x_fhit          ;
  std::vector<float> dsamu_y_fhit          ;
  std::vector<float> dsamu_z_fhit          ;

  std::vector<int  > dsamu_nMuonHits       ;
  std::vector<int  > dsamu_nDTHits         ;
  std::vector<int  > dsamu_nCSCHits        ;
  std::vector<int  > dsamu_nDTStations     ;
  std::vector<int  > dsamu_nCSCStations    ;
  std::vector<int  > dsamu_nSegments       ;

  std::vector<float> dsamu_d0_pv           ;
  std::vector<float> dsamu_d0_bs           ;
  std::vector<float> dsamu_d0_pv_lin       ;
  std::vector<float> dsamu_d0_bs_lin       ;
  std::vector<float> dsamu_d0sig_pv        ;
  std::vector<float> dsamu_d0sig_bs        ;
  std::vector<float> dsamu_d0sig_pv_lin    ;
  std::vector<float> dsamu_d0sig_bs_lin    ;

  std::vector<float> dsamu_dz_pv           ;
  std::vector<float> dsamu_dz_bs           ;
  std::vector<float> dsamu_dz_pv_lin       ;
  std::vector<float> dsamu_dz_bs_lin       ;
  std::vector<float> dsamu_dzsig_pv        ;
  std::vector<float> dsamu_dzsig_bs        ;
  std::vector<float> dsamu_dzsig_pv_lin    ;
  std::vector<float> dsamu_dzsig_bs_lin    ;

  // Segment-based matches: PAT mu idx; number of segments matched;
  // dR(DSA position; PAT direction); dR(DSA position; PAT
  // extrapolated position)
  std::vector<std::vector<int>>   dsamu_idx_SegmMatch      ;
  std::vector<std::vector<int>>   dsamu_nSegms_SegmMatch   ;
  std::vector<std::vector<float>> dsamu_deltaR_pd_SegmMatch;
  std::vector<std::vector<float>> dsamu_deltaR_pp_SegmMatch;

  // Closest PAT muon(s) for two types of matches [(position;
  // direction) and (position; position)]: idx; number of segments
  // matched; dR
  std::vector<int>   dsamu_idx_pd_ProxMatch   ;
  std::vector<int>   dsamu_nSegms_pd_ProxMatch;
  std::vector<float> dsamu_deltaR_pd_ProxMatch;
  std::vector<int>   dsamu_idx_pp_ProxMatch   ;
  std::vector<int>   dsamu_nSegms_pp_ProxMatch;
  std::vector<float> dsamu_deltaR_pp_ProxMatch;

  // Timing info.  Use timing of the nearest standalone muon as proxy.
  std::vector<float> dsamu_dR_DSA_STA          ;
  std::vector<int>   dsamu_direction           ;
  std::vector<float> dsamu_timeAtIpInOut       ;
  std::vector<float> dsamu_timeAtIpInOutErr    ;
  std::vector<float> dsamu_timeAtIpOutIn       ;
  std::vector<float> dsamu_timeAtIpOutInErr    ;
  std::vector<int>   dsamu_direction_RPC       ;
  std::vector<float> dsamu_timeAtIpInOut_RPC   ;
  std::vector<float> dsamu_timeAtIpInOutErr_RPC;
  std::vector<float> dsamu_timeAtIpOutIn_RPC   ;
  std::vector<float> dsamu_timeAtIpOutInErr_RPC;

  // methods
  void Declarations()
  {
    Declare("dsamu_idx"             , dsamu_idx             );
    Declare("dsamu_px"              , dsamu_px              );
    Declare("dsamu_py"              , dsamu_py              );
    Declare("dsamu_pz"              , dsamu_pz              );
    Declare("dsamu_ptError"         , dsamu_ptError         );
    Declare("dsamu_eta"             , dsamu_eta             );
    Declare("dsamu_phi"             , dsamu_phi             );
    Declare("dsamu_charge"          , dsamu_charge          );
    Declare("dsamu_chi2"            , dsamu_chi2            );
    Declare("dsamu_ndof"            , dsamu_ndof            );

    Declare("dsamu_x"               , dsamu_x               );
    Declare("dsamu_y"               , dsamu_y               );
    Declare("dsamu_z"               , dsamu_z               );
    Declare("dsamu_x_fhit"          , dsamu_x_fhit          );
    Declare("dsamu_y_fhit"          , dsamu_y_fhit          );
    Declare("dsamu_z_fhit"          , dsamu_z_fhit          );

    Declare("dsamu_nMuonHits"       , dsamu_nMuonHits       );
    Declare("dsamu_nDTHits"         , dsamu_nDTHits         );
    Declare("dsamu_nCSCHits"        , dsamu_nCSCHits        );
    Declare("dsamu_nDTStations"     , dsamu_nDTStations     );
    Declare("dsamu_nCSCStations"    , dsamu_nCSCStations    );
    Declare("dsamu_nSegments"       , dsamu_nSegments       );

    Declare("dsamu_d0_pv"           , dsamu_d0_pv           );
    Declare("dsamu_d0_bs"           , dsamu_d0_bs           );
    Declare("dsamu_d0_pv_lin"       , dsamu_d0_pv_lin       );
    Declare("dsamu_d0_bs_lin"       , dsamu_d0_bs_lin       );
    Declare("dsamu_d0sig_pv"        , dsamu_d0sig_pv        );
    Declare("dsamu_d0sig_bs"        , dsamu_d0sig_bs        );
    Declare("dsamu_d0sig_pv_lin"    , dsamu_d0sig_pv_lin    );
    Declare("dsamu_d0sig_bs_lin"    , dsamu_d0sig_bs_lin    );

    Declare("dsamu_dz_pv"           , dsamu_dz_pv           );
    Declare("dsamu_dz_bs"           , dsamu_dz_bs           );
    Declare("dsamu_dz_pv_lin"       , dsamu_dz_pv_lin       );
    Declare("dsamu_dz_bs_lin"       , dsamu_dz_bs_lin       );
    Declare("dsamu_dzsig_pv"        , dsamu_dzsig_pv        );
    Declare("dsamu_dzsig_bs"        , dsamu_dzsig_bs        );
    Declare("dsamu_dzsig_pv_lin"    , dsamu_dzsig_pv_lin    );
    Declare("dsamu_dzsig_bs_lin"    , dsamu_dzsig_bs_lin    );

    Declare("dsamu_idx_SegmMatch"      , dsamu_idx_SegmMatch      );
    Declare("dsamu_nSegms_SegmMatch"   , dsamu_nSegms_SegmMatch   );
    Declare("dsamu_deltaR_pd_SegmMatch", dsamu_deltaR_pd_SegmMatch);
    Declare("dsamu_deltaR_pp_SegmMatch", dsamu_deltaR_pp_SegmMatch);

    Declare("dsamu_idx_pd_ProxMatch"   , dsamu_idx_pd_ProxMatch   );
    Declare("dsamu_nSegms_pd_ProxMatch", dsamu_nSegms_pd_ProxMatch);
    Declare("dsamu_deltaR_pd_ProxMatch", dsamu_deltaR_pd_ProxMatch);
    Declare("dsamu_idx_pp_ProxMatch"   , dsamu_idx_pp_ProxMatch   );
    Declare("dsamu_nSegms_pp_ProxMatch", dsamu_nSegms_pp_ProxMatch);
    Declare("dsamu_deltaR_pp_ProxMatch", dsamu_deltaR_pp_ProxMatch);

    Declare("dsamu_dR_DSA_STA"           , dsamu_dR_DSA_STA          );
    Declare("dsamu_direction"            , dsamu_direction           );
    Declare("dsamu_timeAtIpInOut"        , dsamu_timeAtIpInOut       );
    Declare("dsamu_timeAtIpInOutErr"     , dsamu_timeAtIpInOutErr    );
    Declare("dsamu_timeAtIpOutIn"        , dsamu_timeAtIpOutIn       );
    Declare("dsamu_timeAtIpOutInErr"     , dsamu_timeAtIpOutInErr    );
    Declare("dsamu_direction_RPC"        , dsamu_direction_RPC       );
    Declare("dsamu_timeAtIpInOut_RPC"    , dsamu_timeAtIpInOut_RPC   );
    Declare("dsamu_timeAtIpInOutErr_RPC" , dsamu_timeAtIpInOutErr_RPC);
    Declare("dsamu_timeAtIpOutIn_RPC"    , dsamu_timeAtIpOutIn_RPC   );
    Declare("dsamu_timeAtIpOutInErr_RPC" , dsamu_timeAtIpOutInErr_RPC);
  }

  void Reset()
  {
    dsamu_idx             .clear();
    dsamu_px              .clear();
    dsamu_py              .clear();
    dsamu_pz              .clear();
    dsamu_ptError         .clear();
    dsamu_eta             .clear();
    dsamu_phi             .clear();
    dsamu_charge          .clear();
    dsamu_chi2            .clear();
    dsamu_ndof            .clear();

    dsamu_x               .clear();
    dsamu_y               .clear();
    dsamu_z               .clear();
    dsamu_x_fhit          .clear();
    dsamu_y_fhit          .clear();
    dsamu_z_fhit          .clear();

    dsamu_nMuonHits       .clear();
    dsamu_nDTHits         .clear();
    dsamu_nCSCHits        .clear();
    dsamu_nDTStations     .clear();
    dsamu_nCSCStations    .clear();
    dsamu_nSegments       .clear();

    dsamu_d0_pv           .clear();
    dsamu_d0_bs           .clear();
    dsamu_d0_pv_lin       .clear();
    dsamu_d0_bs_lin       .clear();
    dsamu_d0sig_pv        .clear();
    dsamu_d0sig_bs        .clear();
    dsamu_d0sig_pv_lin    .clear();
    dsamu_d0sig_bs_lin    .clear();

    dsamu_dz_pv           .clear();
    dsamu_dz_bs           .clear();
    dsamu_dz_pv_lin       .clear();
    dsamu_dz_bs_lin       .clear();
    dsamu_dzsig_pv        .clear();
    dsamu_dzsig_bs        .clear();
    dsamu_dzsig_pv_lin    .clear();
    dsamu_dzsig_bs_lin    .clear();

    dsamu_idx_SegmMatch      .clear();
    dsamu_nSegms_SegmMatch   .clear();
    dsamu_deltaR_pd_SegmMatch.clear();
    dsamu_deltaR_pp_SegmMatch.clear();

    dsamu_idx_pd_ProxMatch   .clear();
    dsamu_deltaR_pd_ProxMatch.clear();
    dsamu_nSegms_pd_ProxMatch.clear();
    dsamu_idx_pp_ProxMatch   .clear();
    dsamu_deltaR_pp_ProxMatch.clear();
    dsamu_nSegms_pp_ProxMatch.clear();

    dsamu_dR_DSA_STA          .clear();
    dsamu_direction           .clear();
    dsamu_timeAtIpInOut       .clear();
    dsamu_timeAtIpInOutErr    .clear();
    dsamu_timeAtIpOutIn       .clear();
    dsamu_timeAtIpOutInErr    .clear();
    dsamu_direction_RPC       .clear();
    dsamu_timeAtIpInOut_RPC   .clear();
    dsamu_timeAtIpInOutErr_RPC.clear();
    dsamu_timeAtIpOutIn_RPC   .clear();
    dsamu_timeAtIpOutInErr_RPC.clear();
  }

  void Fill(const edm::Handle<reco::TrackCollection> &dsamuonsHandle,
	    const edm::ESHandle<TransientTrackBuilder>& ttB,
	    const edm::Handle<reco::VertexCollection> &verticesHandle,
	    const edm::Handle<reco::BeamSpot> &beamspotHandle,
	    const edm::ESHandle<Propagator>& propagator,
	    const edm::ESHandle<MagneticField>& magfield,
	    const edm::Handle<pat::MuonCollection> &patmuonsHandle,
	    const edm::ESHandle<CSCGeometry>& cscGeom,
	    const edm::ESHandle<DTGeometry>& dtGeom);

  void DRExtrapTrackToDSA(const reco::Track& track,
			  const reco::Track& dsamuon,
			  const edm::ESHandle<Propagator>& propagator,
			  const edm::ESHandle<MagneticField>& magfield,
			  double& dR_pd, double& dR_pp);

  virtual bool alreadyPrinted() { return alreadyPrinted_; }
  virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
