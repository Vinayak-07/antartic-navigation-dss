---
name: implementation-plan
description: Phase-by-phase implementation plan for Antarctic Navigation DSS enhancements
metadata:
  type: project
---

# Implementation Plan - Antarctic Navigation DSS Enhancements

## Phase 0: Complete Project Audit ✓ DONE

## Phase 1-6: Scientific Foundation ✓ MOSTLY COMPLETE
- Environment, Sea Ice, Iceberg Physics, Land Constraints - WORKING
- Trip Engine with deterministic replay - WORKING
- Route Optimization (A*) - WORKING
- Risk Model - WORKING

---

## Phase 7: Continuous Sea-Ice Visualization (PRIORITY 1)
**Goal**: Replace rectangular grid cells with smooth, continuous environmental field visualization

### Backend Changes:
- [ ] Add sea-ice grid interpolation endpoint or enhance existing grid with interpolation hints
- [ ] Optionally: Add contour/iso-line generation for smooth boundaries

### Frontend Changes:
- [ ] Replace `L.rectangle` grid cells with `L.imageOverlay` or Canvas-based rendering
- [ ] Implement bilinear/bicubic interpolation for smooth color gradients
- [ ] Add semi-transparent continuous color ramp
- [ ] Implement dynamic opacity based on concentration
- [ ] Add smooth contour lines at category boundaries
- [ ] Ensure performance with requestAnimationFrame or offscreen canvas

### Files to Modify:
- `frontend/js/map.js` - `renderSeaIce` function
- `frontend/css/map.css` - New styles for continuous sea-ice layer
- Possibly `backend/api/sea_ice.py` - Enhanced grid endpoint

---

## Phase 5: Vessel Dynamics (PRIORITY 2)
**Goal**: Smooth vessel movement with realistic physics

### Backend Changes:
- [ ] Add vessel state: heading, target_heading, speed, target_speed, acceleration, turn_rate
- [ ] Implement heading interpolation (rate-limited turn)
- [ ] Implement acceleration/deceleration curves
- [ ] Update `_advance_trip` to compute smooth vessel state
- [ ] Add vessel configuration (max_speed, max_acceleration, max_turn_rate, ice_capability)

### Frontend Changes:
- [ ] Smooth position interpolation between backend updates
- [ ] Smooth heading rotation animation
- [ ] Visual feedback for acceleration/turning
- [ ] Vessel wake/trail effect

### Files to Modify:
- `backend/simulation.py` - `_advance_trip`, `_update_trip`, vessel_state
- `backend/scientific.py` - Vessel dynamics helpers
- `frontend/js/map.js` - `updateState` vessel rendering
- `frontend/css/map.css` - Vessel animation styles

---

## Phase 10: Wind Animation (PRIORITY 3)
**Goal**: Animated wind visualization from backend fields

### Backend:
- [ ] Ensure wind vector field available at grid points
- [ ] Add wind field endpoint for animation sampling

### Frontend:
- [ ] Particle-based wind animation (moving particles along wind vectors)
- [ ] Or animated streamlines
- [ ] Speed-proportional animation rate
- [ ] Click for technical wind info

### Files to Modify:
- `frontend/js/map.js` - New wind animation layer
- `frontend/js/app.js` - Wind layer toggle
- `backend/api/environment.py` - Wind field endpoint

---

## Phase 11: Current Animation (PRIORITY 3)
**Goal**: Ocean current visualization

### Frontend:
- [ ] Moving particles along current vectors
- [ ] Distinct visual style from wind
- [ ] Helps explain iceberg movement

---

## Phase 12: Wave Visualization (PRIORITY 3)
**Goal**: Subtle moving wave patterns

### Frontend:
- [ ] Subtle animated wave texture
- [ ] Intensity proportional to wave height
- [ ] Direction affects visual movement
- [ ] Low visual priority (under routes/icebergs)

---

