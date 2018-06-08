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
		std::vector<unsigned int> trig_hlt_idx;
		std::vector<std::string > trig_hlt_path;
		std::vector<unsigned int> trig_hlt_prescale;
		std::vector<unsigned int> trig_l1t_prescale;

		// Level-1 muon info
		std::vector<unsigned int> trig_l1tmu_idx;
		std::vector<float       > trig_l1tmu_px ;
		std::vector<float       > trig_l1tmu_py ;
		std::vector<float       > trig_l1tmu_pz ;
		std::vector<float       > trig_l1tmu_eta;
		std::vector<float       > trig_l1tmu_phi;

		// HLT muon info
		std::vector<unsigned int> trig_hltmu_idx;
		std::vector<float       > trig_hltmu_px ;
		std::vector<float       > trig_hltmu_py ;
		std::vector<float       > trig_hltmu_pz ;
		std::vector<float       > trig_hltmu_eta;
		std::vector<float       > trig_hltmu_phi;

		// methods
		void Declarations()
		{
      Declare("trig_hlt_idx"      , trig_hlt_idx     );
      Declare("trig_hlt_path"     , trig_hlt_path    );
      Declare("trig_hlt_prescale" , trig_hlt_prescale);
      Declare("trig_l1t_prescale" , trig_l1t_prescale);

      Declare("trig_l1tmu_idx"    , trig_l1tmu_idx   );
      Declare("trig_l1tmu_px"     , trig_l1tmu_px    );
      Declare("trig_l1tmu_py"     , trig_l1tmu_py    );
      Declare("trig_l1tmu_pz"     , trig_l1tmu_pz    );
      Declare("trig_l1tmu_eta"    , trig_l1tmu_eta   );
      Declare("trig_l1tmu_phi"    , trig_l1tmu_phi   );

      Declare("trig_hltmu_idx"    , trig_hltmu_idx   );
      Declare("trig_hltmu_px"     , trig_hltmu_px    );
      Declare("trig_hltmu_py"     , trig_hltmu_py    );
      Declare("trig_hltmu_pz"     , trig_hltmu_pz    );
      Declare("trig_hltmu_eta"    , trig_hltmu_eta   );
      Declare("trig_hltmu_phi"    , trig_hltmu_phi   );
		}

		void Reset()
		{
			trig_hlt_idx     .clear();
			trig_hlt_path    .clear();
			trig_hlt_prescale.clear();
			trig_l1t_prescale.clear();

			trig_l1tmu_idx   .clear();
			trig_l1tmu_px    .clear();
			trig_l1tmu_py    .clear();
			trig_l1tmu_pz    .clear();
			trig_l1tmu_eta   .clear();
			trig_l1tmu_phi   .clear();

			trig_hltmu_idx   .clear();
			trig_hltmu_px    .clear();
			trig_hltmu_py    .clear();
			trig_hltmu_pz    .clear();
			trig_hltmu_eta   .clear();
			trig_hltmu_phi   .clear();
		}

		bool Fill(const pat::TriggerEvent& triggerEvent,
				const edm::Handle<pat::PackedTriggerPrescales>& prescales,
				const edm::TriggerNames& triggerNames,
				const std::vector<std::string>& ddmHLTPaths);

		virtual bool alreadyPrinted() { return alreadyPrinted_; }
		virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
