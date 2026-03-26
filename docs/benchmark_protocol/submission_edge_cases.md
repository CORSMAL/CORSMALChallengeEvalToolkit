## 1. **Boundary Value Cases**

- **Workspace limits**: Robot pose exactly at min/max bounds (e.g., x=-1000, y=1000, z=0, z=2000)
- **Fill level extremes**: 0%, 100%, 0.0001%, 99.9999%
- **Time boundaries**: t_human_first_contact=0, very large timestamps (e.g., 999999999 ms)
- **Mass edge cases**: mass=0.0001g, extremely large masses (e.g., 100000g)
- **Quaternion near-boundary norms**: norm²=0.99, 1.01, 1.001, 0.999

## 2. **Invalid Data Type Cases**

- **Quaternion as strings**: "q1='one'", "q1='1.5e10'"
- **Coordinates as text**: robot_initial_pose_x="not_a_number", "Infinity", "NaN"
- **Timestamps as strings**: t_robot_first_contact_ms="abc123", "12.5.3"
- **Flags as invalid integers**: spill_observed=2, -1, 0.5, "true"
- **Negative workspace coordinates**: negative z values (-100), negative y in positive-only regions

## 3. **Logical Constraint Violations**

- **robot_mass_est_available mismatch**: available=1 but robot_mass_est_g=-1 (missing data)
- **robot_mass_est_available=0 with value**: available=0 but robot_mass_est_g=50.5 (should be -1)
- **final_mass_null_flag contradictions**: null_flag=1 but final_mass_measured_g=25.0 (should be -1)
- **final_mass_null_flag=0 with -1**: null_flag=0 but final_mass_measured_g=-1 (invalid)
- **Temporal ordering violations**: 
  - t_human_last < t_human_first (e.g., first=1000, last=500)
  - t_robot_last < t_robot_first
  - t_human_first=100, t_human_last=100 (same time, edge case)

## 4. **Timepoint Format Violations**

- **Invalid formats**: "frame123" (missing colon), "frame:abc", "range_frame:5-2" (reversed)
- **Malformed ranges**: "range_ms:100-" (missing end), "range_ms:-200" (missing start)
- **Mixed separators**: "range_frame:10_20", "frame-5", "single_ms.500"
- **Negative frame numbers**: "frame:-10", "range_frame:-5-10"
- **Missing components**: "frame:", "range_ms:", empty string ""
- **Valid but unusual**: "frame:0", "range_frame:0-0", "single_ms:0"

## 5. **Missing/Empty Data Cases**

- **Null config_id**: "" or NaN in config_id column
- **All -1 values**: Complete row filled with -1 (placeholder data)
- **Sparse valid data**: Only a few fields valid, rest -1 or NaN
- **Empty geometry timepoint with valid dimensions**: geometry_est_timepoint="unknown" but dimensions present
- **NaN propagation**: Single NaN in quaternion (q1=NaN, others valid)

## 6. **CSV Format Edge Cases**

- **Extra whitespace**: " 123.45 ", "  frame:10  " (should trim)
- **Scientific notation**: robot_initial_pose_x=1.5e-3, 2.0E+10
- **Floating point precision**: "1.0000000000000001", "0.9999999999999999"
- **Unicode/special characters**: config_id="ö_1", "中文_test"
- **Very long strings**: timepoint with excessive length: "frame:" + "0"*10000

## 7. **Quaternion-Specific Cases**

- **Unit quaternion variants**: (1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,1)
- **Conjugate pairs**: (0.7, 0.7, 0, 0) and (0.7, -0.7, 0, 0)
- **Nearly invalid norms**: norm²=0.980, 0.999, 1.001, 1.020
- **All zeros**: q1=0, q2=0, q3=0, q4=0 (norm²=0, definitely invalid)
- **Mixed precision**: q1=0.5, q2=0.5000000001, q3=0.5, q4=0.5

## 8. **Spatial/Temporal Logic Cases**

- **Delivery location just outside workspace**: x=1000.0001, y=-1000.0001
- **Robot pose inside, delivery outside**: robot at origin, delivery far beyond bounds
- **Contact time > reasonable trial duration**: t_robot_first_contact=1000000000 (unrealistic)
- **Extremely short contact duration**: first=100, last=101 (1ms contact)
- **Zero duration contacts**: first=last=500 (instant contact)

## 9. **Real-World Anomaly Cases**

- **Realistic valid submission**: All fields correct, proper quaternion, reasonable times
- **Partial failure case**: 90% fields valid, 10% with -1 placeholders
- **Data entry typos**: robot_initial_pose_x=120 (clearly out of bounds but parseable)
- **Swapped fields**: x and y coordinates swapped, time values in wrong columns
- **Unit confusion**: mass in kg instead of g (e.g., 500 instead of 0.5)
- **Vision estimate inconsistencies**: top_width > bottom_width (inverted cone)

## 10. **Performance/Scale Cases**

- **Single row file**: Just header + 1 data row
- **Large file**: 10,000+ rows to test pandas efficiency
- **All identical rows**: Every row is exact duplicate
- **Incremental row corruption**: First N rows valid, remaining all -1

## 11. **Cross-Field Validation Cases**

- **Vision estimates vs. mass**: Cup dimensions suggest 100g capacity but mass_estimate=500g
- **Robot estimate availability changes**: Some rows available=1 with estimates, others available=0 without
- **Spill flag with final mass**: spill_observed=1 but final_mass equals initial_mass (no spillage?)
- **Fill level consistency**: high fill_level but low mass_full_est_g

## 12. **Special Float Values**

- **Infinity**: robot_initial_pose_x=float('inf'), float('-inf')
- **Very small numbers**: 1e-100, 1e-308
- **Very large numbers**: 1e100, 1e308
- **Subnormal floats**: Smallest positive normalized float

These edge cases test robustness across data validation, constraint enforcement, boundary conditions, type safety, and real-world data quality issues.