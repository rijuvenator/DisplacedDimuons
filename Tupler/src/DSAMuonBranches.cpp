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
  double dR_thr = 0.4; // very generous, should be tightened downstream
  double min_fraction_matched_segm = 0.49; // min. fraction of matched
					   // segments for storing
  DisplacedMuonFiller muf;
  for (const auto &dsamu : dsamuons) {
    if (debug)
      muf.CompareTrackParams(dsamu, verticesHandle, beamspotHandle, propagator, magfield);
    DisplacedMuon muon_cand = muf.Fill(dsamu, ttB, verticesHandle, beamspotHandle, false);
    muon_cand.idx = idx;

    // Number of DT+CSC segments
    unsigned int nsegments = 0;
    for (trackingRecHit_iterator hit = dsamu.recHitsBegin();
	 hit != dsamu.recHitsEnd(); ++hit) {
      if (!(*hit)->isValid()) continue;
      DetId id = (*hit)->geographicalId();
      if (id.det() != DetId::Muon) continue;
      if (id.subdetId() == MuonSubdetId::DT ||
	  id.subdetId() == MuonSubdetId::CSC) {
	nsegments++;
      }
    }

    // Look for a matched PAT (global or tracker) muon.
    int idx_patmu_closest_pd = -999, idx_patmu_closest_pp = -999;
    int nmatches_closest_pd  = -999, nmatches_closest_pp = -999;
    std::vector<int>   idx_patmu_matched_segm, n_matched_segm;
    std::vector<float> dR_pd_matched_segm, dR_pp_matched_segm;
    double dR_pd_min = 999., dR_pp_min = 999.;
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

        // Compute delta R between the position or direction of
        // extrapolated global/tracker tracks and the position of the
        // innermost hit of the DSA muon.
	double dR_pd, dR_pp;
	DRExtrapTrackToDSA(*tk, dsamu, propagator, magfield, dR_pd, dR_pp);
        if (debug)
          std::cout << "DSA muon #" << idx << " PAT muon #" << idx_patmu
		    << " dR(pos; dir) = " << dR_pd
		    << " dR(pos; pos) = " << dR_pp << std::endl;

        // Proximity match: take the smallest dR below the delta R
        // threshold.
        if (dR_pd < dR_thr && dR_pd < dR_pd_min) {
          dR_pd_min = dR_pd;
          idx_patmu_closest_pd = idx_patmu;
        }
        if (dR_pp < dR_thr && dR_pp < dR_pp_min) {
          dR_pp_min = dR_pp;
          idx_patmu_closest_pp = idx_patmu;
        }

        std::vector<reco::MuonChamberMatch>::const_iterator chamber;
        std::vector<reco::MuonSegmentMatch>::const_iterator segment;
        // Print the list of DT and CSC segments for a given PAT muon.
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
        unsigned int nmatches = 0;
        for (trackingRecHit_iterator hit = dsamu.recHitsBegin();
            hit != dsamu.recHitsEnd(); ++hit) {
          if (!(*hit)->isValid()) continue;
          DetId id = (*hit)->geographicalId();
          if (id.det() != DetId::Muon) continue;
          if (id.subdetId() == MuonSubdetId::DT ||
              id.subdetId() == MuonSubdetId::CSC) {
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

        if (nsegments > 0) {
	  if (float(nmatches)/nsegments > min_fraction_matched_segm) {
	    idx_patmu_matched_segm.push_back(idx_patmu);
	    n_matched_segm.push_back(nmatches);
	    dR_pd_matched_segm.push_back(dR_pd);
	    dR_pp_matched_segm.push_back(dR_pp);
	    if (debug)
	      std::cout << "DSA muon #" << idx << " shares " << nmatches << "/"
			<< nsegments << " segments with PAT muon #" << idx_patmu
			<< " dR(pos; dir) = " << dR_pd
			<< " dR(pos; pos) = " << dR_pp << std::endl;
	  }
	}

	// Number of matched segments for the closest muon
	if (idx_patmu == idx_patmu_closest_pd) {
	  nmatches_closest_pd = nmatches;
	}
	if (idx_patmu == idx_patmu_closest_pp) {
	  nmatches_closest_pp = nmatches;
	}

        idx_patmu++;
      }

      if (debug) {
	if (idx_patmu_closest_pd >= 0) {
	  std::cout << "  PAT muon closest in (pos; dir): #"
		    << idx_patmu_closest_pd << " dR = " << dR_pd_min
		    << " N(matched segments) = " << nmatches_closest_pd
		    << "/" << nsegments << std::endl;
	}
	if (idx_patmu_closest_pp >= 0) {
	  std::cout << "  PAT muon closest in (pos; pos): #"
		    << idx_patmu_closest_pp << " dR = " << dR_pp_min
		    << " N(matched segments) = " << nmatches_closest_pp
		    << "/" << nsegments << std::endl;
	}
        if (idx_patmu_matched_segm.size() > 0) {
	  std::cout << "  PAT muon(s) with matched segments:\n";
	  for (unsigned int itrk = 0; itrk < idx_patmu_matched_segm.size(); itrk++) {
	    std::cout << "    #" << idx_patmu_matched_segm[itrk]
		      << " dR(pos; dir) = " << dR_pd_matched_segm[itrk]
		      << " dR(pos; pos) = " << dR_pp_matched_segm[itrk]
		      << " N(matched segments) = " << n_matched_segm[itrk]
		      << "/" << nsegments << std::endl;
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
    dsamu_nSegments       .push_back(     nsegments              );

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

    dsamu_idx_SegmMatch      .push_back(idx_patmu_matched_segm );
    dsamu_nSegms_SegmMatch   .push_back(n_matched_segm         );
    dsamu_deltaR_pd_SegmMatch.push_back(dR_pd_matched_segm     );
    dsamu_deltaR_pp_SegmMatch.push_back(dR_pp_matched_segm     );

    dsamu_idx_pd_ProxMatch   .push_back(idx_patmu_closest_pd   );
    dsamu_nSegms_pd_ProxMatch.push_back(nmatches_closest_pd    );
    dsamu_deltaR_pd_ProxMatch.push_back(dR_pd_min              );
    dsamu_idx_pp_ProxMatch   .push_back(idx_patmu_closest_pp   );
    dsamu_nSegms_pp_ProxMatch.push_back(nmatches_closest_pp    );
    dsamu_deltaR_pp_ProxMatch.push_back(dR_pp_min              );

    if (debug) {
      std::cout << "DSA muon info:" << muon_cand;
    }

    idx++;
  }
}

// Extrapolate global/tracker muons to the point of closest approach
// to the innermost hit of DSA muons and calculate delta R between
// eta/phi of the extrapolated global/tracker tracks and eta/phi of
// the position of the innermost hit of the DSA muon.
void DSAMuonBranches::DRExtrapTrackToDSA(
    const reco::Track& track,
    const reco::Track& dsamuon,
    const edm::ESHandle<Propagator>& propagator,
    const edm::ESHandle<MagneticField>& magfield, double& dR_pd, double& dR_pp)
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

  dR_pd = deltaR(ftsPCA.momentum().eta(),       ftsPCA.momentum().phi(),
		 dsamuon.innerPosition().eta(), dsamuon.innerPosition().phi());
  dR_pp = deltaR(ftsPCA.position().eta(),       ftsPCA.position().phi(),
		 dsamuon.innerPosition().eta(), dsamuon.innerPosition().phi());
}
