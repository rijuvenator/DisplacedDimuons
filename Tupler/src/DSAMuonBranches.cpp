#include "DisplacedDimuons/Tupler/interface/DSAMuonBranches.h"

#include "DataFormats/Math/interface/deltaR.h"

bool DSAMuonBranches::alreadyPrinted_ = false;

void DSAMuonBranches::Fill(const edm::Handle<reco::TrackCollection> &dsamuonsHandle,
    const edm::ESHandle<TransientTrackBuilder>& ttB,
    const edm::Handle<reco::VertexCollection> &verticesHandle,
    const edm::Handle<reco::BeamSpot> &beamspotHandle,
    const edm::ESHandle<Propagator>& propagator,
    const edm::ESHandle<MagneticField>& magfield,
    const edm::Handle<pat::MuonCollection> &patmuonsHandle)
{
  static bool debug = false;
  Reset();

  // Check if failed to get
  // already checked if vertices are valid
  if (FailedToGet(dsamuonsHandle)) return;
  const reco::TrackCollection &dsamuons = *dsamuonsHandle;

  // Also fetch PAT muons for matching with DSA muons
  if (FailedToGet(patmuonsHandle)) return;
  const pat::MuonCollection &patmuons = *patmuonsHandle;

  unsigned int idx = 0;
  double dR_thr = 0.4; // very generous, should probably be tightened downstream
  DisplacedMuonFiller muf;
  for (const auto &dsamu : dsamuons) {
    if (debug)
      muf.CompareTrackParams(dsamu, verticesHandle, beamspotHandle, propagator, magfield);
    DisplacedMuon muon_cand = muf.Fill(dsamu, ttB, verticesHandle, beamspotHandle, false);
    muon_cand.idx = idx;

    // Look for a matched PAT (global or tracker) muon.
    int idx_patmu_matched_prox = -999, nmatches_prox = -999;
    std::vector<int> idx_patmu_matched_segm;
    double dR_min = 999.;
    // Do not waste time trying to match DSA muons with no valid hits.
    if (muon_cand.n_MuonHits > 0) {
      // Print the list of DT and CSC segments belonging to a given
      // DSA muon.
      if (debug) {
        for (trackingRecHit_iterator hit = dsamu.recHitsBegin();
            hit != dsamu.recHitsEnd(); ++hit) {
          if (!(*hit)->isValid()) continue;
          DetId id = (*hit)->geographicalId();
          if (id.det() == DetId::Muon) {
	    int muonSubdetId = id.subdetId();
            if (muonSubdetId == MuonSubdetId::DT ||
		muonSubdetId == MuonSubdetId::CSC) {
	      int station;
	      if (muonSubdetId == MuonSubdetId::DT) {
		DTChamberId segId(id.rawId());
		station = segId.station();
	      }
	      else if (muonSubdetId == MuonSubdetId::CSC) {
		CSCDetId segId(id.rawId());
		station = segId.station();
	      }

              std::cout << "DSA muon segment: subdet "
                << ((id.subdetId() == MuonSubdetId::DT) ? "DT" : "CSC")
                << " station = " << station
                << " id = "    << id.rawId()
                << " x = "     << (*hit)->localPosition().x()
                << " y = "     << (*hit)->localPosition().y()
                << std::endl;
            }
	  }
        }
      }

      int idx_patmu = 0;
      for (const auto &patmu : patmuons) {
        // Only use global and arbitrated tracker muons
        if (!patmu.isGlobalMuon() &&
            !(patmu.isTrackerMuon() && patmu.muonID("TrackerMuonArbitrated")))
          continue;
        const reco::Track* tk = patmu.tunePMuonBestTrack().get();
	//const reco::Track* tk = patmu.combinedMuon().get();
	//const reco::Track* tk = patmu.innerTrack().get();

        // Compute delta R between the extrapolated global/tracker
        // tracks and the position of the innermost hit of the DSA
        // muon.
        double dR = DRExtrapTrackToDSA(*tk, dsamu, propagator, magfield);
        if (debug)
          std::cout << "DSA muon #" << idx << " PAT muon #" << idx_patmu
            << " dR = " << dR << std::endl;

        // Proximity match: take the smallest dR below the delta R
        // threshold.
        if (dR < dR_thr && dR < dR_min) {
          dR_min = dR;
          idx_patmu_matched_prox = idx_patmu;
        }

        std::vector<reco::MuonChamberMatch>::const_iterator chamber;
        std::vector<reco::MuonSegmentMatch>::const_iterator segment;
        // Print the list of DT and CSC segments matched to a given
        // PAT muon.
        if (debug) {
          for (chamber = patmu.matches().begin();
              chamber != patmu.matches().end(); ++chamber) {
            if (chamber->id.det() == DetId::Muon) {
	      int muonSubdetId = chamber->id.subdetId();
              if (muonSubdetId == MuonSubdetId::DT ||
                  muonSubdetId == MuonSubdetId::CSC) {

		int station;
		if (muonSubdetId == MuonSubdetId::DT) {
		  DTChamberId segId(chamber->id.rawId());
		  station = segId.station();
		}
		else if (muonSubdetId == MuonSubdetId::CSC) {
		  CSCDetId segId(chamber->id.rawId());
		  station = segId.station();
		}

                for (segment = chamber->segmentMatches.begin();
		     segment != chamber->segmentMatches.end(); ++segment) {
                  // select the only segment that belongs to track and is
                  // the best in station by dR
                  // if (!(segment->isMask(reco::MuonSegmentMatch::BestInStationByDR) &&
                  //	  segment->isMask(reco::MuonSegmentMatch::BelongsToTrackByDR)))
                  //  continue;
                  std::cout << "PAT muon segment: subdet "
			    << ((chamber->id.subdetId() == MuonSubdetId::DT) ? "DT" : "CSC")
			    << " station = " << station
			    << " id = " << chamber->id.rawId()
			    << " x = " << segment->x
			    << " y = " << segment->y << std::endl;
                }
              }
	    }
          }
        }

        // Segment match: consider global/tracker and DSA muons
        // matched if the segments used to build the DSA muon are the
        // same as or a subset of segments of the global/tracker muon.
        unsigned int nsegments = 0, nmatches = 0;
        for (trackingRecHit_iterator hit = dsamu.recHitsBegin();
            hit != dsamu.recHitsEnd(); ++hit) {
          if (!(*hit)->isValid()) continue;
          DetId id = (*hit)->geographicalId();
          if (id.det() != DetId::Muon) continue;
          if (id.subdetId() == MuonSubdetId::DT ||
              id.subdetId() == MuonSubdetId::CSC) {
            nsegments++;
            for (chamber = patmu.matches().begin();
                chamber != patmu.matches().end(); ++chamber) {
              if (chamber->id.rawId() != id.rawId()) continue;
              for (segment = chamber->segmentMatches.begin();
                  segment != chamber->segmentMatches.end(); ++segment) {
                if (fabs(segment->x - (*hit)->localPosition().x()) < 1e-6 &&
                    fabs(segment->y - (*hit)->localPosition().y()) < 1e-6) {
                  if (debug)
                    std::cout << "matched segment found!!! subdet "
                      << ((chamber->id.subdetId() == MuonSubdetId::DT) ? "DT" : "CSC")
                      << " id = " << chamber->id.rawId()
                      << " x = " << segment->x
                      << " y = " << segment->y << std::endl;
                  nmatches++;
                  break;
                }
              }
            }
          }
        }
        if (nsegments > 0 && nsegments == nmatches) {
          idx_patmu_matched_segm.push_back(idx_patmu);
          if (debug)
            std::cout << "DSA-PAT segment match found! DSA muon #" << idx
              << " PAT muon #" << idx_patmu
              << " N(matched segments) = " << nmatches << std::endl;
        }

	// Number of matched segments for the closest muon
	if (idx_patmu == idx_patmu_matched_prox) {
	  nmatches_prox = nmatches;
	}

        idx_patmu++;
      }

      if (debug) {
        if (idx_patmu_matched_prox >= 0)
          std::cout << "DSA-PAT proximity match found! DSA muon #" << idx
		    << " PAT muon #" << idx_patmu_matched_prox
		    << " dR = " << dR_min << " N(matched segments) = " << nmatches_prox
		    << std::endl;

        if (idx_patmu_matched_segm.size() > 0 || idx_patmu_matched_prox >= 0) {
          bool matches_agree = false;
          for (unsigned int itrk = 0; itrk < idx_patmu_matched_segm.size(); itrk++) {
            if (idx_patmu_matched_segm[itrk] == idx_patmu_matched_prox) {
              std::cout << " Proximity and segment matches agree" << std::endl;
              matches_agree = true;
              break;
            }
          }
          if (!matches_agree) {
            std::cout << " Proximity and segment matches do not agree\n"
              << "   DSA muon #" << idx
              << " proximity-matched PAT muon # " << idx_patmu_matched_prox
              << " segment-matched PAT muon #";
            if (idx_patmu_matched_segm.size() > 0) {
              for (unsigned int itrk = 0; itrk < idx_patmu_matched_segm.size(); itrk++) {
                std::cout << " " << idx_patmu_matched_segm[itrk];
              }
            }
            else {
              std::cout << " -999";
            }
            std::cout << std::endl;
          }
        }
      }
    }

    // Fill the tree
    dsamu_idx             .push_back(     muon_cand.idx          );
    dsamu_px              .push_back(     muon_cand.px           );
    dsamu_py              .push_back(     muon_cand.py           );
    dsamu_pz              .push_back(     muon_cand.pz           );
    dsamu_ptError         .push_back(     muon_cand.ptError      );
    dsamu_eta             .push_back(     muon_cand.eta          );
    dsamu_phi             .push_back(     muon_cand.phi          );
    dsamu_charge          .push_back(     muon_cand.charge       );
    dsamu_chi2            .push_back(     muon_cand.chi2         );
    dsamu_ndof            .push_back(     muon_cand.ndof         );

    dsamu_x               .push_back(     muon_cand.x            );
    dsamu_y               .push_back(     muon_cand.y            );
    dsamu_z               .push_back(     muon_cand.z            );
    dsamu_x_fhit          .push_back(     muon_cand.x_fhit       );
    dsamu_y_fhit          .push_back(     muon_cand.y_fhit       );
    dsamu_z_fhit          .push_back(     muon_cand.z_fhit       );

    dsamu_nMuonHits       .push_back(     muon_cand.n_MuonHits   );
    dsamu_nDTHits         .push_back(     muon_cand.n_DTHits     );
    dsamu_nCSCHits        .push_back(     muon_cand.n_CSCHits    );
    dsamu_nDTStations     .push_back(     muon_cand.n_DTStations );
    dsamu_nCSCStations    .push_back(     muon_cand.n_CSCStations);

    dsamu_d0_pv           .push_back(fabs(muon_cand.d0_pv       ));
    dsamu_d0_bs           .push_back(fabs(muon_cand.d0_bs       ));
    dsamu_d0_pv_lin       .push_back(fabs(muon_cand.d0_pv_lin   ));
    dsamu_d0_bs_lin       .push_back(fabs(muon_cand.d0_bs_lin   ));
    dsamu_d0sig_pv        .push_back(     muon_cand.d0sig_pv     );
    dsamu_d0sig_bs        .push_back(     muon_cand.d0sig_bs     );
    dsamu_d0sig_pv_lin    .push_back(     muon_cand.d0sig_pv_lin );
    dsamu_d0sig_bs_lin    .push_back(     muon_cand.d0sig_bs_lin );

    dsamu_dz_pv           .push_back(fabs(muon_cand.dz_pv       ));
    dsamu_dz_bs           .push_back(fabs(muon_cand.dz_bs       ));
    dsamu_dz_pv_lin       .push_back(fabs(muon_cand.dz_pv_lin   ));
    dsamu_dz_bs_lin       .push_back(fabs(muon_cand.dz_bs_lin   ));
    dsamu_dzsig_pv        .push_back(     muon_cand.dzsig_pv     );
    dsamu_dzsig_bs        .push_back(     muon_cand.dzsig_bs     );
    dsamu_dzsig_pv_lin    .push_back(     muon_cand.dzsig_pv_lin );
    dsamu_dzsig_bs_lin    .push_back(     muon_cand.dzsig_bs_lin );

    dsamu_idx_ProxMatch   .push_back(     idx_patmu_matched_prox );
    dsamu_deltaR_ProxMatch.push_back(     dR_min                 );
    dsamu_nSegms_ProxMatch.push_back(     nmatches_prox          );
    dsamu_idx_SegMatch    .push_back(     idx_patmu_matched_segm );

    if (debug) {
      std::cout << "DSA muon info:" << muon_cand;
      std::cout << "  proximity-matched PAT muon: " << idx_patmu_matched_prox
		<< " (dR = " << dR_min << " N(matched segments) = " << nmatches_prox
		<< "); segment-matched PAT muon:";
      if (idx_patmu_matched_segm.size() > 0) {
        for (unsigned int itrk = 0; itrk < idx_patmu_matched_segm.size(); itrk++) {
          std::cout << " " << idx_patmu_matched_segm[itrk];
        }
      }
      else {
        std::cout << " -999";
      }
      std::cout << std::endl;
    }

    idx++;
  }
}

