#include "DisplacedDimuons/Tupler/interface/EventBranches.h"

bool EventBranches::alreadyPrinted_ = false;

void EventBranches::Fill(const edm::Event &iEvent)
{
	static bool debug = false;

	Reset();

	evt_run   = iEvent.id().run();
	evt_lumi  = iEvent.id().luminosityBlock();
	evt_event = iEvent.id().event();
	// Likely not needed
	evt_bx    = iEvent.eventAuxiliary().bunchCrossing();

	if (debug)
		std::cout << "Event info: run / lumisection / event: " << evt_run
			<< " / " << evt_lumi << " / " << evt_event
			<< " bx = " << evt_bx << std::endl;
}
