#ifndef DIMUONBRANCHES_H
#define DIMUONBRANCHES_H

// CMSSW includes
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/PatCandidates/interface/Muon.h"

#include "FWCore/Framework/interface/Event.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "RecoVertex/VertexPrimitives/interface/TransientVertex.h"
#include "RecoVertex/KalmanVertexFit/interface/KalmanVertexFitter.h"
#include "RecoVertex/AdaptiveVertexFit/interface/AdaptiveVertexFitter.h"
#include "RecoVertex/VertexTools/interface/VertexDistanceXY.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// ROOT includes
#include "TVector3.h"
#include "TLorentzVector.h"

// muon branch collection
class DimuonBranches : public BranchCollection
{
  public:
    // constructor
    DimuonBranches(TreeContainer &tree, const bool DECLARE=true) :
      BranchCollection(tree)
    {
      Reset();
      if (DECLARE) Declarations();
    }

    // members
    static bool alreadyPrinted_;

    std::vector<float> dim_pt                     ;
    std::vector<float> dim_eta                    ;
    std::vector<float> dim_phi                    ;
    std::vector<float> dim_mass                   ;
    std::vector<float> dim_p                      ;
    std::vector<float> dim_x                      ;
    std::vector<float> dim_y                      ;
    std::vector<float> dim_z                      ;
    std::vector<float> dim_Lxy_pv                 ;
    std::vector<float> dim_LxySig_pv              ;
    std::vector<float> dim_Lxy_bs                 ;
    std::vector<float> dim_LxySig_bs              ;
    std::vector<float> dim_deltaR                 ;
    std::vector<float> dim_normChi2               ;
    std::vector<float> dim_cosAlpha               ;
    std::vector<float> dim_deltaPhi               ;

    std::vector<int  > dim_mu1_idx                ;
    std::vector<float> dim_mu1_px                 ;
    std::vector<float> dim_mu1_py                 ;
    std::vector<float> dim_mu1_pz                 ;
    std::vector<float> dim_mu1_ptError            ;
    std::vector<float> dim_mu1_eta                ;
    std::vector<float> dim_mu1_phi                ;
    std::vector<int  > dim_mu1_charge             ;
    std::vector<float> dim_mu1_d0_pv              ;
    std::vector<float> dim_mu1_d0_bs              ;
    std::vector<float> dim_mu1_d0_pv_lin          ;
    std::vector<float> dim_mu1_d0_bs_lin          ;
    std::vector<float> dim_mu1_d0sig_pv           ;
    std::vector<float> dim_mu1_d0sig_bs           ;
    std::vector<float> dim_mu1_d0sig_pv_lin       ;
    std::vector<float> dim_mu1_d0sig_bs_lin       ;
    std::vector<float> dim_mu1_dz_pv              ;
    std::vector<float> dim_mu1_dz_bs              ;
    std::vector<float> dim_mu1_dz_pv_lin          ;
    std::vector<float> dim_mu1_dz_bs_lin          ;
    std::vector<float> dim_mu1_dzsig_pv           ;
    std::vector<float> dim_mu1_dzsig_bs           ;
    std::vector<float> dim_mu1_dzsig_pv_lin       ;
    std::vector<float> dim_mu1_dzsig_bs_lin       ;
    // number of hits track has upstream of the vertex
    std::vector<int  > dim_mu1_hitsBeforeVtx      ;
    // number of missing hits between the vertex position
    // and the innermost valid hit on the track
    std::vector<int  > dim_mu1_missingHitsAfterVtx;

