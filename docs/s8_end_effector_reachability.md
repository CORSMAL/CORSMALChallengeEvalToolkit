# **s8 – End‑Effector Reachability Accuracy**  
### *Benchmark Protocol & Submission Instructions*

This task evaluates how accurately a robot can reach **six canonical target poses** in its workspace. The metric is designed to be **hardware‑agnostic**, allowing robots with different kinematics and reachability to participate fairly.

---

## **1. Overview**

Participants must command their robot to reach **six desired poses**, defined relative to the robot’s own workspace dimensions:

- **r** — horizontal reachability (meters)  
- **h** — vertical reachability (meters)

For each desired pose, the participant records the **reached end‑effector pose** (position + orientation) in the **robot base frame**.

The benchmark computes a **normalised accuracy score** based on the Euclidean distance between the desired and reached positions.

---

## **2. Desired Poses**

Each robot defines its own six target positions using its measured workspace parameters **r** and **h**.

Let:

- \( r \) = maximum horizontal reachability  
- \( h \) = maximum vertical reachability  

The six desired positions are:

| Pose | \(x\) | \(y\) | \(z\) |
|------|------|-------|-------|
| 1 | \(0\) | \(r/2\) | \(0\) |
| 2 | \(-r/2\) | \(r/2\) | \(0\) |
| 3 | \(+r/2\) | \(r/2\) | \(0\) |
| 4 | \(0\) | \(r/2\) | \(h/4\) |
| 5 | \(-r/2\) | \(r/2\) | \(h/4\) |
| 6 | \(+r/2\) | \(r/2\) | \(h/4\) |

### Orientation  
The end‑effector orientation is **fixed** and must point toward the central location \((0, r/2, 0)\).  
Participants may use any consistent convention (e.g., quaternion), but must report the reached orientation.

---

## **3. What Participants Must Do**

For each of the six desired poses:

1. Move the robot end‑effector to the desired pose.  
2. Record the **reached pose**:
   - position: \(x, y, z\) (meters)  
   - orientation: quaternion \(q_x, q_y, q_z, q_w\)  
3. Repeat for all six poses.  
4. Submit:
   - the robot’s measured **r** and **h**  
   - the six reached poses in a CSV file  

---

## **4. Scoring Method**

### **4.1 Position Error**

For each pose \(i\):

\[
e_{p,i} = \| p_i^{sub} - p_i^{des} \|
\]

### **4.2 Position Score**

A fixed threshold \(\tau_p = 0.03\,\text{m}\) (3 cm) is used.

\[
s_{p,i} = \max\left(0,\; 1 - \frac{e_{p,i}}{\tau_p}\right)
\]

- Perfect accuracy → score = 1  
- Error = 3 cm → score = 0  
- Error > 3 cm → score = 0  

### **4.3 Final Score**

\[
S = \frac{1}{6} \sum_{i=1}^{6} s_{p,i}
\]

The final score ranges from **0** (poor accuracy) to **1** (perfect accuracy).

---

## **5. Submission Format**

Participants must submit a CSV file with the following structure:

### **Header for workspace parameters**
```
r,h
```

### **Header for reached poses**
```
target_id,x,y,z,qx,qy,qz,qw
```

### **Full CSV Template**
```
r,h
<r_value>,<h_value>

target_id,x,y,z,qx,qy,qz,qw
1,<x1>,<y1>,<z1>,<qx1>,<qy1>,<qz1>,<qw1>
2,<x2>,<y2>,<z2>,<qx2>,<qy2>,<qz2>,<qw2>
3,<x3>,<y3>,<z3>,<qx3>,<qy3>,<qz3>,<qw3>
4,<x4>,<y4>,<z4>,<qx4>,<qy4>,<qz4>,<qw4>
5,<x5>,<y5>,<z5>,<qx5>,<qy5>,<qz5>,<qw5>
6,<x6>,<y6>,<z6>,<qx6>,<qy6>,<qz6>,<qw6>
```

---

## **6. Example Submission**

Assume:

- \( r = 0.80 \) m  
- \( h = 0.60 \) m  

Example reached poses:

```
r,h
0.80,0.60

target_id,x,y,z,qx,qy,qz,qw
1,0.01,0.39,0.02,0,0,0,1
2,-0.41,0.38,-0.01,0,0,0,1
3,0.39,0.41,0.01,0,0,0,1
4,-0.02,0.42,0.16,0,0,0,1
5,-0.38,0.41,0.14,0,0,0,1
6,0.42,0.39,0.17,0,0,0,1
```

---

## **7. Example Score Computation**

Using the example above:

| Pose | Error (m) | Score |
|------|-----------|--------|
| 1 | 0.024 | 0.20 |
| 2 | 0.029 | 0.03 |
| 3 | 0.017 | 0.43 |
| 4 | 0.029 | 0.03 |
| 5 | 0.024 | 0.20 |
| 6 | 0.029 | 0.03 |

Final score:

\[
S = 0.153
\]

---

## **8. Interpretation**

- **1.0** → robot consistently reaches within 0–1 cm  
- **0.5** → robot often within 1–2 cm  
- **0.1** → robot rarely within 3 cm  
- **0.0** → robot misses the tolerance window entirely  

This metric reflects **functional accuracy** for handover tasks.