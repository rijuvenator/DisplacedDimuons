#include "DisplacedDimuons/Tupler/interface/TriggerBranches.h"

bool TriggerBranches::alreadyPrinted_ = false;

bool TriggerBranches::Fill(const pat::TriggerEvent& triggerEvent,
		const edm::Handle<pat::PackedTriggerPrescales>& prescales,
		const edm::TriggerNames& triggerNames,
		const std::vector<std::string>& ddmHLTPaths)
{
  bool fired = false;
  static bool debug = false;

  Reset();

  // Dump the list of all triggers that fired
  /* 
     std::cout << "List of all triggers that fired: " << std::endl;
     for (unsigned i=0; i < triggerEvent.acceptedPaths().size(); i++)
     {
     std::string trigname(triggerEvent.acceptedPaths()[i]->name());
     std::cout << trigname << " ";
     }
     std::cout << std::endl;
  */

  // Loop over the trigger paths used in the analysis
  unsigned int idx = -1; // trigger path index for trees
  for (auto HLTPath : ddmHLTPaths)
  {
    if (!triggerEvent.path(HLTPath)) continue;
    if (triggerEvent.path(HLTPath)->wasAccept())
    {
      fired = true;
      idx++;
      unsigned path_prescale = triggerEvent.path(HLTPath)->prescale();
      trig_hlt_idx     .push_back(idx);
      trig_hlt_path    .push_back(HLTPath);
      trig_hlt_prescale.push_back(path_prescale);
      if (debug)
        std::cout << "DDM trigger path " << HLTPath << " fired;"
            << " path index = " << idx
            << " prescale = "   << path_prescale << std::endl;
      if (path_prescale != 1)
      {
        edm::LogWarning("TriggerBranches")
        << "+++ Warning: the path " << HLTPath
        << " has the prescale of " << path_prescale << " +++";
      }

      // Get trigger objects associated with this path.
      // Unfortunately this returns duplicate objects, so use it for
      // debugging only and get objects from filters instead.
      // (see https://hypernews.cern.ch/HyperNews/CMS/get/physTools/3584.html).
      if (debug)
      {
        const pat::TriggerObjectRefVector triggerObjects(triggerEvent.pathObjects(HLTPath));
        for (unsigned i = 0; i < triggerObjects.size(); i++)
        {
          // Object types are defined in
          // DataFormats/HLTReco/interface/TriggerTypeDefs.h;
          // interesting ones are TriggerL1Mu (-81) and TriggerMuon (83).
          bool l1tmu = triggerObjects[i]->hasTriggerObjectType(trigger::TriggerL1Mu);
          bool hltmu = triggerObjects[i]->hasTriggerObjectType(trigger::TriggerMuon);
          std::cout << "  object # " << i
              << ": is L1 muon? "  << (l1tmu ? "yes" : "no")
              << "; is HLT muon? " << (hltmu ? "yes" : "no")
              << "; eta = " << triggerObjects[i]->eta()
              << " phi = "  << triggerObjects[i]->phi()
              << " pT = "   << triggerObjects[i]->pt() << std::endl;
        }
      }

      // Loop over trigger filters associated with this path and extract
      // L1 and HLT objects
      const pat::TriggerFilterRefVector triggerFilters(triggerEvent.pathFilters(HLTPath));
      unsigned nfilters = triggerFilters.size();
      for (unsigned i = 0; i < nfilters; i++)
      {
        const std::string filter_type(triggerFilters[i]->type());
        const std::string filter_label(triggerFilters[i]->label());
        if (debug)
          std::cout << " filter # " << i << " label: " << filter_label
          << " type: " << filter_type << std::endl;

        // Find Level-1 objects, i.e. objects associated with the Level-1
        // muon filter
        if (filter_type == "HLTMuonL1TFilter")
        {
          // Loop over the objects associated with the filter
          const pat::TriggerObjectRefVector l1t_objects(triggerEvent.filterObjects(filter_label));
          for (unsigned i = 0; i < l1t_objects.size(); i++)
          {
            if (debug)
              std::cout << "    L1T object # " << i
              << " path index = "    << idx
              << " eta = " << l1t_objects[i]->eta()
              << " phi = " << l1t_objects[i]->phi()
              << " pT =  " << l1t_objects[i]->pt()
              << std::endl;

            // Fill Level-1 muon info
            trig_l1tmu_idx.push_back(idx);
            trig_l1tmu_px .push_back(l1t_objects[i]->px());
            trig_l1tmu_py .push_back(l1t_objects[i]->py());
            trig_l1tmu_pz .push_back(l1t_objects[i]->pz());
            trig_l1tmu_eta.push_back(l1t_objects[i]->eta());
            trig_l1tmu_phi.push_back(l1t_objects[i]->phi());
          }
        }

        // Find HLT objects, i.e. objects associated with the last filter
        // in the chain
        if (i == nfilters-1)
        {
          // Extract the label of the last filter and do some basic checks of it
          const std::string hlt_filter(triggerFilters[i]->label());
          if (hlt_filter.find("L2DoubleMu") == std::string::npos)
          {
            edm::LogWarning("TriggerBranches")
            << "+++ Warning: the last filter in the path "
            << HLTPath
            << " does not contain the L2DoubleMu string +++\n"
            << "+++ The filter is " << hlt_filter << " +++";
          }
          // Loop over the objects associated with the filter
          const pat::TriggerObjectRefVector hlt_objects(triggerEvent.filterObjects(hlt_filter));
          for (unsigned i = 0; i < hlt_objects.size(); i++)
          {
              if (debug)
                std::cout << "   HLT object # " << i
                << " path index = "   << idx
                << " eta = " << hlt_objects[i]->eta()
                << " phi = " << hlt_objects[i]->phi()
                << " pT = "  << hlt_objects[i]->pt()
                << std::endl;

              // Fill HLT info
              trig_hltmu_idx.push_back(idx);
              trig_hltmu_px .push_back(hlt_objects[i]->px());
              trig_hltmu_py .push_back(hlt_objects[i]->py());
              trig_hltmu_pz .push_back(hlt_objects[i]->pz());
              trig_hltmu_eta.push_back(hlt_objects[i]->eta());
              trig_hltmu_phi.push_back(hlt_objects[i]->phi());
          }
        }
      }

      // I am not totally sure whether the prescales stored in
      // pat::TriggerEvent include the Level-1 prescales or not, so
      // I check prescales in the pat::PackedTriggerPrescales as well.
      // See the discussion in 
      // https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD2016#Trigger
      if (prescales.failedToGet())
      {
        edm::LogWarning("TriggerBranches")
        << "+++ Warning: pat::PackedTriggerPrescales collection is not found +++";
      }
      else
      {
        pat::PackedTriggerPrescales packed_prescales(*prescales);
        // for (size_t i = 0, n = triggerNames.size(); i < n; ++i)
        // {
        //   const std::string &thispath = triggerNames.triggerName(i);
        //   std::cout << "trigname: " << thispath << std::endl;
        // }
        packed_prescales.setTriggerNames(triggerNames);
        int l1max_prescale = packed_prescales.getPrescaleForName(HLTPath);
        trig_l1t_prescale.push_back(l1max_prescale);
        if (l1max_prescale != 1)
        {
          edm::LogWarning("TriggerBranches")
            << "+++ Warning: the path " << HLTPath
            << " has the l1max prescale of " << l1max_prescale << " +++";
        }
      }
    }
  }

  return fired;
}
