# Identified issues and risks in the protocol & Mitigations

1. Unreported repeated trials and cherry-picking
*Issue*: For each configuration, teams can repeat failed trial until they get a “good” (indefinitely) run and report only the best one (cherry-picking). Teams can hide instability or failures. Organisers cannot detect repeated attempts.
*Mitigation*: Require a “trial_start_timestamp” and “trial_end_timestamp”. Teams may retry once, but must submit both attempts if the first attempt fails due to robot crash, sensor failure, human error.

2. Hard to automate and compare handover timings
*Issue*: Measuring contact times is extremely hard to automate or detecting human–robot contact *automatically* is unreliable across labs. Vision‑based contact detection is inaccurate. Force‑based detection varies by robot. Teams will implement different heuristics. Results will not be comparable.
*Mitigation*: Timestamps will be rounded to ms (not subms measures). 

3. Robot mass estimation is the most inconsistent metric across labs.
*Issue*: Different robots have different sensors. Some robots cannot estimate mass at all. Some teams will use vision instead. Some will use force‑torque sensors. Some will use joint torque inference. Noise levels vary dramatically. Timing of measurement is unclear. A hard zero for the missing of the estimation can be unfair to low‑cost / vision‑only systems and a disincentive for otherwise strong teams to participate (teams punished for missing hardware)
*Mitigation*: Require teams to report *how* and *when* mass was estimated (e.g. method, timestamp, context). Require teams to report raw sensor values

4. Uncomparable cups across labs
*Issue*: Alternative cups because of broken purchase links or benchmark cups no available everywhere around the world.
*Mitigation*: Require teams to submit a “Cup Profile” for each cup. Organisers validate cup similarity by defining acceptable tolerances. Store cup profiles for reproducibility
