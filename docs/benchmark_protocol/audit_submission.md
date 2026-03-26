### High‑level verdict
Given **4 subjects × 72 configs = 288 runs** and ~4 hours total effort, your instincts are correct: **don’t require a trial id**, expect natural variability, and treat identical or near‑identical numbers across many configurations as a strong signal of fabrication rather than proof. The protocol should therefore be **lightweight for honest teams** but include **automated statistical checks + a small, targeted audit workflow** that makes cheating risky and expensive.

---

### 1 — Principles to apply (short)
- **Minimise team burden.** Keep the CSV compact and avoid per‑trial administrative fields that add friction.  
- **Require verifiable anchors.** Videos + video manifest (SHA256) and a small set of frame indices or hashes tie reported numbers to evidence.  
- **Detect patterns, don’t assume guilt.** Use automated anomaly detection to flag suspicious submissions for manual audit and request raw logs/frames.  
- **Allow natural variability.** Design checks to expect per‑subject and per‑config variance; flag statistical anomalies, not single identical values.

---

### 2 — What to *not* ask for
- **No trial id**: correct decision — trial ids add overhead and are unnecessary if video manifests and config IDs are present.  
- **No per‑config verbose provenance** in the CSV (methods, long text). Keep provenance in the single team JSON.

---

### 3 — Automated checks to run on every submission (fast, deterministic)
Run these checks first; they should reject only clearly invalid rows (missing fields, sentinel values) and otherwise produce flags.

1. **Completeness**  
   - No `-1` or `unknown` in required CSV fields.  
2. **Unit & range checks**  
   - Mass ≥ 0 (or `-1` when null flag set), fill 0–100, confidences (if present) 0–1, positions inside workspace.  
3. **Contact ordering**  
   - `t_human_first ≤ t_human_last`, `t_robot_first ≤ t_robot_last`.  
4. **Flag exact repeats**  
   - Count identical values per field across all 288 rows (exact equality). If **> 5%** of rows identical for a numeric field (e.g., same width_top_est_mm across >14 configs), flag.  
5. **Flag zero variance**  
   - If variance of a numeric field across all configs ≤ machine epsilon (or effectively zero), flag.  
6. **Target equality check**  
   - If delivery_location_est equals organiser target exactly for **> 10%** of configs, flag.  
7. **Plausibility checks**  
   - Delivery location reachable from robot_initial_pose and typical gripper reach (quick kinematic bound).  
8. **Temporal plausibility**  
   - If estimation timepoints (frames/ms) are outside video length or inconsistent with contact times, flag.

---

### 4 — Statistical anomaly detectors (score and prioritize flags)
Use these to rank submissions for audit rather than to immediately penalize.

- **Repeated‑value score**: for each numeric column compute fraction of rows equal to the modal value. Score = max fraction across columns. If score > 0.10 → medium risk; > 0.25 → high risk.  
- **Entropy test**: compute Shannon entropy per column (discretize numeric values to small bins). Very low entropy → suspicious.  
- **Runs test / autocorrelation**: check whether identical values cluster by subject or are uniformly repeated (clustering by subject is plausible; uniform repetition across subjects is suspicious).  
- **Z‑score outlier detection**: per config, compute z for each numeric field relative to team distribution; many z>3 across fields → suspicious.  
- **Cross‑field consistency**: e.g., mass_full_est_g_vision should correlate with fill_level_est_percent and geometry; compute correlation and flag gross inconsistencies (e.g., fill 90% but mass estimate near empty).

Use these detectors to produce a **risk score** (0–100) per team; set thresholds for manual audit.

---

### 5 — Audit workflow (manual + evidence requests)
1. **Tiering**  
   - **Tier 0**: passes automated checks → accept.  
   - **Tier 1**: low/medium risk (some flags) → request clarifications and a small set of raw artifacts.  
   - **Tier 2**: high risk → request full raw logs + selected frames + explanation; hold scoring until resolved.  
2. **Artifacts to request** (only for flagged configs)  
   - video file(s) for those configs (or confirm video SHA256), extracted frames at reported contact frames, robot joint logs and gripper pose around release, scale logs for final mass.  
3. **Manual checks**  
   - Verify frame hashes vs reported frame indices; inspect frames for obvious mismatch.  
   - Recompute delivery location from gripper pose if robot logs provided.  
4. **Resolution**  
   - If evidence matches reported numbers → clear.  
   - If evidence contradicts reports → downgrade/penalize that config (e.g., mark as invalid) and escalate for repeat offences.  
5. **Appeal & remediation**  
   - Allow teams to explain anomalies (e.g., subject behavior, spill). If explanation plausible and evidence supports it, accept with note.

---

### 6 — Practical thresholds and policies (suggested, adjustable)
- **Exact‑repeat threshold**: flag if identical value appears in **> 5%** of configs for any primary numeric field; high‑risk if > 25%.  
- **Target‑match threshold**: flag if delivery_location_est equals organiser target exactly in **> 10%** of configs.  
- **Zero‑variance**: immediate flag if variance = 0 across all 288 configs for any numeric field.  
- **Audit sampling**: for medium risk, request **5%** of configs (random, stratified by subject). For high risk, request **20%** or full set of flagged configs.  
- **Penalty policy**: define clear outcomes in advance (e.g., single flagged config → request resubmission; repeated or proven fabrication → disqualification). Publish policy to deter cheating.

---

### Short operational recommendations to implement now
1. **Keep CSV as you designed** (no trial id).  
2. **Require video manifest (SHA256) and per‑config video filenames** in team JSON.  
3. **Require frame indices or frame‑based timepoints** for contact events in CSV (ms allowed only if fps in JSON).  
4. **Run the automated checks and compute a risk score**; use thresholds above to triage.  
5. **Perform small random audits** (5–10% of configs) on all teams to keep the cost of cheating high.  
6. **Publish the validation rules and audit policy** so teams know what will be checked and the consequences.

---

If you want, I can now produce **(A)** a compact Python pseudocode validator that implements the automated checks and risk scoring, or **(B)** a one‑page audit policy text you can publish with the benchmark. Which would you like?