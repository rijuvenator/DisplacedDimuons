#include "DisplacedDimuons/Tupler/interface/BeamspotBranches.h"

void BeamspotBranches::Fill(const reco::BeamSpot &beamspot)
{
	Reset();
	bs_x     = beamspot.x0()     ;
	bs_y     = beamspot.y0()     ;
	bs_z     = beamspot.z0()     ;
	bs_x_err = beamspot.x0Error();
	bs_y_err = beamspot.y0Error();
	bs_z_err = beamspot.z0Error();
}
