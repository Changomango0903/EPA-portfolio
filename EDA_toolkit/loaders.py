import pandas as pd
import json
import os
from typing import Dict, List, Union, Optional, Tuple

"""
Data loading utilities for the visualization toolkit.
Supports loading from various file formats with error handling and metadata extraction
"""

def load_csv(filepath: str, delimiter: str = ',', encoding: str = 'utf-8', infer_types: bool = True, parse_dates: Union[bool, List[str]] = True, low_memory: bool = False, **kwargs) -> Tuple[pd.DataFrame, Dict]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    file_size = os.path.getsize(filepath) / (1024 * 1024)
    file_name = os.path.basename(filepath)
    
    try:
        df = pd.read_csv(
            filepath,
            delimiter = delimiter,
            encoding = encoding,
            low_memory = low_memory,
            parse_dates = parse_dates,
            **kwargs
        )
        
        metadata = {
            'filename': file_name,
            'file_size_mb': file_size,
            'rows': len(df),
            'columns': list(df.columns),
            'column_types': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        return df, metadata
    
    except UnicodeDecodeError:
        for enc in ['latin1', 'iso-8859-1', 'cp1252']:
            if encoding != enc:
                try:
                    df = pd.read_cv(
                        filepath,
                        delimiter = delimiter,
                        encoding = enc,
                        low_memory = low_memory,
                        parse_dates = parse_dates,
                        **kwargs
                    )
                    print(f"Warning: File loaded with {enc} encoding instead of {encoding}")
                    
                    metadata = {
                        'filename': file_name,
                        'file_size_mb': file_size,
                        'rows': len(df),
                        'columns': list(df.columns),
                        'column_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                        'encoding_used': enc
                    }
                    
                    return df, metadata
                
                except:
                    continue
        raise ValueError(f"Could not decode file with any of the following encodings: {encoding}, latin1, iso-8859-1, cp1252")