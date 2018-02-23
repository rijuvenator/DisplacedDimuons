#ifndef BRANCHCOLLECTION_H
#define BRANCHCOLLECTION_H

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"

// base class for a collection of tree branches
// derived classes define branch variables, call the Declare methods in the constructor, and implement Reset
// derived classes should also define a Fill method that sets the values of the branch variables given CMSSW tag(s)
class BranchCollection
{
	public:
		// constructor
		BranchCollection(TreeContainer &tree_) : tree(&tree_) { Reset(); }

	protected:
		// members
		TreeContainer *tree;

		// methods
		virtual void Reset() {};

		template<class Type>
		void Declare(const char* name, Type& variable, const char* type)   { tree->tree->Branch(name, &variable, (std::string(name)+"/"+type).c_str()); }
		template<class Type>
		void Declare(const char* name, std::vector<Type>& vector_variable) { tree->tree->Branch(name, &vector_variable); }
};

#endif
