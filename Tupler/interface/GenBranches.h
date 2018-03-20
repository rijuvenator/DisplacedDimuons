#ifndef GENBRANCHES_H
#define GENBRANCHES_H

// ROOT includes
#include "TVector3.h"

// CMSSW includes
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/HepMCCandidate/interface/GenParticleFwd.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// gen particle branch collection
class GenBranches : BranchCollection
{
	public:
		// constructor
		GenBranches(TreeContainer &tree) : BranchCollection(tree)
		{
			Declare("gen_weight", gen_weight, "F");

			Declare("gen_pdgID" , gen_pdgID );
			Declare("gen_pt"    , gen_pt    );
			Declare("gen_eta"   , gen_eta   );
			Declare("gen_phi"   , gen_phi   );
			Declare("gen_mass"  , gen_mass  );
			Declare("gen_energy", gen_energy);
			Declare("gen_charge", gen_charge);
			Declare("gen_x"     , gen_x     );
			Declare("gen_y"     , gen_y     );
			Declare("gen_z"     , gen_z     );

			Declare("gen_d0"    , gen_d0    );
			Declare("gen_d00"   , gen_d00   );
		}

		// members
		float              gen_weight;

		std::vector<int  > gen_pdgID ;
		std::vector<float> gen_pt    ;
		std::vector<float> gen_eta   ;
		std::vector<float> gen_phi   ;
		std::vector<float> gen_mass  ;
		std::vector<float> gen_energy;
		std::vector<float> gen_charge;
		std::vector<float> gen_x     ;
		std::vector<float> gen_y     ;
		std::vector<float> gen_z     ;

		std::vector<float> gen_d0    ;
		std::vector<float> gen_d00   ;

		// methods
		virtual void Reset()
		{
			gen_weight = 0;

			gen_pdgID .clear();
			gen_pt    .clear();
			gen_eta   .clear();
			gen_phi   .clear();
			gen_mass  .clear();
			gen_energy.clear();
			gen_charge.clear();
			gen_x     .clear();
			gen_y     .clear();
			gen_z     .clear();

			gen_d0    .clear();
			gen_d00   .clear();
		}

		void Fill(const reco::GenParticleCollection &gens, const GenEventInfoProduct &GEIP);
};

#endif
