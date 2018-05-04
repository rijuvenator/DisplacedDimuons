#include "DisplacedDimuons/Tupler/interface/BeamspotBranches.h"

void BeamspotBranches::Fill(const reco::BeamSpot &beamspot)
{
  static bool debug = false;

  Reset();
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
