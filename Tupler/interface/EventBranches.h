#ifndef EVENTBRANCHES_H
#define EVENTBRANCHES_H

// CMSSW includes
#include "FWCore/Framework/interface/Event.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// event branch collection
class EventBranches : public BranchCollection
{
	public:
		// constructor
		EventBranches(TreeContainer &tree, const bool DECLARE=true) :
			BranchCollection(tree)
		{
			Reset();
			if (DECLARE) Declarations();
		}

		// members
		static bool alreadyPrinted_;

		unsigned int       evt_run   ;
		unsigned int       evt_lumi  ;
		unsigned long long evt_event ;
		int                evt_bx    ;

		// methods
		void Declarations()
		{
			Declare("evt_run"  , evt_run  , "i");
			Declare("evt_lumi" , evt_lumi , "i");
			Declare("evt_event", evt_event, "l");
			Declare("evt_bx"   , evt_bx   , "I");
		}

		void Reset()
		{
			evt_run   = -1;
			evt_lumi  = -1;
			evt_event = -1;
			evt_bx    = -1;
		}

		void Fill(const edm::Event &iEvent);

		virtual bool alreadyPrinted() { return alreadyPrinted_; }
		virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
