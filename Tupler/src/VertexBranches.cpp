#include "DisplacedDimuons/Tupler/interface/VertexBranches.h"

void VertexBranches::Fill(const reco::VertexCollection &vertices)
{
  static bool debug = false;

  Reset();

  // Total number of vertices found; useful for pile-up reweighting?
  vtx_nvtx = 0;
  for (unsigned ivtx = 0; ivtx < vertices.size(); ivtx++) {
    if (!vertices[ivtx].isFake()) vtx_nvtx++; // or maybe we should check on isValid() instead?
  }

  // Primary vertex
  reco::Vertex pv = vertices.front();

  vtx_pv_x    = pv.x();
  vtx_pv_y    = pv.y();
  vtx_pv_z    = pv.z();
  vtx_pv_dx   = pv.xError();
  vtx_pv_dy   = pv.yError();
  vtx_pv_dz   = pv.zError();
  vtx_pv_chi2 = pv.chi2();
  vtx_pv_ndof = pv.ndof();
  vtx_pv_ntrk = pv.nTracks();

  if (debug) {
    std::cout << "Vertex info: total / valid vertices = " << vertices.size()
	      << " / " << vtx_nvtx << std::endl;
    std::cout << "Primary vtx: (" << vtx_pv_x << "+/-" << vtx_pv_dx
	      << "; " << vtx_pv_y << "+/-" << vtx_pv_dy
	      << "; " << vtx_pv_z << "+/-" << vtx_pv_dz
	      << ") chi2/ndof = " << vtx_pv_chi2 << "/" << vtx_pv_ndof
	      << " ntracks = " << vtx_pv_ntrk << std::endl;
  }
}
