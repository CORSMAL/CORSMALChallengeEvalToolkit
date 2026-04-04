# **s8 – End‑Effector Reachability Accuracy**  
### *Benchmark Protocol & Submission Instructions*

This measure quantifies the end-effector reaching accuracy for the robotic control. This task evaluates how accurately a robot can reach **six canonical target poses** in its workspace. The metric is designed to be **hardware‑agnostic**, allowing robots with different kinematics and reachability to participate fairly. To ensure fair and honest evaluation, participants must follow a **strict procedural protocol** with multiple repetitions, continuous execution, and video verification.

---

## **1. Overview**
 
Participants must command their robot to reach **six desired poses**, defined relative to the robot's own workspace dimensions:
 
- **r** — horizontal reachability (meters)  
- **h** — vertical reachability (meters)

<p align="center">
  <img width="500" src="https://github.com/CORSMAL/2019_RA-L_Benchmark-for-Human-to-Robot-Handovers-of-Unseen-Containers-with-Unknown-Filling/blob/master/offlineScores/s8_end-effector/illustration.png">
</p>
 
For each **sequence of six poses**, the participant:
 
1. Executes **K = 3 repetitions** of the sequence  
2. Records the **reached end‑effector pose** for each attempt  
3. Submits **position and orientation** data  
4. Provides video evidence of the execution  
 
The benchmark computes a **normalised accuracy score** based on the **median position error** (across all repetitions and poses) relative to the desired positions. Orientation is recorded but **not scored**.

---
 
## **2. Workspace Parameters and Desired Poses**
 
Each robot defines its own six target positions using its measured workspace parameters **r** and **h**.
 
Let:
 
- \( r \) = maximum horizontal reachability  
- \( h \) = maximum vertical reachability  
 
### **2.1 Standard Initial Pose**
 
Before each sequence, the robot **must start** from a standardised initial pose:

Initial pose in base frame (orientation: identity):
$p_{\text{init}} = \[ (0, 0, 0),  (0, 0, 0, 1) \]$

 
Participants must ensure their robot end‑effector can reach this pose reliably. This pose will be verified in video evidence.
 
### **2.2 The Six Target Poses**
 
The six desired positions are:
 
| Pose | \(x\) | \(y\) | \(z\) |
|------|-------|-------|-------|
| 1 | \(0\) | \(r/2\) | \(0\) |
| 2 | \(-r/2\) | \(r/2\) | \(0\) |
| 3 | \(+r/2\) | \(r/2\) | \(0\) |
| 4 | \(0\) | \(r/2\) | \(h/4\) |
| 5 | \(-r/2\) | \(r/2\) | \(h/4\) |
| 6 | \(+r/2\) | \(r/2\) | \(h/4\) |
 
### **2.3 Orientation**  
 
The end‑effector orientation **must point toward** the central location \((0, r/2, 0)\). Participants may use any consistent convention (e.g., quaternion), but must report the reached orientation in the submission.
 
---
 
## **3. Execution Protocol**
 
### **3.1 Single Continuous Run (No Resets, No Pauses)**
 
Participants must execute all **six target poses in a single uninterrupted sequence**, starting from the standard initial pose. The procedure for each repetition is:
 
1. **Start** from the standard initial pose \( (0, 0, 0) \) with orientation identity  
2. **Move to target pose 1**, record the reached pose  
3. **Return to standard initial pose**  
4. **Move to target pose 2**, record the reached pose  
5. ... continue for all six poses ...  
6. **Return to standard initial pose** after the final pose  
 
**Return to initial pose** between targets to ensure all starts are from the same reference.
 
### **3.2 Time‑Bound Execution**
 
Each individual motion (from initial pose to target pose, or target to initial pose) must complete within **T_max = 5 seconds**.
 
**Scoring penalty:** If any motion exceeds 5 seconds, the corresponding pose in that repetition receives a **score of 0**.
 
### **3.3 Multiple Repetitions**
 
Participants must execute the **complete sequence 3 times** (K = 3 repetitions). All repetitions must be:
 
- Executed on the same day before executing the 288 handover configurations.  
- Without manual recalibration between repetitions  
- Documented in separate video clips or a single continuous video  
 
### **3.4 No Manual Fine‑Tuning**
 
