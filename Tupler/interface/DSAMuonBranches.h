#ifndef DSAMUONBRANCHES_H
#define DSAMUONBRANCHES_H

// CMSSW includes
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// muon branch collection
class DSAMuonBranches : BranchCollection
{
	public:
		// constructor
		DSAMuonBranches(TreeContainer &tree) : BranchCollection(tree)
		{
			Declare("dsamu_pdgID" , dsamu_pdgID );
			Declare("dsamu_pt"    , dsamu_pt    );
			Declare("dsamu_eta"   , dsamu_eta   );
			Declare("dsamu_phi"   , dsamu_phi   );
			Declare("dsamu_mass"  , dsamu_mass  );
			Declare("dsamu_energy", dsamu_energy);
			Declare("dsamu_charge", dsamu_charge);
			Declare("dsamu_x"     , dsamu_x     );
			Declare("dsamu_y"     , dsamu_y     );
			Declare("dsamu_z"     , dsamu_z     );

			Declare("dsamu_d0"    , dsamu_d0    );
		}

		// members
		std::vector<int  > dsamu_pdgID ;
		std::vector<float> dsamu_pt    ;
		std::vector<float> dsamu_eta   ;
		std::vector<float> dsamu_phi   ;
		std::vector<float> dsamu_mass  ;
		std::vector<float> dsamu_energy;
		std::vector<int  > dsamu_charge;
		std::vector<float> dsamu_x     ;
		std::vector<float> dsamu_y     ;
		std::vector<float> dsamu_z     ;

		std::vector<float> dsamu_d0    ;

		// methods
		virtual void Reset()
		{
			dsamu_pdgID .clear();
			dsamu_pt    .clear();
			dsamu_eta   .clear();
			dsamu_phi   .clear();
			dsamu_mass  .clear();
			dsamu_energy.clear();
			dsamu_charge.clear();
			dsamu_x     .clear();
			dsamu_y     .clear();
			dsamu_z     .clear();

			dsamu_d0    .clear();
		}

		void Fill(const reco::TrackCollection &muons);
};

#endif
