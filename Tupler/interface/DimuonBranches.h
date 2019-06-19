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
#include "DataFormats/RecoCandidate/interface/IsoDepositDirection.h"

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
    std::vector<float> dim_p                      ;
    std::vector<float> dim_mass                   ;
    std::vector<float> dim_massunc                ;
    std::vector<float> dim_x                      ;
    std::vector<float> dim_y                      ;
    std::vector<float> dim_z                      ;
    std::vector<float> dim_dca                    ;
    std::vector<float> dim_pca_x                  ;
    std::vector<float> dim_pca_y                  ;
    std::vector<float> dim_pca_z                  ;
    std::vector<float> dim_normChi2               ;
    std::vector<float> dim_Lxy_pv                 ;
    std::vector<float> dim_LxySig_pv              ;
    std::vector<float> dim_Lxy_bs                 ;
    std::vector<float> dim_LxySig_bs              ;
    std::vector<float> dim_deltaPhi               ;
    std::vector<float> dim_deltaR                 ;
    std::vector<float> dim_cosAlpha               ;
    std::vector<float> dim_cosAlphaOrig           ;
    std::vector<float> dim_isoPmumu               ;
    std::vector<float> dim_isoLxy                 ;

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
    //isolation variable
    std::vector<float> dim_mu1_iso				  ;

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
    std::vector<float> dim_mu2_iso				  ;

    // methods
    void Declarations()
    {
      Declare("dim_pt"                     , dim_pt                     );
      Declare("dim_eta"                    , dim_eta                    );
      Declare("dim_phi"                    , dim_phi                    );
      Declare("dim_p"                      , dim_p                      );
      Declare("dim_mass"                   , dim_mass                   );
      Declare("dim_massunc"                , dim_massunc                );
      Declare("dim_x"                      , dim_x                      );
      Declare("dim_y"                      , dim_y                      );
      Declare("dim_z"                      , dim_z                      );
      Declare("dim_dca"                    , dim_dca                    );
      Declare("dim_pca_x"                  , dim_pca_x                  );
      Declare("dim_pca_y"                  , dim_pca_y                  );
      Declare("dim_pca_z"                  , dim_pca_z                  );
      Declare("dim_normChi2"               , dim_normChi2               );
      Declare("dim_Lxy_pv"                 , dim_Lxy_pv                 );
      Declare("dim_LxySig_pv"              , dim_LxySig_pv              );
      Declare("dim_Lxy_bs"                 , dim_Lxy_bs                 );
      Declare("dim_LxySig_bs"              , dim_LxySig_bs              );
      Declare("dim_deltaPhi"               , dim_deltaPhi               );
      Declare("dim_deltaR"                 , dim_deltaR                 );
      Declare("dim_cosAlpha"               , dim_cosAlpha               );
      Declare("dim_cosAlphaOrig"           , dim_cosAlphaOrig           );
      Declare("dim_isoPmumu"               , dim_isoPmumu               );
      Declare("dim_isoLxy"                 , dim_isoLxy                 );

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
      Declare("dim_mu1_iso"				   , dim_mu1_iso				);

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
      Declare("dim_mu2_iso"				   , dim_mu2_iso				);
    }

    void Reset()
    {
      dim_pt                     .clear();
      dim_eta                    .clear();
      dim_phi                    .clear();
      dim_p                      .clear();
      dim_mass                   .clear();
      dim_massunc                .clear();
      dim_x                      .clear();
      dim_y                      .clear();
      dim_z                      .clear();
      dim_dca                    .clear();
      dim_pca_x                  .clear();
      dim_pca_y                  .clear();
      dim_pca_z                  .clear();
      dim_normChi2               .clear();
      dim_Lxy_pv                 .clear();
      dim_LxySig_pv              .clear();
      dim_Lxy_bs                 .clear();
      dim_LxySig_bs              .clear();
      dim_deltaPhi               .clear();
      dim_deltaR                 .clear();
      dim_cosAlpha               .clear();
      dim_cosAlphaOrig           .clear();
      dim_isoPmumu               .clear();
      dim_isoLxy                 .clear();

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
      dim_mu1_iso				 .clear();

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
      dim_mu2_iso				 .clear();
    }


    void Fill(const edm::EventSetup& iSetup,
	      const edm::Handle<reco::TrackCollection> &dsamuonsHandle,
	      const edm::ESHandle<TransientTrackBuilder>& ttB,
	      const edm::Handle<reco::VertexCollection> &verticesHandle,
	      const edm::Handle<reco::BeamSpot> &beamspotHandle,
	      const edm::Handle<pat::MuonCollection> &patmuonsHandle,
	      const edm::ESHandle<MagneticField>& magfield,
	      const edm::Handle<reco::TrackCollection> &generalTracksHandle);

    void FillDimuon(int i, int j,
		    const reco::Track& tk1, const reco::Track& tk2,
		    const edm::EventSetup& iSetup,
		    const edm::ESHandle<TransientTrackBuilder>& ttB,
		    const edm::Handle<reco::VertexCollection> &verticesHandle,
		    const edm::Handle<reco::BeamSpot> &beamspotHandle,
		    const edm::ESHandle<MagneticField>& magfield,
		    const edm::Handle<reco::TrackCollection> &generalTracksHandle,
		    bool debug);


    static float Isolation(
    		const reco::isodeposit::Direction& isoConeDirection,
			const reco::Vertex& pv,
			const TLorentzVector& momentum,
			const reco::BeamSpot &beamspot,
			const reco::TrackCollection &cleanedTracks,
			bool debug = false);

    static const reco::TrackCollection RemoveTracksFromCollection(
    		const reco::TrackCollection& trackCollection,
			const std::vector<reco::TransientTrack> tracksToRemove,
			bool debug = false);

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
