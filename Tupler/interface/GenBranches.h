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
class GenBranches : public BranchCollection
{
	public:
		// constructor
		GenBranches(TreeContainer &tree, const bool DECLARE=true) :
			BranchCollection(tree, "reco::GenParticle collection", "gen info will not be filled")
		{
			Reset();
			if (DECLARE) Declarations();
		}

		// members
		static bool alreadyPrinted_;
		static bool alreadyPrinted_GEIP;

		float               gen_weight    ;

		std::vector<int   > gen_pdgID     ;
		std::vector<float > gen_p         ;
		std::vector<float > gen_pt        ;
		std::vector<float > gen_px        ;
		std::vector<float > gen_py        ;
		std::vector<float > gen_pz        ;
		std::vector<float > gen_eta       ;
		std::vector<float > gen_phi       ;
		std::vector<float > gen_mass      ;
		std::vector<float > gen_energy    ;
		std::vector<float > gen_charge    ;
		std::vector<float > gen_x         ;
		std::vector<float > gen_y         ;
		std::vector<float > gen_z         ;

    std::vector<size_t> gen_mother    ;

		std::vector<float > gen_d0        ;
		std::vector<float > gen_d00       ;

		std::vector<float > gen_pairDeltaR;

		// methods
		void Declarations()
		{
			Declare("gen_weight"    , gen_weight, "F");

			Declare("gen_pdgID"     , gen_pdgID      );
			Declare("gen_p"         , gen_p          );
			Declare("gen_pt"        , gen_pt         );
			Declare("gen_px"        , gen_px         );
			Declare("gen_py"        , gen_py         );
			Declare("gen_pz"        , gen_pz         );
			Declare("gen_eta"       , gen_eta        );
			Declare("gen_phi"       , gen_phi        );
			Declare("gen_mass"      , gen_mass       );
			Declare("gen_energy"    , gen_energy     );
			Declare("gen_charge"    , gen_charge     );
			Declare("gen_x"         , gen_x          );
			Declare("gen_y"         , gen_y          );
			Declare("gen_z"         , gen_z          );

      Declare("gen_mother"    , gen_mother     );

			Declare("gen_d0"        , gen_d0         );
			Declare("gen_d00"       , gen_d00        );

			Declare("gen_pairDeltaR", gen_pairDeltaR );
		}

		void Reset()
		{
			gen_weight = 0;

			gen_pdgID     .clear();
			gen_p         .clear();
			gen_pt        .clear();
			gen_px        .clear();
			gen_py        .clear();
			gen_pz        .clear();
			gen_eta       .clear();
			gen_phi       .clear();
			gen_mass      .clear();
			gen_energy    .clear();
			gen_charge    .clear();
			gen_x         .clear();
			gen_y         .clear();
			gen_z         .clear();

      gen_mother    .clear();

			gen_d0        .clear();
			gen_d00       .clear();

			gen_pairDeltaR.clear();
		}

		void Fill(const edm::Handle<reco::GenParticleCollection> &gensHandle,
				const edm::Handle<GenEventInfoProduct> &GEIPHandle,
        const bool isSignal);

		bool FailedToGet(const edm::Handle<reco::GenParticleCollection> &gensHandle,
				const edm::Handle<GenEventInfoProduct> &GEIPHandle);

		virtual bool alreadyPrinted() { return alreadyPrinted_ && alreadyPrinted_GEIP; }
		virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
