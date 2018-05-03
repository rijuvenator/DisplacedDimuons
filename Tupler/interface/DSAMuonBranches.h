#ifndef DSAMUONBRANCHES_H
#define DSAMUONBRANCHES_H

// CMSSW includes
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// muon branch collection
class DSAMuonBranches : BranchCollection
{
	public:
		// constructor
		DSAMuonBranches(TreeContainer &tree, const bool DECLARE=true) : BranchCollection(tree) { Reset(); if (DECLARE) {Declarations();} }

		// members
		std::vector<int  > dsamu_pdgID        ;
		std::vector<float> dsamu_pt           ;
		std::vector<float> dsamu_eta          ;
		std::vector<float> dsamu_phi          ;
		std::vector<float> dsamu_mass         ;
		std::vector<float> dsamu_energy       ;
		std::vector<int  > dsamu_charge       ;
		std::vector<float> dsamu_x            ;
		std::vector<float> dsamu_y            ;
		std::vector<float> dsamu_z            ;

		std::vector<float> dsamu_d0           ;
		std::vector<float> dsamu_d0MV         ;

		std::vector<float> dsamu_normChi2     ;
		std::vector<float> dsamu_d0Sig        ;
		std::vector<float> dsamu_d0MVSig      ;
		std::vector<int  > dsamu_nMuonHits    ;
		std::vector<int  > dsamu_nDTStations  ;
		std::vector<int  > dsamu_nCSCStations ;

		// methods
		void Declarations()
		{
			Declare("dsamu_pdgID"        , dsamu_pdgID        );
			Declare("dsamu_pt"           , dsamu_pt           );
			Declare("dsamu_eta"          , dsamu_eta          );
			Declare("dsamu_phi"          , dsamu_phi          );
			Declare("dsamu_mass"         , dsamu_mass         );
			Declare("dsamu_energy"       , dsamu_energy       );
			Declare("dsamu_charge"       , dsamu_charge       );
			Declare("dsamu_x"            , dsamu_x            );
			Declare("dsamu_y"            , dsamu_y            );
			Declare("dsamu_z"            , dsamu_z            );

			Declare("dsamu_d0"           , dsamu_d0           );
			Declare("dsamu_d0MV"         , dsamu_d0MV         );

			Declare("dsamu_normChi2"     , dsamu_normChi2     );
			Declare("dsamu_d0Sig"        , dsamu_d0Sig        );
			Declare("dsamu_d0MVSig"      , dsamu_d0MVSig      );
			Declare("dsamu_nMuonHits"    , dsamu_nMuonHits    );
			Declare("dsamu_nDTStations"  , dsamu_nDTStations  );
			Declare("dsamu_nCSCStations" , dsamu_nCSCStations );
		}

		void Reset()
		{
			dsamu_pdgID        .clear();
			dsamu_pt           .clear();
			dsamu_eta          .clear();
			dsamu_phi          .clear();
			dsamu_mass         .clear();
			dsamu_energy       .clear();
			dsamu_charge       .clear();
			dsamu_x            .clear();
			dsamu_y            .clear();
			dsamu_z            .clear();

			dsamu_d0           .clear();
			dsamu_d0MV         .clear();

			dsamu_normChi2     .clear();
			dsamu_d0Sig        .clear();
			dsamu_d0MVSig      .clear();
			dsamu_nMuonHits    .clear();
			dsamu_nDTStations  .clear();
			dsamu_nCSCStations .clear();
		}

		void Fill(const reco::TrackCollection &muons, const reco::VertexCollection &vertices);
};

#endif
