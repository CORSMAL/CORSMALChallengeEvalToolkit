import pandas as pd
import re
import sys
from pathlib import Path
from typing import Tuple

from datetime import datetime

from loguru import logger

class SubmissionValidator:
    def __init__(self, workspace_bounds=None):
        self.workspace_bounds = workspace_bounds or {
            'x_min': -1000, 'x_max': 1000,
            'y_min': -1000, 'y_max': 1000,
            'z_min': 0, 'z_max': 2000
        }
        self.errors = []
        self.warnings = []
        self.df = None
    
    def validate_file(self, filepath: str) -> bool:
        try:
            self.df = pd.read_csv(filepath)
            
            if self.df.empty:
                self.errors.append("CSV file is empty")
                return False
            
            for idx, row in self.df.iterrows():
                self._validate_row(row, idx + 2)  # +2 because idx starts at 0, CSV rows start at 1, +1 for header
            
            return len(self.errors) == 0
        
        except FileNotFoundError:
            self.errors.append(f"File not found: {filepath}")
            return False
        except Exception as e:
            self.errors.append(f"Failed to read file: {str(e)}")
            return False
    
    def _validate_row(self, row: pd.Series, row_num: int):
        prefix = f"Row {row_num}: "
        
        # config_id
        if pd.isna(row.get('config_id')) or row.get('config_id') == '':
            self.errors.append(f"{prefix}config_id is required")
        
        # Robot initial pose (XYZ)
        for coord in ['x', 'y', 'z']:
            key = f'robot_initial_pose_{coord}'
            val = self._parse_float(row.get(key))
            if val is None:
                self.errors.append(f"{prefix}{key} must be a float")
            elif not self._in_workspace(coord, val):
                self.errors.append(f"{prefix}{key}={val} outside workspace bounds")
        
        # Quaternion
        q_vals = []
        for i in range(1, 5):
            key = f'robot_initial_pose_q{i}'
            val = self._parse_float(row.get(key))
            if val is None:
                self.errors.append(f"{prefix}{key} must be a float")
            else:
                q_vals.append(val)
        
        if len(q_vals) == 4:
            norm_sq = sum(q ** 2 for q in q_vals)
            if not (0.99 <= norm_sq <= 1.01):
                self.warnings.append(f"{prefix}Quaternion norm² = {norm_sq:.4f}, expect ≈ 1.0")
        
        # Masses and dimensions
        self._validate_nonnegative(row, 'initial_mass_measured_g', prefix)
        self._validate_nonnegative(row, 'width_top_est_mm_vision', prefix)
        self._validate_nonnegative(row, 'width_bottom_est_mm_vision', prefix)
        self._validate_nonnegative(row, 'height_est_mm_vision', prefix)
        self._validate_nonnegative(row, 'mass_full_est_g_vision', prefix)
        
        # Timepoint validations
        self._validate_timepoint(row.get('geometry_est_timepoint'), 'geometry_est_timepoint', prefix)
        self._validate_timepoint(row.get('mass_full_est_vision_timepoint'), 'mass_full_est_vision_timepoint', prefix)
        self._validate_timepoint(row.get('fill_level_vision_timepoint'), 'fill_level_vision_timepoint', prefix)
        self._validate_timepoint(row.get('robot_mass_est_timepoint'), 'robot_mass_est_timepoint', prefix)
        
        # Fill level
        fill_level = self._parse_float(row.get('fill_level_est_percent_vision'))
        if fill_level is not None and not (0 <= fill_level <= 100):
            self.errors.append(f"{prefix}fill_level_est_percent_vision must be 0-100, got {fill_level}")
        
        # Spill flag
        spill = self._parse_int(row.get('spill_observed_during_human_maneuvering'))
        if spill is not None and spill not in [0, 1]:
            self.errors.append(f"{prefix}spill_observed_during_human_maneuvering must be 0 or 1")
        
        # Robot mass estimate
        robot_avail = self._parse_int(row.get('robot_mass_est_available'))
        robot_mass = self._parse_float(row.get('robot_mass_est_g'))
        
        if robot_avail is not None:
            if robot_avail not in [0, 1]:
                self.errors.append(f"{prefix}robot_mass_est_available must be 0 or 1")
            elif robot_avail == 0 and robot_mass != -1:
                self.errors.append(f"{prefix}robot_mass_est_available=0 requires robot_mass_est_g=-1")
            elif robot_avail == 1 and robot_mass is None:
                self.errors.append(f"{prefix}robot_mass_est_available=1 requires valid robot_mass_est_g")
        
        # Delivery location
        for coord in ['x', 'y', 'z']:
            key = f'delivery_location_est_{coord}_mm'
            val = self._parse_float(row.get(key))
            if val is not None and not self._in_workspace(coord, val):
                self.errors.append(f"{prefix}{key}={val} outside workspace bounds")
        
        # Final mass
        final_null = self._parse_int(row.get('final_mass_null_flag'))
        final_mass = self._parse_float(row.get('final_mass_measured_g'))
        
        if final_null is not None:
            if final_null not in [0, 1]:
                self.errors.append(f"{prefix}final_mass_null_flag must be 0 or 1")
            elif final_null == 1 and final_mass != -1:
                self.errors.append(f"{prefix}final_mass_null_flag=1 requires final_mass_measured_g=-1")
            elif final_null == 0 and final_mass is not None and final_mass < 0:
                self.errors.append(f"{prefix}final_mass_null_flag=0 requires final_mass_measured_g >= 0")
        
        # Temporal constraints
        t_hfc = self._parse_int(row.get('t_human_first_contact_ms'))
        t_hlc = self._parse_int(row.get('t_human_last_contact_ms'))
        t_rfc = self._parse_int(row.get('t_robot_first_contact_ms'))
        t_rlc = self._parse_int(row.get('t_robot_last_contact_ms'))
        
        if t_hfc is not None and t_hfc < 0:
            self.errors.append(f"{prefix}t_human_first_contact_ms must be >= 0")
        if t_hlc is not None and t_hfc is not None and t_hlc < t_hfc:
            self.errors.append(f"{prefix}t_human_last_contact_ms must be >= t_human_first_contact_ms")
        if t_rfc is not None and t_rfc < 0:
            self.errors.append(f"{prefix}t_robot_first_contact_ms must be >= 0")
        if t_rlc is not None and t_rfc is not None and t_rlc < t_rfc:
            self.errors.append(f"{prefix}t_robot_last_contact_ms must be >= t_robot_first_contact_ms")
    
    def _parse_float(self, val) -> float:
        if pd.isna(val) or val == '':
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None
    
    def _parse_int(self, val) -> int:
        if pd.isna(val) or val == '':
            return None
        try:
            return int(val)
        except (ValueError, TypeError):
            return None
    
    def _in_workspace(self, coord: str, val: float) -> bool:
        bounds = {
            'x': (self.workspace_bounds['x_min'], self.workspace_bounds['x_max']),
            'y': (self.workspace_bounds['y_min'], self.workspace_bounds['y_max']),
            'z': (self.workspace_bounds['z_min'], self.workspace_bounds['z_max'])
        }
        min_val, max_val = bounds[coord]
        return min_val <= val <= max_val
    
    def _validate_nonnegative(self, row: pd.Series, key: str, prefix: str):
        val = self._parse_float(row.get(key))
        if val is not None and val < 0:
            self.errors.append(f"{prefix}{key} must be >= 0, got {val}")
    
    def _validate_timepoint(self, val, key: str, prefix: str):
        if pd.isna(val) or not val or val in ['unknown', '-1']:
            return
        
        pattern = r'^(frame:\d+|range_frame:\d+-\d+|single_ms:\d+|range_ms:\d+-\d+)$'
        if not re.match(pattern, str(val)):
            self.errors.append(f"{prefix}{key}='{val}' invalid format")
    
    def print_report(self):
        if self.errors:
            print(f"\n❌ {len(self.errors)} Error(s):")
            for e in self.errors:
                print(f"   {e}")
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} Warning(s):")
            for w in self.warnings:
                print(f"   {w}")
        
        if not self.errors and not self.warnings:
            print("✓ Validation passed!")
    
    def get_summary(self) -> dict:
        """Return validation summary statistics"""
        return {
            'total_rows': len(self.df) if self.df is not None else 0,
            'errors': len(self.errors),
            'warnings': len(self.warnings),
            'is_valid': len(self.errors) == 0
        }
    
    def get_dataframe(self) -> pd.DataFrame:
        """Return the loaded dataframe for downstream processing"""
        if self.df is None:
            raise ValueError("No dataframe loaded. Call validate_file() first.")
        return self.df.copy()
    
    def get_validation_metadata(self) -> dict:
        """Return comprehensive validation metadata for scoring"""
        return {
            'dataframe': self.df.copy() if self.df is not None else None,
            'total_rows': len(self.df) if self.df is not None else 0,
            'valid_rows': self._count_valid_rows(),
            'invalid_rows': self._count_invalid_rows(),
            'errors': self.errors,
            'warnings': self.warnings,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'is_valid': len(self.errors) == 0,
            'error_by_row': self._group_errors_by_row(),
            'error_by_field': self._group_errors_by_field(),
            'warning_by_row': self._group_warnings_by_row(),
            'workspace_bounds': self.workspace_bounds
        }
    
    def _count_valid_rows(self) -> int:
        """Count rows with no errors"""
        if not self.errors:
            return len(self.df) if self.df is not None else 0
        
        error_rows = set()
        for error in self.errors:
            # Extract row number from error message "Row N: ..."
            try:
                row_num = int(error.split(':')[0].split()[-1])
                error_rows.add(row_num)
            except (ValueError, IndexError):
                pass
        
        return max(0, len(self.df) - len(error_rows)) if self.df is not None else 0
    
    def _count_invalid_rows(self) -> int:
        """Count rows with at least one error"""
        if not self.errors:
            return 0
        
        error_rows = set()
        for error in self.errors:
            try:
                row_num = int(error.split(':')[0].split()[-1])
                error_rows.add(row_num)
            except (ValueError, IndexError):
                pass
        
        return len(error_rows)
    
    def _group_errors_by_row(self) -> dict:
        """Group errors by row number"""
        errors_by_row = {}
        for error in self.errors:
            try:
                row_num = int(error.split(':')[0].split()[-1])
                if row_num not in errors_by_row:
                    errors_by_row[row_num] = []
                errors_by_row[row_num].append(error)
            except (ValueError, IndexError):
                pass
        return errors_by_row
    
    def _group_errors_by_field(self) -> dict:
        """Group errors by field name"""
        errors_by_field = {}
        field_keywords = [
            'config_id', 'robot_initial_pose', 'quaternion', 'mass', 'width', 
            'height', 'geometry', 'vision', 'fill_level', 'spill', 'robot_mass_est',
            'delivery_location', 'final_mass', 't_human', 't_robot', 'contact'
        ]
        
        for error in self.errors:
            field = 'unknown'
            for keyword in field_keywords:
                if keyword in error.lower():
                    field = keyword
                    break
            
            if field not in errors_by_field:
                errors_by_field[field] = []
            errors_by_field[field].append(error)
        
        return errors_by_field
    
    def _group_warnings_by_row(self) -> dict:
        """Group warnings by row number"""
        warnings_by_row = {}
        for warning in self.warnings:
            try:
                row_num = int(warning.split(':')[0].split()[-1])
                if row_num not in warnings_by_row:
                    warnings_by_row[row_num] = []
                warnings_by_row[row_num].append(warning)
            except (ValueError, IndexError):
                pass
        return warnings_by_row
    
