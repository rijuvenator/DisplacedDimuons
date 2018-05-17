#include "DisplacedDimuons/Tupler/interface/GenBranches.h"

bool GenBranches::alreadyPrinted_ = false;
bool GenBranches::alreadyPrinted_GEIP = false;

namespace PDGID
{
  const int MUON   = 13;
  const int LLXP   = 6000111;
  const int LLX    = 6000113;
  const int HIGGS  = 35;
  const int PROTON = 2212;
}

bool GenBranches::FailedToGet(const edm::Handle<reco::GenParticleCollection> &gensHandle,
    const edm::Handle<GenEventInfoProduct> &GEIPHandle)
{
  if (gensHandle.failedToGet())
  {
    if (!alreadyPrinted_)
    {
      edm::LogWarning("SimpleNTupler")
        << "+++ Warning: "
        << primaryHandleName
        << " is not found; "
        << primaryExtraText
        << "+++";
      alreadyPrinted_ = true;
    }
    return true;
  }
  if (GEIPHandle.failedToGet())
  {
    if (!alreadyPrinted_GEIP)
    {
      edm::LogWarning("SimpleNTupler")
        << "+++ Warning: GenEventInfoProduct is not found +++";
      alreadyPrinted_GEIP = true;
    }
    return true;
  }
  return false;
}

void GenBranches::Fill(const edm::Handle<reco::GenParticleCollection> &gensHandle,
    const edm::Handle<GenEventInfoProduct> &GEIPHandle,
    const bool isSignal,
    const std::string finalState)
{
  Reset();

  // Check if failed to get
  if (FailedToGet(gensHandle, GEIPHandle)) return;
  const reco::GenParticleCollection &gens = *gensHandle;
  const GenEventInfoProduct &GEIP = *GEIPHandle;

  // set gen weight
  gen_weight = GEIP.weight();

  // find appropriate gen particles and fill branches
  if      (isSignal && finalState == "4Mu"  ) Fill4Mu  (gens);
  else if (isSignal && finalState == "2Mu2J") Fill2Mu2J(gens);
  else                                        FillOther(gens);

}