## Phase 13: Iceberg Animation (PRIORITY 4)
**Goal**: Smooth iceberg movement with forecast visualization

### Frontend:
- [ ] Interpolate iceberg position between backend states
- [ ] Rotate icon toward movement heading
- [ ] Smooth trajectory line updates
- [ ] Forecast markers (+6h, +12h, +24h, +48h, +72h) with smooth transitions

---

## Phase 14: Physics Visualization Mode (PRIORITY 4)
**Goal**: Enhanced technical inspection for icebergs

### Frontend:
- [ ] Expand existing iceberg popup to full physics panel
- [ ] Vector visualization (wind force, current force, Coriolis, resultant)
- [ ] Numerical values with units
- [ ] Toggle between normal/technical view

---

## Phase 19: Explain Mode (PRIORITY 5)
**Goal**: Normal vs Technical mode toggle

### Frontend:
- [ ] Global mode toggle (Normal/Technical)
- [ ] Normal: Plain language explanations
- [ ] Technical: Numerical values, equations, backend calculations
- [ ] Apply to all panels: sea-ice, iceberg, route, risk, events

---

## Phase 18: Event Story Engine (PRIORITY 5)
**Goal**: Narrative event sequence

### Backend:
- [ ] Enhance event structure with story linkage
- [ ] Add event chains (detection → approach → conflict → recalculation → response)

### Frontend:
- [ ] Story-mode event display
- [ ] Event focus with camera movement
- [ ] Technical drill-down

---

## Phase 34: Visual Storytelling Mode (PRIORITY 6)
**Goal**: Self-explanatory simulation sequence

### Frontend:
- [ ] Guided mode with automatic camera focus
- [ ] Sequential highlighting (iceberg → trajectory → risk zone → route change → vessel turn)
- [ ] Narrative captions
- [ ] Demo seed that reliably produces interesting sequence

---

## Phase 20: Voyage Playback Enhancement (PRIORITY 6)
**Goal**: Video-like playback experience

### Frontend:
- [ ] Continuous timeline scrubbing
- [ ] Event markers on timeline (click to seek)
- [ ] Reroute markers
- [ ] Speed presets (0.5x, 1x, 2x, 5x, 10x, 50x)
- [ ] Frame-accurate seek

---

## Phase 37: Deterministic Replay Optimization (PRIORITY 7)
**Goal**: Efficient state reconstruction for seeking

### Backend:
- [ ] Cache simulation snapshots at intervals
- [ ] Fast-forward from nearest snapshot instead of full replay
- [ ] Store: seed, scenario, clock, events, model params

---

## Phase 30-31: Advanced Map Layers & Visual Hierarchy (PRIORITY 7)
**Goal**: Clean layer management and visual priority

### Frontend:
- [ ] Compact layer toggle panel (not giant menu)
- [ ] Visual priority: Vessel > Actual Route > Hazards > Reference Routes > Icebergs > Sea Ice > Wind/Current > Background
- [ ] Layer opacity controls

---

## Testing & Validation
- [ ] Run full pytest suite after each phase
- [ ] Browser validation per Phase 46 scenario
- [ ] Performance profiling (no heavy calc per frame)
- [ ] Visual QA (no jitter, teleport, overlap, stale data)

---

## Implementation Order
1. **Phase 7** - Continuous Sea-Ice (biggest visual impact)
2. **Phase 5** - Vessel Dynamics (core simulation feel)
3. **Phase 10-12** - Environmental Animations (atmosphere)
4. **Phase 13** - Iceberg Animation (polish)
5. **Phase 14** - Physics Visualization (technical depth)
6. **Phase 19** - Explain Mode (accessibility)
7. **Phase 18** - Event Story (narrative)
8. **Phase 34** - Visual Storytelling (demo mode)
9. **Phase 20** - Playback Enhancement (usability)
10. **Phase 37** - Replay Optimization (performance)
11. **Phase 30-31** - Layer System (polish)

Each phase: inspect → plan → implement → test → validate → document