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
class TriggerBranches : BranchCollection
{
	public:
		// constructor
		TriggerBranches(TreeContainer &tree, const bool DECLARE=true) : BranchCollection(tree) { Reset(); if (DECLARE) {Declarations();} }

		// members
		bool trig_goodVtx;

		// methods
		void Declarations()
		{
			Declare("trig_goodVtx", trig_goodVtx, "B");
		}

		void Reset()
		{
			trig_goodVtx = false;
		}

		bool Fill(const pat::TriggerEvent& triggerEvent,
				const edm::Handle<pat::PackedTriggerPrescales>& prescales,
				const edm::TriggerNames& triggerNames,
				const std::vector<std::string>& ddmHLTPaths);
};

#endif