    std::vector<int  > dim_mu2_idx                ;
    std::vector<float> dim_mu2_px                 ;
    std::vector<float> dim_mu2_py                 ;
    std::vector<float> dim_mu2_pz                 ;
    std::vector<float> dim_mu2_ptError            ;
    std::vector<float> dim_mu2_eta                ;
    std::vector<float> dim_mu2_phi                ;
    std::vector<int  > dim_mu2_charge             ;
    std::vector<float> dim_mu2_d0_pv              ;
    std::vector<float> dim_mu2_d0_bs              ;
    std::vector<float> dim_mu2_d0_pv_lin          ;
    std::vector<float> dim_mu2_d0_bs_lin          ;
    std::vector<float> dim_mu2_d0sig_pv           ;
    std::vector<float> dim_mu2_d0sig_bs           ;
    std::vector<float> dim_mu2_d0sig_pv_lin       ;
    std::vector<float> dim_mu2_d0sig_bs_lin       ;
    std::vector<float> dim_mu2_dz_pv              ;
    std::vector<float> dim_mu2_dz_bs              ;
    std::vector<float> dim_mu2_dz_pv_lin          ;
    std::vector<float> dim_mu2_dz_bs_lin          ;
    std::vector<float> dim_mu2_dzsig_pv           ;
    std::vector<float> dim_mu2_dzsig_bs           ;
    std::vector<float> dim_mu2_dzsig_pv_lin       ;
    std::vector<float> dim_mu2_dzsig_bs_lin       ;
    std::vector<int  > dim_mu2_hitsBeforeVtx      ;
    std::vector<int  > dim_mu2_missingHitsAfterVtx;

