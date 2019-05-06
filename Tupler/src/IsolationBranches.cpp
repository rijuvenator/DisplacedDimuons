#include "DisplacedDimuons/Tupler/interface/IsolationBranches.h"

bool IsolationBranches::alreadyPrinted_ = false;

/*
void IsolationBranches::Fill(const edm::Handle<reco::BeamSpot> &beamspotHandle)
{
	static bool debug = false;
	Reset();

	// Check if failed to get
	if (FailedToGet(beamspotHandle)) return;
	const reco::BeamSpot &beamspot = *beamspotHandle;

	bs_x  = beamspot.x0()     ;
	bs_y  = beamspot.y0()     ;
	bs_z  = beamspot.z0()     ;
	bs_dx = beamspot.x0Error();
	bs_dy = beamspot.y0Error();
	bs_dz = beamspot.z0Error();

	if (debug) 
		std::cout << "Beam spot position: (" << bs_x << "+/-" << bs_dx
			<< "; " << bs_y << "+/-" << bs_dy
			<< "; " << bs_z << "+/-" << bs_dz << std::endl;
}
*/