// Extrapolate global/tracker muons to the point of closest approach
// to the innermost hit of DSA muons and calculate delta R between
// eta/phi of the extrapolated global/tracker tracks and eta/phi of
// the position of the innermost hit of the DSA muon.
double DSAMuonBranches::DRExtrapTrackToDSA(
    const reco::Track& track,
    const reco::Track& dsamuon,
    const edm::ESHandle<Propagator>& propagator,
    const edm::ESHandle<MagneticField>& magfield)
{
  // Create a free trajectory state of the track to be extrapolated
  // (global or tracker muon).
  FreeTrajectoryState fts(GlobalPoint(track.vx(), track.vy(), track.vz()),
      GlobalVector(track.px(), track.py(), track.pz()),
      track.charge(), magfield.product());

  // Propagate the state to the point of closest approach to the
  // inndermost hit of the DSA muon.
  GlobalPoint fhpos(dsamuon.innerPosition().x(),
      dsamuon.innerPosition().y(),
      dsamuon.innerPosition().z());
  FreeTrajectoryState ftsPCA(propagator->propagate(fts, fhpos));

  /*
  // For debugging purposes
  std::cout << "extrap mom eta: " << ftsPCA.momentum().eta()
  << " phi: "           << ftsPCA.momentum().phi() << std::endl;
  std::cout << "extrap pos eta: " << ftsPCA.position().eta()
  << " phi: "           << ftsPCA.position().phi() << std::endl;
  std::cout << "mom eta: " << dsamuon.innerMomentum().eta()
  << " phi: "    << dsamuon.innerMomentum().phi() << std::endl;
  std::cout << "pos eta: " << dsamuon.innerPosition().eta()
  << " phi: "    << dsamuon.innerPosition().phi() << std::endl;
  */

  double dR = deltaR(ftsPCA.momentum().eta(),
      ftsPCA.momentum().phi(),
      dsamuon.innerPosition().eta(),
      dsamuon.innerPosition().phi());

  return dR;
}