- No manual adjustment of robot pose between trials  
- All execution must be autonomous (i.e., driven by the robot's control system)  
- Manual teleoperation is **not permitted**  
 
---
 
## **4. Video Evidence Requirements**
 
Each submission must include **one or more video files** showing:
 
- **Robot identifier** visible on screen or in filename  
- **Sequence number** and **repetition number** (e.g., "Rep 1 of 3")  
- **Start of each sequence:** robot at the standard initial pose  
- **Target pose index** announced or displayed before motion begins  
- **Full motion:** robot moving autonomously from initial to target pose  
- **Final pose:** clearly visible and stable for ≥ 1 second before returning  
- **Timestamp overlay** or a visible clock in the frame for each motion  
 
**Video specifications:**
- Resolution: ≥ 720p  
- Frame rate: ≥ 30 fps  
- Duration: minimal editing; if edited, gaps must be marked clearly  
 
---
 
## **5. Data to Submit**
 
### **5.1 Workspace Parameters**
 
- **r** (horizontal reachability in meters)  
- **h** (vertical reachability in meters)  
 
### **5.2 Reached Poses (CSV)**
 
For each of the **K = 3 repetitions** and each of the **6 target poses**, report:
 
- **Target ID** (1–6)  
- **Position**: \(x, y, z\) in millimeters (base frame)  
- **Orientation**: quaternion \(q_x, q_y, q_z, q_w\) (base frame)  
- **Repetition number** (1, 2, or 3)  
- **Motion time** (milliseconds, from initial pose to target pose)  
 
### **5.3 Optional: Joint State Logs**
 
Participants **may** submit joint‑state logs (CSV format) containing:
 
- Timestamp  
- All joint positions (radians or degrees)  
- Computed end‑effector position (from forward kinematics)  
- Computed end‑effector orientation (from forward kinematics)  
 
These logs allow organisers to verify consistency between reported poses and forward kinematics.
 
---
 
## **6. Submission Format**
 
### **6.1 CSV Structure**
 
Participants must submit a single CSV file with the following structure:
 
``` 
run_id,repetition,target_id,x,y,z,qx,qy,qz,qw,motion_time_s
1,1,1,<x1>,<y1>,<z1>,<qx1>,<qy1>,<qz1>,<qw1>,<t1>
1,1,2,<x2>,<y2>,<z2>,<qx2>,<qy2>,<qz2>,<qw2>,<t2>
...
1,1,6,<x6>,<y6>,<z6>,<qx6>,<qy6>,<qz6>,<qw6>,<t6>
1,2,1,<x1>,<y1>,<z1>,<qx1>,<qy1>,<qz1>,<qw1>,<t1>
...
1,3,6,<x6>,<y6>,<z6>,<qx6>,<qy6>,<qz6>,<qw6>,<t6>
```
 
### **6.2 Field Definitions**
 
| Field | Type | Description |
|-------|------|-------------|
| `run_id` | int | Run identifier (not used in scoring, for traceability) |
| `repetition` | int | Repetition number (1, 2, or 3) |
| `target_id` | int | Target pose ID (1–6) |
| `x, y, z` | float | Position in base frame (millimeters) |
| `qx, qy, qz, qw` | float | Quaternion (base frame) |
| `motion_time_s` | float | Time from initial to target pose (milliseconds) |

---
 
## **7. Example Submission**
 
Assume:
 
- Team name: `Example_Arm_v1`  
- \( r = 800 \) mm  
- \( h = 600 \) mm  
- **3 repetitions**, each with 6 target poses  
 
Example CSV:
 
``` 
run_id,repetition,target_id,x,y,z,qx,qy,qz,qw,motion_time_ms
1,1,1,0.01,0.39,0.02,0,0,0,1,2300
1,1,2,-0.41,0.38,-0.01,0,0,0,1,2100
1,1,3,0.39,0.41,0.01,0,0,0,1,2000
1,1,4,-0.02,0.42,0.16,0,0,0,1,2500
1,1,5,-0.38,0.41,0.14,0,0,0,1,2200
1,1,6,0.42,0.39,0.17,0,0,0,1,2400
1,2,1,0.02,0.40,0.01,0,0,0,1,2400
1,2,2,-0.40,0.39,0.00,0,0,0,1,2200
1,2,3,0.40,0.42,0.02,0,0,0,1,2100
1,2,4,-0.01,0.41,0.17,0,0,0,1,2600
1,2,5,-0.39,0.40,0.15,0,0,0,1,2300
1,2,6,0.41,0.40,0.16,0,0,0,1,2300
1,3,1,0.00,0.40,0.03,0,0,0,1,2500
1,3,2,-0.42,0.37,-0.02,0,0,0,1,2000
1,3,3,0.38,0.42,0.00,0,0,0,1,2200
1,3,4,-0.03,0.43,0.15,0,0,0,1,2400
1,3,5,-0.37,0.42,0.13,0,0,0,1,2100
1,3,6,0.43,0.38,0.18,0,0,0,1,2200
```
 
---
 
## **8. Example Score Computation**
 
Using the example above, position errors are computed for each pose across repetitions:
 
### **Pose 1**
- Rep 1: \(e_{p,1,1} = \|(0.01, 0.39, 0.02) - (0, 0.40, 0)\| = 0.022\) m  
- Rep 2: \(e_{p,1,2} = \|(0.02, 0.40, 0.01) - (0, 0.40, 0)\| = 0.020\) m  
- Rep 3: \(e_{p,1,3} = \|(0.00, 0.40, 0.03) - (0, 0.40, 0)\| = 0.030\) m  
- Median: \(\tilde{e}_{p,1} = 0.022\) m  
- Score: \(s_{p,1} = \max(0, 1 - 0.022 / 0.03) = 0.27\)
 
### **Pose 2**
- Rep 1: \(e_{p,2,1} = \|(-410, 380, -10) - (-400, 400, 0)\| = 26\) mm  
- Rep 2: \(e_{p,2,2} = \|(-400, 390, 0) - (-400, 400, 0)\| = 10\) mm  
- Rep 3: \(e_{p,2,3} = \|(-420, 370, -20) - (-400, 400, 0)\| = 39\) mm  
- Median: \(\tilde{e}_{p,2} = 26\) m  
- Score: \(s_{p,2} = \max(0, 1 - 26 / 30) = 0.13\)
 
Continuing similarly for poses 3–6...
 
### **Final Aggregation**
 
| Pose | Median Error (mm) | Score |
|------|------------------|-------|
| 1 | 22 | 0.27 |
| 2 | 26 | 0.13 |
| 3 | 15 | 0.50 |
| 4 | 24 | 0.20 |
| 5 | 18 | 0.40 |
| 6 | 29 | 0.03 |
 
Final score:

$$
\[
S = \frac{1}{6}(0.27 + 0.13 + 0.50 + 0.20 + 0.40 + 0.03) = 0.26
\]
$$
 
---
 
## **9. Interpretation**
 
- **1.0** → robot consistently reaches within 0–1 cm across all repetitions  
- **0.75** → robot often within 0.5–1 cm  
- **0.5** → robot often within 1–2 cm  
- **0.25** → robot often within 2–3 cm  
- **0.1** → robot rarely within 3 cm  
- **0.0** → robot consistently misses the tolerance window  
 
This metric reflects **functional accuracy and consistency** for handover and manipulation tasks.
 
---
 
## **12. Submission Checklist**
 
Before submitting, verify:
 
- [ ] CSV file is properly formatted with all required fields  
- [ ] All three repetitions are included (18 rows of pose data: 3 reps × 6 poses)  
- [ ] `r` and `h` values are realistic for your robot  
- [ ] `motion_time_ms` values are ≤ 5.0 seconds  
- [ ] All quaternions are normalised (magnitude ≈ 1.0)  
- [ ] Video files show the full execution of all three repetitions  
- [ ] Video includes timestamp overlays or visible clock  
- [ ] Video clearly shows robot moving from initial pose to target and back  
- [ ] All poses in CSV correspond to those shown in video  
- [ ] Team name is consistent across submission  
- [ ] No manual fine‑tuning between repetitions is visible in video  
- [ ] Initial pose is the same for all repetitions  
 
---
 
## **13. Submission Instructions**
 
Participants must submit:
 
1. **CSV file** named `s8_submission_<TEAM_NAME>.csv` containing:
   - Workspace parameters (r, h)  
   - All 18 pose records (3 reps × 6 poses)  
 
2. **Video file(s)** named `s8_video_<TEAM_NAME>_rep1.mp4`, `s8_video_<TEAM_NAME>_rep2.mp4`, `s8_video_<TEAM_NAME>_rep3.mp4` (one per repetition, or a single continuous file)  
 
3. **Optional: Joint-state logs** (CSV format) named `s8_logs_<TEAM_NAME>.csv` for verification  

 
---
 
## **14. Frequently Asked Questions**
 
### **Q: Can we use teleoperation?**  
**A:** No. All motions must be autonomous (driven by your robot control system).
 
### **Q: What if the robot cannot reach the standard initial pose?**  
**A:** Your robot must be capable of reaching this pose. If not, contact the organisers to discuss accommodations.
 
### **Q: Can we pause between repetitions?**  
**A:** Yes, you may pause for setup or equipment checks between the three full repetitions. But within each repetition, all six poses must be executed continuously without resets.
 
### **Q: What if a motion takes 5.2 seconds?**  
**A:** That pose is marked `valid=no` and receives a score of 0 for that repetition. The median is computed over the remaining valid repetitions.
 
### **Q: How should we define r and h for a non-planar robot?**  
**A:** Use the maximum horizontal reach from the base and maximum vertical reach from the base. If your robot has complex kinematics, document your methodology in a brief readme file.
 
### **Q: Can we submit more than 3 repetitions?**  
**A:** Yes, you may submit additional repetitions. Scoring will use K=3 unless otherwise specified.
 
### **Q: Will orientation be scored in future versions?**  
**A:** Not in this version (s8 v1.0). Future versions may include orientation scoring.
 
---
 
## **Appendix: Changes from s8 v0 (Original Version)**
 
| Aspect | Original | Updated (v1.0) |
|--------|----------|-----------------|
| Repetitions | 1 | 3 (K=3) |
| Aggregation | Single trial | Median across K trials |
| Initial pose | Not specified | Standard fixed pose (0,0,0) |
| Time constraints | None | 5 seconds per motion |
| Video requirement | Optional | Mandatory with timestamps |
| Scoring | Position only | Position only (orientation recorded but not scored) |
| Continuous run | Not required | Required (no resets between poses) |
| Manual fine-tuning | Allowed | Not permitted |
 
---
 
**Version:** s8 v1.0  
**Date:** April 2025  
**Contact:** [competition organiser email] 

---

## End-effector poses (old version)
The end-effector must reach 6 desired poses. The poses are defined by the locations depicted in the figure below and the rotation of the end-effector gripper  is fixed and pointing to the central location (i.e., end-effector gripper planes perpendicular to the central point). 