# ----------------------------

class ReachabilityValidator(SubmissionValidator):
    """
    Validator for robotic reachability test CSV data.
    
    Validates:
    - Required fields and data types
    - Pose coordinates and quaternion normalization
    - Motion timing: ±1ms tolerance between computed and recorded durations
    - Temporal sequence: all 6 poses executed in single uninterrupted sequence
    - Individual motion duration: max 5 seconds per motion
    """
    def __init__(self, max_motion_time_ms=5000):
        """
        Initialize validator.
        
        Args:
            max_motion_time_ms: Maximum allowed duration for individual motion (default: 5000ms = 5s)
        """
        super().__init__()
        self.max_motion_time_ms = max_motion_time_ms
    
    def _validate_row(self, row: pd.Series, row_num: int):
        """
        Validate individual row.
        
        Args:
            row: DataFrame row to validate
            row_num: Row number for error reporting
        """
        prefix = f"Row {row_num}: "
        
        # run_id
        if pd.isna(row.get('run_id')) or row.get('run_id') == '':
            self.errors.append(f"{prefix}run_id is required")
        
        # repetition
        if pd.isna(row.get('repetition')) or row.get('repetition') == '':
            self.errors.append(f"{prefix}repetition is required")
        else:
            rep = self._parse_int(row.get('repetition'))
            if rep is not None and not (1 <= rep <= 3):
                self.warnings.append(f"{prefix}repetition {rep} outside expected range [1, 3]")
        
        # target_id
        if pd.isna(row.get('target_id')) or row.get('target_id') == '':
            self.errors.append(f"{prefix}target_id is required")
        else:
            target_id = self._parse_int(row.get('target_id'))
            if target_id is not None and not (1 <= target_id <= 6):
                self.errors.append(f"{prefix}target_id must be in range [1, 6], got {target_id}")
        
        # Robot pose (XYZ)
        for coord in ['x', 'y', 'z']:
            key = f'{coord}'
            val = self._parse_float(row.get(key))
            if val is None:
                self.errors.append(f"{prefix}{key} must be a float")
            # elif not self._in_workspace(coord, val):
            #     self.errors.append(f"{prefix}{key}={val} outside workspace bounds")
        
        # Quaternion
        q_vals = []
        for i in ['x', 'y', 'z', 'w']:
            key = f'q{i}'
            val = self._parse_float(row.get(key))
            if val is None:
                self.errors.append(f"{prefix}{key} must be a float")
            else:
                q_vals.append(val)
        
        if len(q_vals) == 4:
            norm_sq = sum(q ** 2 for q in q_vals)
            if not (0.99 <= norm_sq <= 1.01):
                self.warnings.append(f"{prefix}Quaternion norm² = {norm_sq:.4f}, expect ≈ 1.0")
        
        # Validate motion_time_ms field
        recorded_motion_time_ms = self._parse_int(row.get('motion_time_ms'))
        if recorded_motion_time_ms is None:
            self.errors.append(f"{prefix}motion_time_ms must be an integer")
        elif recorded_motion_time_ms < 0:
            self.errors.append(f"{prefix}motion_time_ms must be >= 0, got {recorded_motion_time_ms}")

        # Validate timepoints
        try:
            start_time_str = row['start_time'].replace('Z', '+00:00')
            end_time_str = row['end_time'].replace('Z', '+00:00')
            
            start_dt = datetime.fromisoformat(start_time_str)
            end_dt = datetime.fromisoformat(end_time_str)
            
            # Check that end_time > start_time
            if end_dt <= start_dt:
                self.errors.append(f"{prefix}end_time must be after start_time")
            
            computed_motion_time_ms = int((end_dt - start_dt).total_seconds() * 1000)
            
            # Check against max allowed motion time
            if computed_motion_time_ms > self.max_motion_time_ms:
                self.errors.append(f"{prefix}Motion time {computed_motion_time_ms}ms exceeds "
                                 f"maximum {self.max_motion_time_ms}ms")
            
            # Verify computed matches recorded (±1ms tolerance)
            if recorded_motion_time_ms is not None:
                motion_time_diff = abs(computed_motion_time_ms - recorded_motion_time_ms)
                if motion_time_diff > 1:
                    self.warnings.append(f"{prefix}Motion time mismatch: computed={computed_motion_time_ms}ms, "
                                       f"recorded={recorded_motion_time_ms}ms, diff={motion_time_diff}ms")
        
        except (ValueError, KeyError, AttributeError) as e:
            self.errors.append(f"{prefix}Invalid timestamp format: {e}")
        
    def _validate_temporal_sequence(self, df: pd.DataFrame):
        """
        Validate that all 6 poses are executed in a single uninterrupted sequence.
        
        For each repetition:
        - All 6 target_ids (1-6) must be present
        - Must execute in sequential order within each run_id/repetition
        - Time gaps between consecutive motions must be minimal (no interruptions)
        - Each motion must complete within max_motion_time_ms
        
        Args:
            df: DataFrame with robot reachability data
        """
        # Group by run_id and repetition
        for (run_id, repetition), group in df.groupby(['run_id', 'repetition']):
            logger.info(f"Validating sequence: run_id={run_id}, repetition={repetition}")
            
            # Check that all 6 target_ids are present
            target_ids_present = set(group['target_id'].unique())
            expected_target_ids = set(range(1, 7))
            
            if target_ids_present != expected_target_ids:
                missing = expected_target_ids - target_ids_present
                extra = target_ids_present - expected_target_ids
                if missing:
                    self.errors.append(f"run_id={run_id}, repetition={repetition}: "
                                     f"Missing target_ids: {sorted(missing)}")
                if extra:
                    self.warnings.append(f"run_id={run_id}, repetition={repetition}: "
                                       f"Unexpected target_ids: {sorted(extra)}")
            
            # Sort by target_id to check sequence
            group_sorted = group.sort_values('target_id').reset_index(drop=True)
            
            # Verify execution order (should be in ascending order of target_id)
            actual_order = group_sorted['target_id'].tolist()
            expected_order = sorted(actual_order)
            if actual_order != expected_order:
                self.warnings.append(f"run_id={run_id}, repetition={repetition}: "
                                   f"Poses not executed in sequential order. "
                                   f"Expected {expected_order}, got {actual_order}")
            
            # Check temporal continuity and gaps between poses
            for idx in range(len(group_sorted) - 1):
                current_row = group_sorted.iloc[idx]
                next_row = group_sorted.iloc[idx + 1]
                
                current_target = int(current_row['target_id'])
                next_target = int(next_row['target_id'])
                
                # Parse timestamps
                try:
                    current_end_str = current_row['end_time'].replace('Z', '+00:00')
                    next_start_str = next_row['start_time'].replace('Z', '+00:00')
                    
                    current_end_dt = datetime.fromisoformat(current_end_str)
                    next_start_dt = datetime.fromisoformat(next_start_str)
                    
                    # Check for gap between end of current and start of next
                    gap_ms = int((next_start_dt - current_end_dt).total_seconds() * 1000)
                    
                    # Allow small tolerance for timing (e.g., 100ms) but warn if large gaps
                    if gap_ms > 100:
                        self.warnings.append(f"run_id={run_id}, repetition={repetition}: "
                                           f"Large gap ({gap_ms}ms) between target {current_target} "
                                           f"(end: {current_row['end_time']}) and target {next_target} "
                                           f"(start: {next_row['start_time']})")
                    
                    # Check for negative gaps (overlapping timestamps)
                    if gap_ms < 0:
                        self.errors.append(f"run_id={run_id}, repetition={repetition}: "
                                         f"Overlapping motions detected: target {current_target} "
                                         f"ends after target {next_target} starts (gap: {gap_ms}ms)")
                
                except (ValueError, AttributeError) as e:
                    self.errors.append(f"run_id={run_id}, repetition={repetition}: "
                                     f"Timestamp parsing error: {e}")
            
            # Validate individual motion durations
            for idx, row in group_sorted.iterrows():
                target_id = int(row['target_id'])
                motion_time_ms = int(row['motion_time_ms'])
                
                if motion_time_ms > self.max_motion_time_ms:
                    self.errors.append(f"run_id={run_id}, repetition={repetition}, target_id={target_id}: "
                                     f"Motion time {motion_time_ms}ms exceeds maximum {self.max_motion_time_ms}ms")

    def validate_file(self, filepath: str) -> bool:
        try:
            self.df = pd.read_csv(filepath)
            
            if self.df.empty:
                self.errors.append("CSV file is empty")
                return False

            # Validate required columns exist
            required_columns = ['run_id', 'repetition', 'target_id', 'x', 'y', 'z',
                            'qx', 'qy', 'qz', 'qw', 'start_time', 'end_time', 'motion_time_ms']
            
            missing_columns = [col for col in required_columns if col not in self.df.columns]
            if missing_columns:
                self.errors.append(f"Missing required columns: {missing_columns}")
                logger.error(f"Missing columns: {missing_columns}")
                return False, self.errors, self.warnings
            
            # Validate individual rows
            for row_num, (idx, row) in enumerate(self.df.iterrows(), start=2):  # Start at 2 (header is row 1)
                self._validate_row(row, row_num)
            
            # Validate temporal sequence and continuity
            if not self.errors:  # Only validate sequence if rows are valid
                self._validate_temporal_sequence(self.df)
            
            return len(self.errors) == 0
        
        except FileNotFoundError:
            self.errors.append(f"File not found: {filepath}")
            return False
        except Exception as e:
            self.errors.append(f"Failed to read file: {str(e)}")
            return False
        
# ----------------------------


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python submission_validator.py <csv_file>")
        sys.exit(1)
    
    validator = SubmissionValidator()
    is_valid = validator.validate_file(sys.argv[1])
    validator.print_report()
    
    summary = validator.get_summary()
    print(f"\nSummary: {summary['total_rows']} rows, {summary['errors']} errors, {summary['warnings']} warnings")
    
    sys.exit(0 if is_valid else 1)