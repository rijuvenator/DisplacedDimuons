#ifndef TRIGGERBRANCHES_H
#define TRIGGERBRANCHES_H

// CMSSW includes
#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/PatCandidates/interface/TriggerEvent.h"
#include "DataFormats/PatCandidates/interface/PackedTriggerPrescales.h"
#include "DataFormats/HLTReco/interface/TriggerTypeDefs.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// trigger branch collection
class TriggerBranches : public BranchCollection
{
	public:
		// constructor
		TriggerBranches(TreeContainer &tree, const bool DECLARE=true) :
			BranchCollection(tree)
		{
			Reset();
			if (DECLARE) Declarations();
		}

		// members
		static bool alreadyPrinted_;

		// Fired path info
		std::vector<unsigned int> hlt_idx;
		std::vector<std::string > hlt_path;
		std::vector<unsigned int> hlt_prescale;
		std::vector<unsigned int> l1t_prescale;

		// Level-1 muon info
		std::vector<unsigned int> l1tmu_idx;
		std::vector<float       > l1tmu_px ;
		std::vector<float       > l1tmu_py ;
		std::vector<float       > l1tmu_pz ;
		std::vector<float       > l1tmu_eta;
		std::vector<float       > l1tmu_phi;

		// HLT muon info
		std::vector<unsigned int> hltmu_idx;
		std::vector<float       > hltmu_px ;
		std::vector<float       > hltmu_py ;
		std::vector<float       > hltmu_pz ;
		std::vector<float       > hltmu_eta;
		std::vector<float       > hltmu_phi;

		// methods
		void Declarations()
		{
			Declare("hlt_idx"      , hlt_idx     );
			Declare("hlt_path"     , hlt_path    );
       		        Declare("hlt_prescale" , hlt_prescale);
       		        Declare("l1t_prescale" , l1t_prescale);

			Declare("l1tmu_idx"    , l1tmu_idx   );
			Declare("l1tmu_px"     , l1tmu_px    );
			Declare("l1tmu_py"     , l1tmu_py    );
			Declare("l1tmu_pz"     , l1tmu_pz    );
			Declare("l1tmu_eta"    , l1tmu_eta   );
			Declare("l1tmu_phi"    , l1tmu_phi   );

			Declare("hltmu_idx"    , hltmu_idx   );
			Declare("hltmu_px"     , hltmu_px    );
			Declare("hltmu_py"     , hltmu_py    );
			Declare("hltmu_pz"     , hltmu_pz    );
			Declare("hltmu_eta"    , hltmu_eta   );
			Declare("hltmu_phi"    , hltmu_phi   );
		}

		void Reset()
		{
			hlt_idx     .clear();
			hlt_path    .clear();
			hlt_prescale.clear();
			l1t_prescale.clear();

			l1tmu_idx   .clear();
			l1tmu_px    .clear();
			l1tmu_py    .clear();
			l1tmu_pz    .clear();
			l1tmu_eta   .clear();
			l1tmu_phi   .clear();

			hltmu_idx   .clear();
			hltmu_px    .clear();
			hltmu_py    .clear();
			hltmu_pz    .clear();
			hltmu_eta   .clear();
			hltmu_phi   .clear();
		}

		bool Fill(const pat::TriggerEvent& triggerEvent,
				const edm::Handle<pat::PackedTriggerPrescales>& prescales,
				const edm::TriggerNames& triggerNames,
				const std::vector<std::string>& ddmHLTPaths);

		virtual bool alreadyPrinted() { return alreadyPrinted_; }
		virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
