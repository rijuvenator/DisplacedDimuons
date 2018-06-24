// -*- C++ -*-
//
// Package:    Histograms
// Class:      EventCounter
// 
/**\class EventCounter EventCounter.cc brot/EventCounter/src/EventCounter.cc

 Description: count events with positive and negative weights and
 store the results in a histogram

**/

// system include files
#include <iostream> 

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"

// ROOT
#include "TH1.h"

//
// class declaration
//
class EventCounter : public edm::EDAnalyzer {
public:
  explicit EventCounter(const edm::ParameterSet&);
  ~EventCounter();

private:
  virtual void beginJob();
  virtual void analyze(const edm::Event&, const edm::EventSetup&);
  virtual void endJob();

  edm::EDGetTokenT<GenEventInfoProduct> GenInfoTag_;

  // histos
  std::map<std::string, TH1F*> count_;

  bool print_counts;
};

// constructors and destructor
EventCounter::EventCounter(const edm::ParameterSet& iConfig):
  GenInfoTag_(consumes<GenEventInfoProduct>(iConfig.getParameter<edm::InputTag>("genInfoTag")))
{
  print_counts = true;
  edm::Service<TFileService> fs;
  std::string name = "events";
  count_[name] = fs->make<TH1F>(name.c_str(), name.c_str(), 2,  0.5, 2.5);
  count_[name]->GetXaxis()->SetBinLabel(1, "events");
  name = "weights";
  count_[name] = fs->make<TH1F>(name.c_str(), name.c_str(), 2, -1.5, 1.5);
  count_[name]->GetXaxis()->SetBinLabel(1, "negative weights");
  count_[name]->GetXaxis()->SetBinLabel(2, "positive weights");
}


EventCounter::~EventCounter()
{
   // do anything here that needs to be done at destruction time
   // (e.g. close files, deallocate resources etc.)
}

// member functions
// ------------ method called for each event ------------
void
EventCounter::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  static bool first_call = true;
  static float first_weight = -999.;

  // count events
  count_["events"]->Fill(1);

  // get generator weights
  edm::Handle<GenEventInfoProduct> genInfoProduct;
  iEvent.getByToken(GenInfoTag_, genInfoProduct);

  if (genInfoProduct.isValid()) {
    float weight = (*genInfoProduct).weight();

    if (first_call) {
      first_weight = fabs(weight);
      first_call   = false;
    }
    else {
      // Expect all weights to have the same abs value; check that
      // this is indeed the case
      if (fabs(fabs(weight)-first_weight) > 1e-3) {
	edm::LogWarning("EventCounter")
	  << "+++ Warning: MC weights do not have the same absolute value \n"
	  << "  first weight stored: " << first_weight
	  << "  current weight: "      << fabs(weight) << " +++";
      }
    }
    // store weights in the histogram
    if (weight < 0.) {
      count_["weights"]->Fill(-1);
    }
    else {
      count_["weights"]->Fill(1);
    }
  }
  else {
    edm::LogWarning("EventCounter")
      << "+++ Warning: GenEventInfoProduct collection is not found +++";
  }
}

// ------------ method called once each job just before starting event loop ------------
void 
EventCounter::beginJob()
{
}

// ------------ method called once each job just after ending the event loop ------------
void 
EventCounter::endJob() 
{
  if (print_counts) {
    int total    = count_["events"]->GetBinContent(1);
    int negative = count_["weights"]->GetBinContent(1);
    int positive = count_["weights"]->GetBinContent(2);
    std::cout << "EventCounter: Total number of events = " << total
	      << " Nevts with positive weight = " << positive
    	      << " Nevts with negative weight = " << negative
    	      << " negative/total = " << float(negative)/total << std::endl;
  }
}

// define this as a plug-in
DEFINE_FWK_MODULE(EventCounter);
