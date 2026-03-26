# Metadata for the submission form

| **Column** | **Type** | **Units** | **Allowed values** | **Description** | **Validation** |
| --- | --- | --- | --- | --- | --- |
| **config_id** | string or integer | n/a | organiser IDs | Organiser defined configuration identifier | Must match organiser config list |
| **robot_initial_pose_x** | float | mm | real | Robot base/world X coordinate at trial start | Within workspace bounds |
| **robot_initial_pose_y** | float | mm | real | Robot base/world Y coordinate at trial start | Within workspace bounds |
| **robot_initial_pose_z** | float | mm | real | Robot base/world Z coordinate at trial start | Within workspace bounds |
| **robot_initial_pose_q1** | float | unitless | real | Quaternion component q1 | Quaternion norm ≈ 1 within tolerance |
| **robot_initial_pose_q2** | float | unitless | real | Quaternion component q2 | See quaternion validation |
| **robot_initial_pose_q3** | float | unitless | real | Quaternion component q3 | See quaternion validation |
| **robot_initial_pose_q4** | float | unitless | real | Quaternion component q4 | See quaternion validation |
| **initial_mass_measured_g** | float | g | ≥ 0 | Measured mass of cup plus contents before handover | Nonnegative; measured with a digital scale |
| **width_top_est_mm_vision** | float | mm | ≥ 0 | Vision estimate of cup top diameter | Nonnegative |
| **width_bottom_est_mm_vision** | float | mm | ≥ 0 | Vision estimate of cup bottom diameter | Nonnegative |
| **height_est_mm_vision** | float | mm | ≥ 0 | Vision estimate of cup height | Nonnegative |
| **geometry_est_timepoint** | string | frames or ms | ``frame:N`` ``range_frame:N0-N1`` ``single_ms:T`` ``range_ms:T0-T1`` | Timepoint or window used for geometry estimate | Must follow allowed format and be within video/trial |
| **mass_full_est_g_vision** | float | g | ≥ 0 | Vision estimate of full mass cup plus contents | Nonnegative |
| **mass_full_est_vision_timepoint** | string | frames or ms | same formats as geometry_est_timepoint | Timepoint or window used for mass estimate | Same validation as geometry_est_timepoint |
| **fill_level_est_percent_vision** | float | percent | 0–100 | Vision estimate of fill level percentage | 0 ≤ value ≤ 100 |
| **fill_level_vision_timepoint** | string | frames or ms | same formats as geometry_est_timepoint | Timepoint or window used for fill level estimate | Same validation as geometry_est_timepoint |
| **spill_observed_during_human_maneuvering** | integer | n/a | ``0`` or ``1`` | Flag indicating observed spill during human manoeuvre | Must be 0 or 1 |
| **robot_mass_est_available** | integer | n/a | ``0`` or ``1`` | Whether robot produced an onboard mass estimate | If 0 then robot_mass_est_g must be ``-1`` |
| **robot_mass_est_g** | float | g | ≥ 0 or ``-1`` | Robot estimated mass if available | If robot_mass_est_available=0 must be ``-1`` |
| **robot_mass_est_timepoint** | string | frames or ms | same formats as geometry_est_timepoint | Timepoint or window used for robot mass estimate | Same validation as geometry_est_timepoint |
| **delivery_location_est_x_mm** | float | mm | real | Team estimated X of cup base centre after placement | Must be within workspace bounds |
| **delivery_location_est_y_mm** | float | mm | real | Team estimated Y of cup base centre after placement | Must be within workspace bounds |
| **delivery_location_est_z_mm** | float | mm | real | Team estimated Z of cup base centre after placement | Must be within workspace bounds |
| **final_mass_null_flag** | integer | n/a | ``0`` or ``1`` | ``1`` if no final mass reading due to drop or failure | If 1 then final_mass_measured_g must be ``-1`` |
| **final_mass_measured_g** | float | g | ≥ 0 or ``-1`` | Scale reading after execution or ``-1`` if null | If final_mass_null_flag=0 must be ≥ 0 |
| **t_human_first_contact_ms** | integer | ms | ≥ 0 | Timestamp of human first contact relative to trial start | 0 ≤ value ≤ trial duration |
| **t_human_last_contact_ms** | integer | ms | ≥ 0 | Timestamp of human last contact | Must satisfy logical ordering |
| **t_robot_first_contact_ms** | integer | ms | ≥ 0 | Timestamp of robot first contact | 0 ≤ value ≤ trial duration |
| **t_robot_last_contact_ms** | integer | ms | ≥ 0 | Timestamp of robot last contact | Must satisfy t_robot_first_contact_ms ≤ t_robot_last_contact_ms |

Note: Teams must declare quaternion ordering in the team metadata JSON.