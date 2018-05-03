#ifndef MUONBRANCHES_H
#define MUONBRANCHES_H

// CMSSW includes
#include "DataFormats/PatCandidates/interface/Muon.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// muon branch collection
class MuonBranches : BranchCollection
{
	public:
		// constructor
		MuonBranches(TreeContainer &tree, const bool DECLARE=true) : BranchCollection(tree) { Reset(); if (DECLARE) {Declarations();} }

		// members
		std::vector<int  > mu_pdgID ;
		std::vector<float> mu_pt    ;
		std::vector<float> mu_eta   ;
		std::vector<float> mu_phi   ;
		std::vector<float> mu_mass  ;
		std::vector<float> mu_energy;
		std::vector<int  > mu_charge;
		std::vector<float> mu_x     ;
		std::vector<float> mu_y     ;
		std::vector<float> mu_z     ;
		std::vector<bool > mu_isSlim;

		std::vector<int  > mu_gen_pdgID ;
		std::vector<float> mu_gen_pt    ;
		std::vector<float> mu_gen_eta   ;
		std::vector<float> mu_gen_phi   ;
		std::vector<float> mu_gen_mass  ;
		std::vector<float> mu_gen_energy;
		std::vector<int  > mu_gen_charge;
		std::vector<float> mu_gen_x     ;
		std::vector<float> mu_gen_y     ;
		std::vector<float> mu_gen_z     ;

		// methods
		void Declarations()
		{
			Declare("mu_pdgID" , mu_pdgID );
			Declare("mu_pt"    , mu_pt    );
			Declare("mu_eta"   , mu_eta   );
			Declare("mu_phi"   , mu_phi   );
			Declare("mu_mass"  , mu_mass  );
			Declare("mu_energy", mu_energy);
			Declare("mu_charge", mu_charge);
			Declare("mu_x"     , mu_x     );
			Declare("mu_y"     , mu_y     );
			Declare("mu_z"     , mu_z     );
			Declare("mu_isSlim", mu_isSlim);

			Declare("mu_gen_pdgID" , mu_gen_pdgID );
			Declare("mu_gen_pt"    , mu_gen_pt    );
			Declare("mu_gen_eta"   , mu_gen_eta   );
			Declare("mu_gen_phi"   , mu_gen_phi   );
			Declare("mu_gen_mass"  , mu_gen_mass  );
			Declare("mu_gen_energy", mu_gen_energy);
			Declare("mu_gen_charge", mu_gen_charge);
			Declare("mu_gen_x"     , mu_gen_x     );
			Declare("mu_gen_y"     , mu_gen_y     );
			Declare("mu_gen_z"     , mu_gen_z     );
		}

		void Reset()
		{
			mu_pdgID .clear();
			mu_pt    .clear();
			mu_eta   .clear();
			mu_phi   .clear();
			mu_mass  .clear();
			mu_energy.clear();
			mu_charge.clear();
			mu_x     .clear();
			mu_y     .clear();
			mu_z     .clear();
			mu_isSlim.clear();

			mu_gen_pdgID .clear();
			mu_gen_pt    .clear();
			mu_gen_eta   .clear();
			mu_gen_phi   .clear();
			mu_gen_mass  .clear();
			mu_gen_energy.clear();
			mu_gen_charge.clear();
			mu_gen_x     .clear();
			mu_gen_y     .clear();
			mu_gen_z     .clear();
		}

		void Fill(const pat::MuonCollection &muons);
		bool isSlim(const pat::Muon &mu);
};

#endif