// fill gen branches for P -> H -> XX -> 4Mu
void GenBranches::Fill4Mu(const reco::GenParticleCollection &gens)
{
  // muAll is for all muons
  std::vector<const reco::GenParticle*> muAll;
  const reco::GenParticle *mu11 = nullptr;
  const reco::GenParticle *mu12 = nullptr;
  const reco::GenParticle *mu21 = nullptr;
  const reco::GenParticle *mu22 = nullptr;
  const reco::Candidate   *X1   = nullptr;
  const reco::Candidate   *X2   = nullptr;
  const reco::Candidate   *H    = nullptr;
  const reco::Candidate   *P    = nullptr;

  // loop over the gen particles and look for muons
  for (const auto &gen : gens)
  {
    if (abs(gen.pdgId()) == PDGID::MUON and gen.status() == 1)
    {
      muAll.push_back(&gen);

      // p will be a dummy changeable pointer to a particle
      // first look for the mother X, then based on the pointer addresses,
      // set the appropriate X and mu pointers. then look for Higgs, then proton
      const reco::Candidate *p = &gen;
      while (p->pdgId() != PDGID::LLX && p->numberOfMothers() != 0) { p = p->mother(); }
      if (p->pdgId() == PDGID::LLX)
      {
        if      (X1 == nullptr) { X1 = p; mu11 = &gen; } // X1 == 0                                  --> found mu11
        else if (p  == X1     ) {         mu12 = &gen; } // X1 != 0 && p == X1                       --> found mu12
        else if (X2 == nullptr) { X2 = p; mu21 = &gen; } // X1 != 0 && p != X1 && X2 == 0            --> found mu21
        else if (p  == X2     ) {         mu22 = &gen; } // X2 != 0 && p != X1 && X2 != 0 && p == X2 --> found mu22

        // once mu22 is found, no need to keep looping over the gen particles
        // X1, X2, mu11, mu12, mu21, and mu22 should be set
        if (mu22 != nullptr) break;
      }
    }
  }
  // make sure X1 and X2 are non-null
  if (X1 == nullptr || X2 == nullptr)
  {
    edm::LogWarning("NTupler::GenBranches") << "+++ Warning: X1 or X2 is null. Filling nothing. +++";
    return;
  }
  // set H and P starting from X1
  const reco::Candidate *p = X1;
  p = p->mother();
  H = p;
  while (abs(p->pdgId()) != PDGID::PROTON) { p = p->mother(); }
  P = p;

  // make sure all pointers are non-null
  if (mu11 == nullptr || mu12 == nullptr ||
      mu21 == nullptr || mu22 == nullptr ||
      X1   == nullptr || X2   == nullptr ||
      H    == nullptr || P    == nullptr)
  {
    edm::LogWarning("NTupler::GenBranches") << "+++ Warning: At least one pointer is null. Filling nothing. +++";
    return;
  }

  // fill the branches: mu11, mu12, mu21, mu22, X1, X2, H, and P
  // and any additional muons
  std::vector<const reco::Candidate*> particles = {mu11, mu12, mu21, mu22, X1, X2, H, P};
  if (muAll.size() > 4)
  {
    for (const auto &mu : muAll)
    {
      if (std::find(particles.begin(), particles.end(), mu) == particles.end())
      {
        particles.push_back(mu);
      }
    }
  }
  for (const auto &p : particles)
  {
    gen_pdgID .push_back(p->pdgId ());
    gen_pt    .push_back(p->pt    ());
    gen_eta   .push_back(p->eta   ());
    gen_phi   .push_back(p->phi   ());
    gen_mass  .push_back(p->mass  ());
    gen_energy.push_back(p->energy());
    gen_charge.push_back(p->charge());
    gen_x     .push_back(p->vx    ());
    gen_y     .push_back(p->vy    ());
    gen_z     .push_back(p->vz    ());
  }

  // fill d0
  std::vector<const reco::GenParticle*> muons = {mu11, mu12, mu21, mu22};
  int count = 0;
  for (const auto &mu : muons)
  {
    TVector3 disp;
    if (count < 2)
             disp = TVector3(mu->vx() - X1->vx(), mu->vy() - X1->vy(), 0.);
    else
             disp = TVector3(mu->vx() - X1->vx(), mu->vy() - X2->vy(), 0.);
    TVector3 zero           (mu->vx()           , mu->vy()           , 0.);
    TVector3 p3z            (mu->px()           , mu->py()           , 0.);

    float d0  = disp.Cross(p3z).Mag()/p3z.Mag();
    float d00 = zero.Cross(p3z).Mag()/p3z.Mag();

    gen_d0 .push_back(d0 );
    gen_d00.push_back(d00);

    count++;
  }

  // fill pair delta R
  float dR1 = TVector3(mu11->px(), mu11->py(), mu11->pz()).DeltaR(TVector3(mu12->px(), mu12->py(), mu12->pz()));
  float dR2 = TVector3(mu21->px(), mu21->py(), mu21->pz()).DeltaR(TVector3(mu22->px(), mu22->py(), mu22->pz()));
  gen_pairDeltaR.push_back(dR1);
  gen_pairDeltaR.push_back(dR1);
  gen_pairDeltaR.push_back(dR2);
  gen_pairDeltaR.push_back(dR2);
}

