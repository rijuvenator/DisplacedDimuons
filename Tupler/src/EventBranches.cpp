#include "DisplacedDimuons/Tupler/interface/EventBranches.h"

void EventBranches::Fill(const edm::Event &iEvent)
{
	Reset();
	evt_event = iEvent.id().event()                      ;
	evt_run   = iEvent.id().run()                        ;
	evt_lumi  = iEvent.eventAuxiliary().luminosityBlock();
	evt_bx    = iEvent.eventAuxiliary().bunchCrossing()  ;
}
