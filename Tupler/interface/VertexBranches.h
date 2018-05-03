#ifndef VERTEXBRANCHES_H
#define VERTEXBRANCHES_H

// CMSSW includes
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// vertex branch collection
class VertexBranches : BranchCollection
{
	public:
		// constructor
		VertexBranches(TreeContainer &tree, const bool DECLARE=true) : BranchCollection(tree) { Reset(); if (DECLARE) {Declarations();} }

		// members
		std::vector<float> vtx_x   ;
		std::vector<float> vtx_y   ;
		std::vector<float> vtx_z   ;
		std::vector<float> vtx_chi2;
		std::vector<float> vtx_ndof;
		
		// methods
		void Declarations()
		{
			Declare("vtx_x"   , vtx_x   );
			Declare("vtx_y"   , vtx_y   );
			Declare("vtx_z"   , vtx_z   );
			Declare("vtx_chi2", vtx_chi2);
			Declare("vtx_ndof", vtx_ndof);
		}

		void Reset()
		{
			vtx_x   .clear();
			vtx_y   .clear();
			vtx_z   .clear();
			vtx_chi2.clear();
			vtx_ndof.clear();
		}

		void Fill(const reco::VertexCollection &vertices);
};

#endif
