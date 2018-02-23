#include "DisplacedDimuons/Tupler/interface/VertexBranches.h"

void VertexBranches::Fill(const reco::VertexCollection &vertices)
{
	Reset();
	for (const auto &vtx : vertices)
	{
		vtx_x   .push_back(vtx.x   ());
		vtx_y   .push_back(vtx.y   ());
		vtx_z   .push_back(vtx.z   ());
		vtx_chi2.push_back(vtx.chi2());
		vtx_ndof.push_back(vtx.ndof());
	}
}