// fill gen branches for P -> H -> XX -> 2Mu 2Jet
void GenBranches::Fill2Mu2J(const reco::GenParticleCollection &gens)
{
  const reco::GenParticle *mu1  = nullptr;
  const reco::GenParticle *mu2  = nullptr;
  const reco::Candidate   *j1   = nullptr;
  const reco::Candidate   *j2   = nullptr;
  const reco::Candidate   *X    = nullptr;
  const reco::Candidate   *XP   = nullptr;
  const reco::Candidate   *H    = nullptr;
  const reco::Candidate   *P    = nullptr;
  for (const auto &gen : gens)
  {
    // look for X -> mu1 mu2
    if (abs(gen.pdgId()) == PDGID::MUON and gen.status() == 1)
    {
      // p will be a dummy changeable pointer to a particle
      // first look for the mother X, then based on the pointer addresses,
      // set the appropriate X and mu pointers. then look for Higgs, then proton
      const reco::Candidate *p = &gen;
      while (p->pdgId() != PDGID::LLX && p->numberOfMothers() != 0) { p = p->mother(); }
      if (p->pdgId() == PDGID::LLX)
      {
        if      (X   == nullptr) { X = p;      }
        if      (mu1 == nullptr) { mu1 = &gen; }
        else if (mu2 == nullptr) { mu2 = &gen; }
      }
    }
    // look for X' -> j1 j2
    if (gen.pdgId() == PDGID::LLXP)
    {
      XP = &gen;
      if (!(XP->numberOfDaughters() == 2))
      {
        edm::LogWarning("NTupler::GenBranches") << "+++ Warning: X' does not have 2 daughters. Filling nothing. +++";
        return;
      }
      j1 = XP->daughter(0);
      j2 = XP->daughter(1);
    }
    // if both mu2 and X' are set, no need to keep looping over gen particles
    if (mu2 != nullptr && XP != nullptr) break;
  }
  // make sure X and X' are non-null
  if (X == nullptr || XP == nullptr)
  {
    edm::LogWarning("NTupler::GenBranches") << "+++ Warning: X or X' is null. Filling nothing. +++";
    return;
  }
  // set H and P starting from X
  const reco::Candidate *p = X;
  p = p->mother();
  H = p;
  while (abs(p->pdgId()) != PDGID::PROTON) { p = p->mother(); }
  P = p;

  // make sure all pointers are non-null
  if (mu1 == nullptr || j1  == nullptr ||
      mu2 == nullptr || j2  == nullptr ||
      X   == nullptr || XP  == nullptr ||
      H   == nullptr || P   == nullptr)
  {
    edm::LogWarning("NTupler::GenBranches") << "+++ Warning: At least one pointer is null. Filling nothing. +++";
//    if (mu1 == nullptr) edm::LogWarning("NTupler::GenBranches") << "+++ mu1 is null +++";
//    if (mu2 == nullptr) edm::LogWarning("NTupler::GenBranches") << "+++ mu2 is null +++";
//    if ( j1 == nullptr) edm::LogWarning("NTupler::GenBranches") << "+++  j1 is null +++";
//    if ( j2 == nullptr) edm::LogWarning("NTupler::GenBranches") << "+++  j2 is null +++";
//    if (  X == nullptr) edm::LogWarning("NTupler::GenBranches") << "+++   X is null +++";
//    if ( XP == nullptr) edm::LogWarning("NTupler::GenBranches") << "+++  XP is null +++";
//    if (  H == nullptr) edm::LogWarning("NTupler::GenBranches") << "+++   H is null +++";
//    if (  P == nullptr) edm::LogWarning("NTupler::GenBranches") << "+++   P is null +++";
    return;
  }

  // fill the branches: mu1, mu2, j1, j2, X, X', H, and P
  std::vector<const reco::Candidate*> particles = {mu1, mu2, j1, j2, X, XP, H, P};
  for (const auto &p : particles)
  {
    gen_pdgID .push_back(p->pdgId ());
    gen_pt    .push_back(p->pt    ());
    gen_eta   .push_back(p->eta   ());
    gen_phi   .push_back(p->phi   ());
    gen_mass  .push_back(p->mass  ());
    gen_energy.push_back(p->energy());
    gen_charge.push_back(p->charge());
    gen_x     .push_back(p->vx    ());
    gen_y     .push_back(p->vy    ());
    gen_z     .push_back(p->vz    ());
  }
}

// fill gen branches for some other MC type, simply filling everything
void GenBranches::FillOther(const reco::GenParticleCollection &gens)
{
  for (const auto &p : gens)
  {
    gen_pdgID .push_back(p.pdgId ());
    gen_pt    .push_back(p.pt    ());
    gen_eta   .push_back(p.eta   ());
    gen_phi   .push_back(p.phi   ());
    gen_mass  .push_back(p.mass  ());
    gen_energy.push_back(p.energy());
    gen_charge.push_back(p.charge());
    gen_x     .push_back(p.vx    ());
    gen_y     .push_back(p.vy    ());
    gen_z     .push_back(p.vz    ());

    size_t mIndex = -1;
    if (p.numberOfMothers() > 0) { mIndex = p.motherRef(0).key(); }

    gen_mother.push_back(mIndex    );
  }
}
