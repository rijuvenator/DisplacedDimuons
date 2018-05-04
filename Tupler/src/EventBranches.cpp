#include "DisplacedDimuons/Tupler/interface/EventBranches.h"

void EventBranches::Fill(const edm::Event &iEvent, const edm::Handle<pat::METCollection>& patMET)
{
	static bool debug = false;
	static int ifois = 0;

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

	// MET
	if (patMET.failedToGet() && ifois == 0) {
		edm::LogWarning("EventBranches")
			<< "+++ Warning: pat::METs collection is not found; MET variables will not be filled +++";
		ifois = 1;
	}
	else {
		if (patMET->size() != 1) 
			throw cms::Exception("CorruptData", "More than one MET in the pat::METs collection");
		// Expect PF MET; check if this is true
		if (!patMET->begin()->isPFMET())
			edm::LogWarning("EventBranches")
				<< "+++ Warning: stored MET is not PFMET! +++";

		// Fill MET info
		evt_met     = patMET->begin()->pt();
		evt_met_phi = patMET->begin()->phi();
		const reco::GenMET *genMET = patMET->begin()->genMET();
		if (genMET != NULL) evt_gen_met = genMET->pt();

		if (debug)
			std::cout << "Event info: MET = " << evt_met
				<< " MET phi = " << evt_met_phi
				<< " gen MET = " << evt_gen_met << std::endl;
	}
}
