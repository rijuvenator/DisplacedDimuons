#ifndef EVENTBRANCHES_H
#define EVENTBRANCHES_H

// CMSSW includes
#include "FWCore/Framework/interface/Event.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// event branch collection
class EventBranches : BranchCollection
{
	public:
		// constructor
		EventBranches(TreeContainer &tree) : BranchCollection(tree)
		{
			Declare("evt_event", evt_event, "I");
			Declare("evt_run"  , evt_run  , "I");
			Declare("evt_lumi" , evt_lumi , "I");
			Declare("evt_bx"   , evt_bx   , "I");
		}

		// members
		int evt_event ;
		int evt_run   ;
		int evt_lumi  ;
		int evt_bx    ;

		// methods
		virtual void Reset()
		{
			evt_event = -1;
			evt_run   = -1;
			evt_lumi  = -1;
			evt_bx    = -1;
		}

		void Fill(const edm::Event &iEvent);
};

#endif
