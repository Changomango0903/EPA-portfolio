import pandas as pd
import numpy as np
from typing import List, Dict, Union, Optional, Callable, Tuple
import re

"""
Data Cleaning utilities for EDA toolkit. Functions for handling missing values, outliers, duplicates, and other type conversions.
"""

def detect_missing(df: pd.DataFrame, include_zeros: bool = False, include_empty_strings: bool = True) -> Dict[str, Dict]:
    temp_df = df.copy()
    
    initial_missing = temp_df.isna().sum()
    missing_percent = (initial_missing / len(temp_df) * 100).round(2)
    
    zeros_count = {}
    empty_strings_count = {}
    
    if include_zeros:
        for col in temp_df.select_dtypes(include = np.number).columns:
            zeros_count[col] = (temp_df[col] == 0).sum()
    if include_empty_strings:
        for col in temp_df.select_dtypes(include = ['object', 'string']).columns:
            empty_strings_count[col] = temp_df[col].str.strip().eq('').sum()
    
    single_value_cols = []
    for col in temp_df.columns:
        if temp_df[col].nunique() == 1:
            single_value_cols.append(col)
    
    missing_patterns = {}
    missing_counts = temp_df.isna().sum(axis = 1)
    for i in range(1, min(5, df.shape[1]) + 1):
        missing_patterns[f'rows_with_{i}_missing'] = (missing_counts == i).sum()
        
    missing_patterns['rows_with_any_missing'] = (missing_counts > 0).sum()
    missing_patterns['complete_rows'] = (missing_counts == 0).sum()
    
    return {
        'missing_count': initial_missing.to_dict(),
        'missing_percent': missing_percent.to_dict(),
        'zeros_count': zeros_count if include_zeros else None,
        'empty_strings_count': empty_strings_count if include_empty_strings else None,
        'single_value_columns': single_value_cols,
        'missing_patterns': missing_patterns,
        'total_cells': df.size,
        'total_missing_cells': initial_missing.sum(),
        'overall_missing_percent': (initial_missing.sum() / df.size * 100).round(2)
    }