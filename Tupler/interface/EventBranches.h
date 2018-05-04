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

		int evt_run   ;
		int evt_lumi  ;
		int evt_event ;
		int evt_bx    ;

		// methods
		void Declarations()
		{
			Declare("evt_run"  , evt_run  , "I");
			Declare("evt_lumi" , evt_lumi , "I");
			Declare("evt_event", evt_event, "I");
			Declare("evt_bx"   , evt_bx   , "I");
		}

		void Reset()
		{
			evt_run   = -999;
			evt_lumi  = -999;
			evt_event = -999;
			evt_bx    = -999;
		}

		void Fill(const edm::Event &iEvent);

		virtual bool alreadyPrinted() { return alreadyPrinted_; }
		virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
