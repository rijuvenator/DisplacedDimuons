#ifndef DIMUONBRANCHES_H
#define DIMUONBRANCHES_H

// CMSSW includes
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

#include "FWCore/Framework/interface/Event.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "RecoVertex/VertexPrimitives/interface/TransientVertex.h"
#include "RecoVertex/KalmanVertexFit/interface/KalmanVertexFitter.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// ROOT includes
#include "TVector3.h"
#include "TLorentzVector.h"

// muon branch collection
class DimuonBranches : BranchCollection
{
	public:
		// constructor
		DimuonBranches(TreeContainer &tree, const bool DECLARE=true) : BranchCollection(tree) { Reset(); if (DECLARE) {Declarations();} }

		// members
		std::vector<unsigned int> dim_idx1    ;
		std::vector<unsigned int> dim_idx2    ;
		std::vector<int         > dim_pdgID   ;
		std::vector<float       > dim_pt      ;
		std::vector<float       > dim_eta     ;
		std::vector<float       > dim_phi     ;
		std::vector<float       > dim_mass    ;
		std::vector<float       > dim_energy  ;
		std::vector<int         > dim_charge  ;
		std::vector<float       > dim_x       ;
		std::vector<float       > dim_y       ;
		std::vector<float       > dim_z       ;
		std::vector<float       > dim_Lxy     ;
		std::vector<float       > dim_deltaR  ;
		std::vector<float       > dim_normChi2;
		std::vector<float       > dim_cosAlpha;
		std::vector<float       > dim_deltaPhi;

		// methods
		void Declarations()
		{
			Declare("dim_idx1"    , dim_idx1    );
			Declare("dim_idx2"    , dim_idx2    );
			Declare("dim_pdgID"   , dim_pdgID   );
			Declare("dim_pt"      , dim_pt      );
			Declare("dim_eta"     , dim_eta     );
			Declare("dim_phi"     , dim_phi     );
			Declare("dim_mass"    , dim_mass    );
			Declare("dim_energy"  , dim_energy  );
			Declare("dim_charge"  , dim_charge  );
			Declare("dim_x"       , dim_x       );
			Declare("dim_y"       , dim_y       );
			Declare("dim_z"       , dim_z       );
			Declare("dim_Lxy"     , dim_Lxy     );
			Declare("dim_deltaR"  , dim_deltaR  );
			Declare("dim_normChi2", dim_normChi2);
			Declare("dim_cosAlpha", dim_cosAlpha);
			Declare("dim_deltaPhi", dim_deltaPhi);
		}

		void Reset()
		{
			dim_idx1    .clear();
			dim_idx2    .clear();
			dim_pdgID   .clear();
			dim_pt      .clear();
			dim_eta     .clear();
			dim_phi     .clear();
			dim_mass    .clear();
			dim_energy  .clear();
			dim_charge  .clear();
			dim_x       .clear();
			dim_y       .clear();
			dim_z       .clear();
			dim_Lxy     .clear();
			dim_deltaR  .clear();
			dim_normChi2.clear();
			dim_cosAlpha.clear();
			dim_deltaPhi.clear();
		}

		void Fill(const edm::EventSetup& iSetup, const reco::TrackCollection &muons, const reco::VertexCollection &vertices);
};

#endif
