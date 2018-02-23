#include "DisplacedDimuons/Tupler/interface/TriggerBranches.h"

void TriggerBranches::Fill(const edm::TriggerResults &triggerResults, const edm::TriggerNames &triggerNames)
{
	Reset();

	//for (unsigned int i = 0; i < triggerResults.size(); ++i)
	//{
	//	std::cout << triggerNames.triggerName(i) << std::endl;
	//}

	if (triggerNames.triggerIndex("primaryVertexFilter") < triggerResults.size())
	{
		trig_goodVtx = triggerResults.accept(triggerNames.triggerIndex("primaryVertexFilter"));
	}
}
