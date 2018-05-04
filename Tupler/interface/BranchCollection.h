#ifndef BRANCHCOLLECTION_H
#define BRANCHCOLLECTION_H

// CMSSW includes
#include "FWCore/Framework/interface/MakerMacros.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"

// base class for a collection of tree branches
// derived classes
//    - define branch variables
//    - define a Declarations method with Declare methods for the tree
//    - define a Reset method with default values
//    - define a Fill method that sets the values of the branch variables given e.g. CMSSW tag(s)
class BranchCollection
{
	public:
		// constructor
		BranchCollection(TreeContainer &tree_, std::string primaryHandleName_="", std::string primaryExtraText_="") :
			tree(&tree_),
			primaryHandleName(primaryHandleName_),
			primaryExtraText(primaryExtraText_)
		{}

	protected:
		// members
		TreeContainer *tree;

		const std::string primaryHandleName;
		const std::string primaryExtraText;

		// methods
		template<class Type>
		void Declare(const char* name, Type& variable, const char* type)   { tree->tree->Branch(name, &variable, (std::string(name)+"/"+type).c_str()); }
		template<class Type>
		void Declare(const char* name, std::vector<Type>& vector_variable) { tree->tree->Branch(name, &vector_variable); }

		template<class Type>
		bool FailedToGet(const Type &Handle)
		{
			if (Handle.failedToGet())
			{
				if (!alreadyPrinted())
				{
					edm::LogWarning("SimpleNTupler")
						<< "+++ Warning: "
						<< primaryHandleName
						<< " is not found; "
						<< primaryExtraText
						<< "+++";
					setAlreadyPrinted();
				}
				return true;
			}
			return false;
		}

	public:
		virtual bool alreadyPrinted() { return false; }
		virtual void setAlreadyPrinted() {};
		virtual bool isValid() { return !alreadyPrinted(); }
};

#endif