    // methods
    void Declarations()
    {
      Declare("dim_pt"                     , dim_pt                     );
      Declare("dim_eta"                    , dim_eta                    );
      Declare("dim_phi"                    , dim_phi                    );
      Declare("dim_mass"                   , dim_mass                   );
      Declare("dim_p"                      , dim_p                      );
      Declare("dim_x"                      , dim_x                      );
      Declare("dim_y"                      , dim_y                      );
      Declare("dim_z"                      , dim_z                      );
      Declare("dim_Lxy_pv"                 , dim_Lxy_pv                 );
      Declare("dim_LxySig_pv"              , dim_LxySig_pv              );
      Declare("dim_Lxy_bs"                 , dim_Lxy_bs                 );
      Declare("dim_LxySig_bs"              , dim_LxySig_bs              );
      Declare("dim_deltaR"                 , dim_deltaR                 );
      Declare("dim_normChi2"               , dim_normChi2               );
      Declare("dim_cosAlpha"               , dim_cosAlpha               );
      Declare("dim_deltaPhi"               , dim_deltaPhi               );

      Declare("dim_mu1_idx"                , dim_mu1_idx                );
      Declare("dim_mu1_px"                 , dim_mu1_px                 );
      Declare("dim_mu1_py"                 , dim_mu1_py                 );
      Declare("dim_mu1_pz"                 , dim_mu1_pz                 );
      Declare("dim_mu1_ptError"            , dim_mu1_ptError            );
      Declare("dim_mu1_eta"                , dim_mu1_eta                );
      Declare("dim_mu1_phi"                , dim_mu1_phi                );
      Declare("dim_mu1_charge"             , dim_mu1_charge             );
      Declare("dim_mu1_d0_pv"              , dim_mu1_d0_pv              );
      Declare("dim_mu1_d0_bs"              , dim_mu1_d0_bs              );
      Declare("dim_mu1_d0_pv_lin"          , dim_mu1_d0_pv_lin          );
      Declare("dim_mu1_d0_bs_lin"          , dim_mu1_d0_bs_lin          );
      Declare("dim_mu1_d0sig_pv"           , dim_mu1_d0sig_pv           );
      Declare("dim_mu1_d0sig_bs"           , dim_mu1_d0sig_bs           );
      Declare("dim_mu1_d0sig_pv_lin"       , dim_mu1_d0sig_pv_lin       );
      Declare("dim_mu1_d0sig_bs_lin"       , dim_mu1_d0sig_bs_lin       );
      Declare("dim_mu1_dz_pv"              , dim_mu1_dz_pv              );
      Declare("dim_mu1_dz_bs"              , dim_mu1_dz_bs              );
      Declare("dim_mu1_dz_pv_lin"          , dim_mu1_dz_pv_lin          );
      Declare("dim_mu1_dz_bs_lin"          , dim_mu1_dz_bs_lin          );
      Declare("dim_mu1_dzsig_pv"           , dim_mu1_dzsig_pv           );
      Declare("dim_mu1_dzsig_bs"           , dim_mu1_dzsig_bs           );
      Declare("dim_mu1_dzsig_pv_lin"       , dim_mu1_dzsig_pv_lin       );
      Declare("dim_mu1_dzsig_bs_lin"       , dim_mu1_dzsig_bs_lin       );
      Declare("dim_mu1_hitsBeforeVtx"      , dim_mu1_hitsBeforeVtx      );
      Declare("dim_mu1_missingHitsAfterVtx", dim_mu1_missingHitsAfterVtx);

      Declare("dim_mu2_idx"                , dim_mu2_idx                );
      Declare("dim_mu2_px"                 , dim_mu2_px                 );
      Declare("dim_mu2_py"                 , dim_mu2_py                 );
      Declare("dim_mu2_pz"                 , dim_mu2_pz                 );
      Declare("dim_mu2_ptError"            , dim_mu2_ptError            );
      Declare("dim_mu2_eta"                , dim_mu2_eta                );
      Declare("dim_mu2_phi"                , dim_mu2_phi                );
      Declare("dim_mu2_charge"             , dim_mu2_charge             );
      Declare("dim_mu2_d0_pv"              , dim_mu2_d0_pv              );
      Declare("dim_mu2_d0_bs"              , dim_mu2_d0_bs              );
      Declare("dim_mu2_d0_pv_lin"          , dim_mu2_d0_pv_lin          );
      Declare("dim_mu2_d0_bs_lin"          , dim_mu2_d0_bs_lin          );
      Declare("dim_mu2_d0sig_pv"           , dim_mu2_d0sig_pv           );
      Declare("dim_mu2_d0sig_bs"           , dim_mu2_d0sig_bs           );
      Declare("dim_mu2_d0sig_pv_lin"       , dim_mu2_d0sig_pv_lin       );
      Declare("dim_mu2_d0sig_bs_lin"       , dim_mu2_d0sig_bs_lin       );
      Declare("dim_mu2_dz_pv"              , dim_mu2_dz_pv              );
      Declare("dim_mu2_dz_bs"              , dim_mu2_dz_bs              );
      Declare("dim_mu2_dz_pv_lin"          , dim_mu2_dz_pv_lin          );
      Declare("dim_mu2_dz_bs_lin"          , dim_mu2_dz_bs_lin          );
      Declare("dim_mu2_dzsig_pv"           , dim_mu2_dzsig_pv           );
      Declare("dim_mu2_dzsig_bs"           , dim_mu2_dzsig_bs           );
      Declare("dim_mu2_dzsig_pv_lin"       , dim_mu2_dzsig_pv_lin       );
      Declare("dim_mu2_dzsig_bs_lin"       , dim_mu2_dzsig_bs_lin       );
      Declare("dim_mu2_hitsBeforeVtx"      , dim_mu2_hitsBeforeVtx      );
      Declare("dim_mu2_missingHitsAfterVtx", dim_mu2_missingHitsAfterVtx);
    }

