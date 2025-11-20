"""
Data validator for quality checks and integrity verification.

Provides methods to validate data quality, check for missing values,
verify time continuity, and generate validation reports.

NOTE: This is a backward-compatible wrapper. Can optionally use
ValidateDataUseCase from Clean Architecture.
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
from datetime import timedelta
from src.database import DatabaseManager

# Optional Clean Architecture imports
try:
    from src.application.use_cases.validate_data import ValidateDataUseCase
    from src.infrastructure.database.sqlite_repository import SQLiteMarketDataRepository
    CLEAN_ARCH_AVAILABLE = True
except ImportError:
    CLEAN_ARCH_AVAILABLE = False


class DataValidator:
    """
    Validator for cryptocurrency data quality checks.
    
    Performs various validation checks on data stored in the database
    to ensure data integrity and quality.
    
    Attributes:
        db_manager (DatabaseManager): Database manager instance
    """
    
    def __init__(self, db_manager: DatabaseManager, use_clean_architecture: bool = False):
        """
        Initialize data validator.
        
        Args:
            db_manager (DatabaseManager): Database manager instance
            use_clean_architecture (bool): If True, use ValidateDataUseCase
        """
        self.db_manager = db_manager
        self.use_clean_architecture = use_clean_architecture and CLEAN_ARCH_AVAILABLE
        
        # Initialize Clean Architecture components if requested
        if self.use_clean_architecture:
            # Get database path from db_manager
            db_path = getattr(db_manager, 'db_path', 'crypto_data.db')
            repository = SQLiteMarketDataRepository(db_path)
            self.validate_use_case = ValidateDataUseCase(repository)
        else:
            self.validate_use_case = None
    
    def validate_all(self, table_name: str = 'btc_15m', limit: int = 100) -> Dict:
        """
        Run all validation checks on a table.
        
        Performs comprehensive validation including:
        - Record count check
        - Missing values detection
        - Time continuity verification
        - Indicator range validation
        
        Args:
            table_name (str): Table to validate ('btc_15m' or 'btc_1h')
            limit (int): Number of recent records to check (default: 100)
        
        Returns:
            dict: Validation results with status and detailed findings
        
        Example:
            >>> validator = DataValidator(db_manager)
            >>> results = validator.validate_all('btc_15m')
            >>> if not results['valid']:
            ...     print(f"Issues found: {results['issues']}")
        """
        # Use Clean Architecture if enabled
        if self.use_clean_architecture and self.validate_use_case:
            # Convert table name to timeframe
            timeframe = table_name.replace('btc_', '')
            
            # Use ValidateDataUseCase
            use_case_result = self.validate_use_case.execute(timeframe, limit)
            
            # Convert to legacy format for backward compatibility
            return {
                'table_name': table_name,
                'valid': use_case_result['status'] == 'PASS',
                'issues': use_case_result.get('issues', []),
                'warnings': [],
                'checks': {
                    'record_count': {
                        'count': use_case_result.get('record_count', 0),
                        'status': 'ok' if use_case_result.get('record_count', 0) > 0 else 'empty'
                    },
                    'quality_score': use_case_result.get('quality_score', 0)
                }
            }
        
        # Legacy implementation
        results = {
            'table_name': table_name,
            'valid': True,
            'issues': [],
            'warnings': [],
            'checks': {}
        }
        
        # Check 1: Record count
        count_result = self.check_record_counts(table_name)
        results['checks']['record_count'] = count_result
        if count_result['count'] == 0:
            results['issues'].append(f"No data in {table_name}")
            results['valid'] = False
        
        # If no data, skip other checks
        if count_result['count'] == 0:
            return results
        
        # Check 2: Missing values
        missing_result = self.check_missing_values(table_name, limit)
        results['checks']['missing_values'] = missing_result
        if missing_result['has_issues']:
            results['issues'].extend(missing_result['issues'])
            results['valid'] = False
        if missing_result['has_warnings']:
            results['warnings'].extend(missing_result['warnings'])
        
        # Check 3: Time continuity
        continuity_result = self.check_time_continuity(table_name, limit)
        results['checks']['time_continuity'] = continuity_result
        if continuity_result['has_issues']:
            results['issues'].extend(continuity_result['issues'])
            results['valid'] = False
        if continuity_result['has_warnings']:
            results['warnings'].extend(continuity_result['warnings'])
        
        # Check 4: Indicator ranges
        range_result = self.check_indicator_ranges(table_name, limit)
        results['checks']['indicator_ranges'] = range_result
        if range_result['has_issues']:
            results['issues'].extend(range_result['issues'])
            results['valid'] = False
        
        return results
    
    def check_record_counts(self, table_name: str) -> Dict:
        """
        Verify number of records in each table.
        
        Args:
            table_name (str): Table name to check
        
        Returns:
            dict: Record count information
        """
        try:
            count = self.db_manager.get_record_count(table_name)
            
            return {
                'table': table_name,
                'count': count,
                'status': 'ok' if count > 0 else 'empty'
            }
        except Exception as e:
            return {
                'table': table_name,
                'count': 0,
                'status': 'error',
                'error': str(e)
            }
    
    def check_missing_values(self, table_name: str, limit: int = 100) -> Dict:
        """
        Identify columns with missing data.
        
        Checks the latest N records for missing values in each column.
        
        Args:
            table_name (str): Table name to check
            limit (int): Number of recent records to check
        
        Returns:
            dict: Missing value analysis with issues and warnings
        """
        try:
            df = self.db_manager.get_latest_records(table_name, limit)
            
            if df.empty:
                return {
                    'has_issues': True,
                    'has_warnings': False,
                    'issues': ['No data to validate'],
                    'warnings': [],
                    'details': {}
                }
            
            # Count missing values per column
            missing_counts = df.isnull().sum()
            total_rows = len(df)
            
            issues = []
            warnings = []
            details = {}
            
            # Define expected missing values for indicators
            # (first N records will have NaN due to calculation periods)
            expected_nan = {
                'ema_7': 6,
                'rsi_6': 6,
                'volume_ma_20': 19
            }
            
            for column, missing_count in missing_counts.items():
                if missing_count > 0:
                    missing_pct = (missing_count / total_rows) * 100
                    details[column] = {
                        'missing_count': int(missing_count),
                        'missing_percentage': round(missing_pct, 2),
                        'total_rows': total_rows
                    }
                    
                    # Check if missing values are expected
                    expected = expected_nan.get(column, 0)
                    
                    if missing_count > expected:
                        # More missing than expected - issue
                        issues.append(
                            f"{column}: {missing_count} missing values "
                            f"({missing_pct:.1f}%), expected max {expected}"
                        )
                    elif missing_count > 0:
                        # Some missing but within expected range - warning
                        warnings.append(
                            f"{column}: {missing_count} missing values "
                            f"(expected for initial records)"
                        )
            
            return {
                'has_issues': len(issues) > 0,
                'has_warnings': len(warnings) > 0,
                'issues': issues,
                'warnings': warnings,
                'details': details
            }
            
        except Exception as e:
            return {
                'has_issues': True,
                'has_warnings': False,
                'issues': [f"Error checking missing values: {str(e)}"],
                'warnings': [],
                'details': {}
            }
    
    def check_time_continuity(self, table_name: str, limit: int = 100) -> Dict:
        """
        Verify time intervals between consecutive records.
        
        Checks if records are evenly spaced according to the timeframe.
        
        Args:
            table_name (str): Table name to check
            limit (int): Number of recent records to check
        
        Returns:
            dict: Time continuity analysis
        """
        try:
            df = self.db_manager.get_latest_records(table_name, limit)
            
            if df.empty or len(df) < 2:
                return {
                    'has_issues': False,
                    'has_warnings': True,
                    'issues': [],
                    'warnings': ['Insufficient data for time continuity check'],
                    'details': {}
                }
            
            # Determine expected interval based on table name
            expected_interval = timedelta(minutes=15) if '15m' in table_name else timedelta(hours=1)
            
            # Sort by timestamp (ascending) for proper diff calculation
            df = df.sort_index()
            
            # Calculate time differences
            time_diffs = df.index.to_series().diff().dropna()
            
            # Find gaps (intervals different from expected)
            gaps = []
            for idx, diff in time_diffs.items():
                if diff != expected_interval:
                    gaps.append({
                        'timestamp': str(idx),
                        'actual_interval': str(diff),
                        'expected_interval': str(expected_interval)
                    })
            
            issues = []
            warnings = []
            
            if len(gaps) > 0:
                gap_pct = (len(gaps) / len(time_diffs)) * 100
                
                if gap_pct > 10:  # More than 10% gaps is an issue
                    issues.append(
                        f"Found {len(gaps)} time gaps ({gap_pct:.1f}% of intervals)"
                    )
                else:  # Less than 10% is a warning
                    warnings.append(
                        f"Found {len(gaps)} time gaps ({gap_pct:.1f}% of intervals)"
                    )
            
            return {
                'has_issues': len(issues) > 0,
                'has_warnings': len(warnings) > 0,
                'issues': issues,
                'warnings': warnings,
                'details': {
                    'expected_interval': str(expected_interval),
                    'total_intervals': len(time_diffs),
                    'gaps_found': len(gaps),
                    'gap_percentage': round((len(gaps) / len(time_diffs)) * 100, 2) if len(time_diffs) > 0 else 0,
                    'sample_gaps': gaps[:5]  # Show first 5 gaps
                }
            }
            
        except Exception as e:
            return {
                'has_issues': True,
                'has_warnings': False,
                'issues': [f"Error checking time continuity: {str(e)}"],
                'warnings': [],
                'details': {}
            }
    
    def check_indicator_ranges(self, table_name: str, limit: int = 100) -> Dict:
        """
        Verify that indicators are within expected ranges.
        
        Checks:
        - RSI should be between 0 and 100
        - Prices should be positive
        - Volume should be positive
        
        Args:
            table_name (str): Table name to check
            limit (int): Number of recent records to check
        
        Returns:
            dict: Indicator range validation results
        """
        try:
            df = self.db_manager.get_latest_records(table_name, limit)
            
            if df.empty:
                return {
                    'has_issues': False,
                    'has_warnings': True,
                    'issues': [],
                    'warnings': ['No data to validate ranges'],
                    'details': {}
                }
            
            issues = []
            details = {}
            
            # Check RSI range (0-100)
            if 'rsi_6' in df.columns:
                rsi_values = df['rsi_6'].dropna()
                if len(rsi_values) > 0:
                    rsi_min = rsi_values.min()
                    rsi_max = rsi_values.max()
                    
                    details['rsi_6'] = {
                        'min': float(rsi_min),
                        'max': float(rsi_max),
                        'valid_range': [0, 100]
                    }
                    
                    if rsi_min < 0 or rsi_max > 100:
                        issues.append(
                            f"RSI out of range: [{rsi_min:.2f}, {rsi_max:.2f}], "
                            f"expected [0, 100]"
                        )
            
            # Check price columns are positive
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in df.columns:
                    values = df[col].dropna()
                    if len(values) > 0:
                        min_val = values.min()
                        
                        details[col] = {
                            'min': float(min_val),
                            'max': float(values.max())
                        }
                        
                        if min_val <= 0:
                            issues.append(f"{col}: Found non-positive values (min: {min_val})")
            
            # Check volume is positive
            if 'volume' in df.columns:
                volume_values = df['volume'].dropna()
                if len(volume_values) > 0:
                    vol_min = volume_values.min()
                    
                    details['volume'] = {
                        'min': float(vol_min),
                        'max': float(volume_values.max())
                    }
                    
                    if vol_min < 0:
                        issues.append(f"volume: Found negative values (min: {vol_min})")
            
            return {
                'has_issues': len(issues) > 0,
                'has_warnings': False,
                'issues': issues,
                'warnings': [],
                'details': details
            }
            
        except Exception as e:
            return {
                'has_issues': True,
                'has_warnings': False,
                'issues': [f"Error checking indicator ranges: {str(e)}"],
                'warnings': [],
                'details': {}
            }
    
    def generate_report(self, validation_results: Dict) -> str:
        """
        Generate a human-readable validation report.
        
        Args:
            validation_results (dict): Results from validate_all()
        
        Returns:
            str: Formatted validation report
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append(f"DATA VALIDATION REPORT: {validation_results['table_name']}")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # Overall status
        status = "✅ PASSED" if validation_results['valid'] else "❌ FAILED"
        report_lines.append(f"Overall Status: {status}")
        report_lines.append("")
        
        # Issues
        if validation_results['issues']:
            report_lines.append("🔴 ISSUES FOUND:")
            for issue in validation_results['issues']:
                report_lines.append(f"  - {issue}")
            report_lines.append("")
        
        # Warnings
        if validation_results['warnings']:
            report_lines.append("⚠️  WARNINGS:")
            for warning in validation_results['warnings']:
                report_lines.append(f"  - {warning}")
            report_lines.append("")
        
        # Detailed checks
        report_lines.append("DETAILED CHECKS:")
        report_lines.append("")
        
        for check_name, check_result in validation_results['checks'].items():
            report_lines.append(f"  {check_name.replace('_', ' ').title()}:")
            
            if check_name == 'record_count':
                report_lines.append(f"    Count: {check_result['count']}")
                report_lines.append(f"    Status: {check_result['status']}")
            
            elif 'details' in check_result and check_result['details']:
                for key, value in check_result['details'].items():
                    if isinstance(value, dict):
                        report_lines.append(f"    {key}:")
                        for k, v in value.items():
                            report_lines.append(f"      {k}: {v}")
                    else:
                        report_lines.append(f"    {key}: {value}")
            
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def __repr__(self) -> str:
        """
        String representation of DataValidator.
        
        Returns:
            str: String representation
        """
        return f"DataValidator(db_path='{self.db_manager.db_path}')"
