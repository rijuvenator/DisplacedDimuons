import FWCore.ParameterSet.Config as cms

# Do some pruning of the genParticles as detailed in the comments below.
prunedGenParticles = cms.EDProducer('GenParticlePruner',
                                    src = cms.InputTag('genParticles'),
                                    select = cms.vstring(
                                        'drop *',
                                        '++keep abs(pdgId) == 11 && status == 1',     # final-state electrons and their ancestors
                                        '++keep abs(pdgId) == 13 && status == 1',     # final-state muons and their ancestors
                                        '++keep abs(pdgId) == 15',                    # taus, their ancestors
                                        'keep++ abs(pdgId) == 15',                    #         and descendants
                                        '++keep abs(pdgId) == 12 || abs(pdgId) == 14 || abs(pdgId) == 16', # neutrinos and their ancestors
                                        "keep pdgId == 22 && status == 1 && pt > 5.", # final-state photons with pT > 5 GeV
                                        'keep (21 <= status <= 29)',                  # keep particles from the hardest subprocess
                                        'drop (30 <  status <  80)',                  #      and drop various intermediate particles
                                        'keep pdgId == 23 || abs(pdgId) == 24 || pdgId == 25 || abs(pdgId) == 6', # keep ZO, W+/-, h0, and t/tbar
                                        '+keep+ pdgId == 35 || pdgId == 6000111',     # signal: BSM Higgs and "qqbar" LL scalar with direct ancestors and descendants
                                        '+keep++ pdgId == 6000113'                    # signal: "mumu" LL scalar with all ancestors and descendants
                                        )
                                    )
