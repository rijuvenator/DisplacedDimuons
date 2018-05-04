#ifndef EVENTBRANCHES_H
#define EVENTBRANCHES_H

// CMSSW includes
#include "FWCore/Framework/interface/Event.h"
#include "DataFormats/PatCandidates/interface/MET.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// event branch collection
class EventBranches : BranchCollection
{
	public:
		// constructor
		EventBranches(TreeContainer &tree, const bool DECLARE=true) : BranchCollection(tree) { Reset(); if (DECLARE) {Declarations();} }

		// members
		int evt_run   ;
		int evt_lumi  ;
		int evt_event ;
		int evt_bx    ;

		// MET-related quantities
		float evt_met     ;
		float evt_met_phi ;
		float evt_gen_met ;

		// methods
		void Declarations()
		{
			Declare("evt_run"  , evt_run  , "I");
			Declare("evt_lumi" , evt_lumi , "I");
			Declare("evt_event", evt_event, "I");
			Declare("evt_bx"   , evt_bx   , "I");

			Declare("evt_met"    , evt_met    , "F");
			Declare("evt_met_phi", evt_met_phi, "F");
			Declare("evt_gen_met", evt_gen_met, "F");
		}

		void Reset()
		{
			evt_run   = -999;
			evt_lumi  = -999;
			evt_event = -999;
			evt_bx    = -999;

			evt_met     = -999.;
			evt_met_phi = -999.;
			evt_gen_met = -999.;
		}

		void Fill(const edm::Event &iEvent, const edm::Handle<pat::METCollection>& patMET);
};

#endif
