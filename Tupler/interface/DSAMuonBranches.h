#ifndef DSAMUONBRANCHES_H
#define DSAMUONBRANCHES_H

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

		std::vector<float> dsamu_px           ;
		std::vector<float> dsamu_py           ;
		std::vector<float> dsamu_pz           ;
		std::vector<float> dsamu_eta          ;
		std::vector<float> dsamu_phi          ;
		std::vector<int  > dsamu_charge       ;
		std::vector<float> dsamu_x            ;
		std::vector<float> dsamu_y            ;
		std::vector<float> dsamu_z            ;

		std::vector<float> dsamu_chi2         ;
		std::vector<int>   dsamu_ndof         ;

		std::vector<int  > dsamu_nMuonHits    ;
		std::vector<int  > dsamu_nDTHits      ;
		std::vector<int  > dsamu_nCSCHits     ;
		std::vector<int  > dsamu_nDTStations  ;
		std::vector<int  > dsamu_nCSCStations ;

		std::vector<float> dsamu_d0_pv        ;
		std::vector<float> dsamu_d0_bs        ;
		std::vector<float> dsamu_d0_pv_lin    ;
		std::vector<float> dsamu_d0_bs_lin    ;
		std::vector<float> dsamu_d0sig_pv     ;
		std::vector<float> dsamu_d0sig_bs     ;
		std::vector<float> dsamu_d0sig_pv_lin ;
		std::vector<float> dsamu_d0sig_bs_lin ;

		std::vector<float> dsamu_dz_pv        ;
		std::vector<float> dsamu_dz_bs        ;
		std::vector<float> dsamu_dz_pv_lin    ;
		std::vector<float> dsamu_dz_bs_lin    ;
		std::vector<float> dsamu_dzsig_pv     ;
		std::vector<float> dsamu_dzsig_bs     ;
		std::vector<float> dsamu_dzsig_pv_lin ;
		std::vector<float> dsamu_dzsig_bs_lin ;

		// methods
		void Declarations()
		{
			Declare("dsamu_px"           , dsamu_px           );
			Declare("dsamu_py"           , dsamu_py           );
			Declare("dsamu_pz"           , dsamu_pz           );
			Declare("dsamu_eta"          , dsamu_eta          );
			Declare("dsamu_phi"          , dsamu_phi          );
			Declare("dsamu_charge"       , dsamu_charge       );
			Declare("dsamu_x"            , dsamu_x            );
			Declare("dsamu_y"            , dsamu_y            );
			Declare("dsamu_z"            , dsamu_z            );

			Declare("dsamu_chi2"         , dsamu_chi2         );
			Declare("dsamu_ndof"         , dsamu_ndof         );

			Declare("dsamu_nMuonHits"    , dsamu_nMuonHits    );
			Declare("dsamu_nDTHits"      , dsamu_nDTHits      );
			Declare("dsamu_nCSCHits"     , dsamu_nCSCHits     );
			Declare("dsamu_nDTStations"  , dsamu_nDTStations  );
			Declare("dsamu_nCSCStations" , dsamu_nCSCStations );

			Declare("dsamu_d0_pv"        , dsamu_d0_pv        );
			Declare("dsamu_d0_bs"        , dsamu_d0_bs        );
			Declare("dsamu_d0_pv_lin"    , dsamu_d0_pv_lin    );
			Declare("dsamu_d0_bs_lin"    , dsamu_d0_bs_lin    );
			Declare("dsamu_d0sig_pv"     , dsamu_d0sig_pv     );
			Declare("dsamu_d0sig_bs"     , dsamu_d0sig_bs     );
			Declare("dsamu_d0sig_pv_lin" , dsamu_d0sig_pv_lin );
			Declare("dsamu_d0sig_bs_lin" , dsamu_d0sig_bs_lin );

			Declare("dsamu_dz_pv"        , dsamu_dz_pv        );
			Declare("dsamu_dz_bs"        , dsamu_dz_bs        );
			Declare("dsamu_dz_pv_lin"    , dsamu_dz_pv_lin    );
			Declare("dsamu_dz_bs_lin"    , dsamu_dz_bs_lin    );
			Declare("dsamu_dzsig_pv"     , dsamu_dzsig_pv     );
			Declare("dsamu_dzsig_bs"     , dsamu_dzsig_bs     );
			Declare("dsamu_dzsig_pv_lin" , dsamu_dzsig_pv_lin );
			Declare("dsamu_dzsig_bs_lin" , dsamu_dzsig_bs_lin );
		}

		void Reset()
		{
			dsamu_px           .clear();
			dsamu_py           .clear();
			dsamu_pz           .clear();
			dsamu_eta          .clear();
			dsamu_phi          .clear();
			dsamu_charge       .clear();
			dsamu_x            .clear();
			dsamu_y            .clear();
			dsamu_z            .clear();

			dsamu_chi2         .clear();
			dsamu_ndof         .clear();

			dsamu_nMuonHits    .clear();
			dsamu_nDTHits      .clear();
			dsamu_nCSCHits     .clear();
			dsamu_nDTStations  .clear();
			dsamu_nCSCStations .clear();

			dsamu_d0_pv        .clear();
			dsamu_d0_bs        .clear();
			dsamu_d0_pv_lin    .clear();
			dsamu_d0_bs_lin    .clear();
			dsamu_d0sig_pv     .clear();
			dsamu_d0sig_bs     .clear();
			dsamu_d0sig_pv_lin .clear();
			dsamu_d0sig_bs_lin .clear();

			dsamu_dz_pv        .clear();
			dsamu_dz_bs        .clear();
			dsamu_dz_pv_lin    .clear();
			dsamu_dz_bs_lin    .clear();
			dsamu_dzsig_pv     .clear();
			dsamu_dzsig_bs     .clear();
			dsamu_dzsig_pv_lin .clear();
			dsamu_dzsig_bs_lin .clear();
		}

		void Fill(const edm::Handle<reco::TrackCollection> &muonsHandle,
			  const edm::ESHandle<TransientTrackBuilder>& ttB,
			  const edm::Handle<reco::VertexCollection> &verticesHandle,
			  const edm::Handle<reco::BeamSpot> &beamspotHandle);

		virtual bool alreadyPrinted() { return alreadyPrinted_; }
		virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