    void Reset()
    {
      dim_pt                     .clear();
      dim_eta                    .clear();
      dim_phi                    .clear();
      dim_mass                   .clear();
      dim_p                      .clear();
      dim_x                      .clear();
      dim_y                      .clear();
      dim_z                      .clear();
      dim_Lxy_pv                 .clear();
      dim_LxySig_pv              .clear();
      dim_Lxy_bs                 .clear();
      dim_LxySig_bs              .clear();
      dim_deltaR                 .clear();
      dim_normChi2               .clear();
      dim_cosAlpha               .clear();
      dim_deltaPhi               .clear();

      dim_mu1_idx                .clear();
      dim_mu1_px                 .clear();
      dim_mu1_py                 .clear();
      dim_mu1_pz                 .clear();
      dim_mu1_ptError            .clear();
      dim_mu1_eta                .clear();
      dim_mu1_phi                .clear();
      dim_mu1_charge             .clear();
      dim_mu1_d0_pv              .clear();
      dim_mu1_d0_bs              .clear();
      dim_mu1_d0_pv_lin          .clear();
      dim_mu1_d0_bs_lin          .clear();
      dim_mu1_d0sig_pv           .clear();
      dim_mu1_d0sig_bs           .clear();
      dim_mu1_d0sig_pv_lin       .clear();
      dim_mu1_d0sig_bs_lin       .clear();
      dim_mu1_dz_pv              .clear();
      dim_mu1_dz_bs              .clear();
      dim_mu1_dz_pv_lin          .clear();
      dim_mu1_dz_bs_lin          .clear();
      dim_mu1_dzsig_pv           .clear();
      dim_mu1_dzsig_bs           .clear();
      dim_mu1_dzsig_pv_lin       .clear();
      dim_mu1_dzsig_bs_lin       .clear();
      dim_mu1_hitsBeforeVtx      .clear();
      dim_mu1_missingHitsAfterVtx.clear();

      dim_mu2_idx                .clear();
      dim_mu2_px                 .clear();
      dim_mu2_py                 .clear();
      dim_mu2_pz                 .clear();
      dim_mu2_ptError            .clear();
      dim_mu2_eta                .clear();
      dim_mu2_phi                .clear();
      dim_mu2_charge             .clear();
      dim_mu2_d0_pv              .clear();
      dim_mu2_d0_bs              .clear();
      dim_mu2_d0_pv_lin          .clear();
      dim_mu2_d0_bs_lin          .clear();
      dim_mu2_d0sig_pv           .clear();
      dim_mu2_d0sig_bs           .clear();
      dim_mu2_d0sig_pv_lin       .clear();
      dim_mu2_d0sig_bs_lin       .clear();
      dim_mu2_dz_pv              .clear();
      dim_mu2_dz_bs              .clear();
      dim_mu2_dz_pv_lin          .clear();
      dim_mu2_dz_bs_lin          .clear();
      dim_mu2_dzsig_pv           .clear();
      dim_mu2_dzsig_bs           .clear();
      dim_mu2_dzsig_pv_lin       .clear();
      dim_mu2_dzsig_bs_lin       .clear();
      dim_mu2_hitsBeforeVtx      .clear();
      dim_mu2_missingHitsAfterVtx.clear();

    }

    void Fill(const edm::EventSetup& iSetup,
        const edm::Handle<reco::TrackCollection> &dsamuonsHandle,
        const edm::ESHandle<TransientTrackBuilder>& ttB,
        const edm::Handle<reco::VertexCollection> &verticesHandle,
        const edm::Handle<reco::BeamSpot> &beamspotHandle,
        const edm::Handle<pat::MuonCollection> &patmuonsHandle);

    void FillDimuon(int i, int j,
        const reco::Track& tk1, const reco::Track& tk2,
        const edm::EventSetup& iSetup,
        const edm::ESHandle<TransientTrackBuilder>& ttB,
        const edm::Handle<reco::VertexCollection> &verticesHandle,
        const edm::Handle<reco::BeamSpot> &beamspotHandle,
        bool debug);

    reco::Vertex RefittedVertex(const edm::ESHandle<TransientTrackBuilder>& ttB,
        const reco::Vertex& pv,
        const reco::BeamSpot& bs,
        const reco::TransientTrack& tt1,
        const reco::TransientTrack& tt2,
        const bool debug = false);

    virtual bool alreadyPrinted() { return alreadyPrinted_; }
    virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
