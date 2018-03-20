#ifndef RSAMUONBRANCHES_H
#define RSAMUONBRANCHES_H

// CMSSW includes
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// muon branch collection
class RSAMuonBranches : BranchCollection
{
	public:
		// constructor
		RSAMuonBranches(TreeContainer &tree) : BranchCollection(tree)
		{
			Declare("rsamu_pdgID"        , rsamu_pdgID        );
			Declare("rsamu_pt"           , rsamu_pt           );
			Declare("rsamu_eta"          , rsamu_eta          );
			Declare("rsamu_phi"          , rsamu_phi          );
			Declare("rsamu_mass"         , rsamu_mass         );
			Declare("rsamu_energy"       , rsamu_energy       );
			Declare("rsamu_charge"       , rsamu_charge       );
			Declare("rsamu_x"            , rsamu_x            );
			Declare("rsamu_y"            , rsamu_y            );
			Declare("rsamu_z"            , rsamu_z            );

			Declare("rsamu_d0"           , rsamu_d0           );
			Declare("rsamu_d0MV"         , rsamu_d0MV         );

			Declare("rsamu_normChi2"     , rsamu_normChi2     );
			Declare("rsamu_d0Sig"        , rsamu_d0Sig        );
			Declare("rsamu_d0MVSig"      , rsamu_d0MVSig      );
			Declare("rsamu_nMuonHits"    , rsamu_nMuonHits    );
			Declare("rsamu_nDTStations"  , rsamu_nDTStations  );
			Declare("rsamu_nCSCStations" , rsamu_nCSCStations );
		}

		// members
		std::vector<int  > rsamu_pdgID        ;
		std::vector<float> rsamu_pt           ;
		std::vector<float> rsamu_eta          ;
		std::vector<float> rsamu_phi          ;
		std::vector<float> rsamu_mass         ;
		std::vector<float> rsamu_energy       ;
		std::vector<int  > rsamu_charge       ;
		std::vector<float> rsamu_x            ;
		std::vector<float> rsamu_y            ;
		std::vector<float> rsamu_z            ;

		std::vector<float> rsamu_d0           ;
		std::vector<float> rsamu_d0MV         ;

		std::vector<float> rsamu_normChi2     ;
		std::vector<float> rsamu_d0Sig        ;
		std::vector<float> rsamu_d0MVSig      ;
		std::vector<int  > rsamu_nMuonHits    ;
		std::vector<int  > rsamu_nDTStations  ;
		std::vector<int  > rsamu_nCSCStations ;

		// methods
		virtual void Reset()
		{
			rsamu_pdgID        .clear();
			rsamu_pt           .clear();
			rsamu_eta          .clear();
			rsamu_phi          .clear();
			rsamu_mass         .clear();
			rsamu_energy       .clear();
			rsamu_charge       .clear();
			rsamu_x            .clear();
			rsamu_y            .clear();
			rsamu_z            .clear();

			rsamu_d0           .clear();
			rsamu_d0MV         .clear();

			rsamu_normChi2     .clear();
			rsamu_d0Sig        .clear();
			rsamu_d0MVSig      .clear();
			rsamu_nMuonHits    .clear();
			rsamu_nDTStations  .clear();
			rsamu_nCSCStations .clear();
		}

		void Fill(const reco::TrackCollection &muons, const reco::VertexCollection &vertices);
};

#endif
