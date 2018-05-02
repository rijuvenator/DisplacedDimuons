#ifndef TRIGGERBRANCHES_H
#define TRIGGERBRANCHES_H

// CMSSW includes
#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/PatCandidates/interface/TriggerEvent.h"
#include "DataFormats/PatCandidates/interface/PackedTriggerPrescales.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// trigger branch collection
class TriggerBranches : BranchCollection
{
	public:
		// constructor
		TriggerBranches(TreeContainer &tree, const bool DECLARE=true) : BranchCollection(tree, DECLARE) {}

		// members
		bool trig_goodVtx;

		// methods
		virtual void Declarations()
		{
			Declare("trig_goodVtx", trig_goodVtx, "B");
		}

		virtual void Reset()
		{
			trig_goodVtx = false;
		}

		bool Fill(const pat::TriggerEvent& triggerEvent,
				const edm::Handle<pat::PackedTriggerPrescales>& prescales,
				const edm::TriggerNames& triggerNames,
				const std::vector<std::string>& ddmHLTPaths);
};

#endif
