#ifndef RSAMUONBRANCHES_H
#define RSAMUONBRANCHES_H

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
class RSAMuonBranches : public BranchCollection
{
	public:
		// constructor
		RSAMuonBranches(TreeContainer &tree, const bool DECLARE=true) :
			BranchCollection(tree, "reco::Track displacedStandAloneMuon collection", "RSA Muon info will not be filled")
		{
			Reset();
			if (DECLARE) Declarations();
		}

		// members
		static bool alreadyPrinted_;

		std::vector<float> rsamu_px           ;
		std::vector<float> rsamu_py           ;
		std::vector<float> rsamu_pz           ;
		std::vector<float> rsamu_eta          ;
		std::vector<float> rsamu_phi          ;
		std::vector<int  > rsamu_charge       ;
		std::vector<float> rsamu_x            ;
		std::vector<float> rsamu_y            ;
		std::vector<float> rsamu_z            ;

		std::vector<float> rsamu_chi2         ;
		std::vector<int>   rsamu_ndof         ;

		std::vector<int  > rsamu_nMuonHits    ;
		std::vector<int  > rsamu_nDTHits      ;
		std::vector<int  > rsamu_nCSCHits     ;
		std::vector<int  > rsamu_nDTStations  ;
		std::vector<int  > rsamu_nCSCStations ;

		std::vector<float> rsamu_d0_pv        ;
		std::vector<float> rsamu_d0_bs        ;
		std::vector<float> rsamu_d0_pv_lin    ;
		std::vector<float> rsamu_d0_bs_lin    ;
		std::vector<float> rsamu_d0sig_pv     ;
		std::vector<float> rsamu_d0sig_bs     ;
		std::vector<float> rsamu_d0sig_pv_lin ;
		std::vector<float> rsamu_d0sig_bs_lin ;

		std::vector<float> rsamu_dz_pv        ;
		std::vector<float> rsamu_dz_bs        ;
		std::vector<float> rsamu_dz_pv_lin    ;
		std::vector<float> rsamu_dz_bs_lin    ;
		std::vector<float> rsamu_dzsig_pv     ;
		std::vector<float> rsamu_dzsig_bs     ;
		std::vector<float> rsamu_dzsig_pv_lin ;
		std::vector<float> rsamu_dzsig_bs_lin ;

		// methods
		void Declarations()
		{
			Declare("rsamu_px"           , rsamu_px           );
			Declare("rsamu_py"           , rsamu_py           );
			Declare("rsamu_pz"           , rsamu_pz           );
			Declare("rsamu_eta"          , rsamu_eta          );
			Declare("rsamu_phi"          , rsamu_phi          );
			Declare("rsamu_charge"       , rsamu_charge       );
			Declare("rsamu_x"            , rsamu_x            );
			Declare("rsamu_y"            , rsamu_y            );
			Declare("rsamu_z"            , rsamu_z            );

			Declare("rsamu_chi2"         , rsamu_chi2         );
			Declare("rsamu_ndof"         , rsamu_ndof         );

			Declare("rsamu_nMuonHits"    , rsamu_nMuonHits    );
			Declare("rsamu_nDTHits"      , rsamu_nDTHits      );
			Declare("rsamu_nCSCHits"     , rsamu_nCSCHits     );
			Declare("rsamu_nDTStations"  , rsamu_nDTStations  );
			Declare("rsamu_nCSCStations" , rsamu_nCSCStations );

			Declare("rsamu_d0_pv"        , rsamu_d0_pv        );
			Declare("rsamu_d0_bs"        , rsamu_d0_bs        );
			Declare("rsamu_d0_pv_lin"    , rsamu_d0_pv_lin    );
			Declare("rsamu_d0_bs_lin"    , rsamu_d0_bs_lin    );
			Declare("rsamu_d0sig_pv"     , rsamu_d0sig_pv     );
			Declare("rsamu_d0sig_bs"     , rsamu_d0sig_bs     );
			Declare("rsamu_d0sig_pv_lin" , rsamu_d0sig_pv_lin );
			Declare("rsamu_d0sig_bs_lin" , rsamu_d0sig_bs_lin );

			Declare("rsamu_dz_pv"        , rsamu_dz_pv        );
			Declare("rsamu_dz_bs"        , rsamu_dz_bs        );
			Declare("rsamu_dz_pv_lin"    , rsamu_dz_pv_lin    );
			Declare("rsamu_dz_bs_lin"    , rsamu_dz_bs_lin    );
			Declare("rsamu_dzsig_pv"     , rsamu_dzsig_pv     );
			Declare("rsamu_dzsig_bs"     , rsamu_dzsig_bs     );
			Declare("rsamu_dzsig_pv_lin" , rsamu_dzsig_pv_lin );
			Declare("rsamu_dzsig_bs_lin" , rsamu_dzsig_bs_lin );
		}

		void Reset()
		{
			rsamu_px           .clear();
			rsamu_py           .clear();
			rsamu_pz           .clear();
			rsamu_eta          .clear();
			rsamu_phi          .clear();
			rsamu_charge       .clear();
			rsamu_x            .clear();
			rsamu_y            .clear();
			rsamu_z            .clear();

			rsamu_chi2         .clear();
			rsamu_ndof         .clear();

			rsamu_nMuonHits    .clear();
			rsamu_nDTHits      .clear();
			rsamu_nCSCHits     .clear();
			rsamu_nDTStations  .clear();
			rsamu_nCSCStations .clear();

			rsamu_d0_pv        .clear();
			rsamu_d0_bs        .clear();
			rsamu_d0_pv_lin    .clear();
			rsamu_d0_bs_lin    .clear();
			rsamu_d0sig_pv     .clear();
			rsamu_d0sig_bs     .clear();
			rsamu_d0sig_pv_lin .clear();
			rsamu_d0sig_bs_lin .clear();

			rsamu_dz_pv        .clear();
			rsamu_dz_bs        .clear();
			rsamu_dz_pv_lin    .clear();
			rsamu_dz_bs_lin    .clear();
			rsamu_dzsig_pv     .clear();
			rsamu_dzsig_bs     .clear();
			rsamu_dzsig_pv_lin .clear();
			rsamu_dzsig_bs_lin .clear();
		}

		void Fill(const edm::Handle<reco::TrackCollection> &muonsHandle,
			  const edm::ESHandle<TransientTrackBuilder>& ttB,
			  const edm::Handle<reco::VertexCollection> &verticesHandle,
			  const edm::Handle<reco::BeamSpot> &beamspotHandle);

		virtual bool alreadyPrinted() { return alreadyPrinted_; }
		virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
