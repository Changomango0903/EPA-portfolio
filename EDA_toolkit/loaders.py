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

def load_excel(filepath: str, sheet_name: Optional[Union[str, int, List[Union[str, int]]]] = 0, **kwargs) -> Tuple[Union[pd.DataFrame, Dict[str, pd.DataFrame]], Dict]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    file_size = os.path.getsize(filepath) / (1024 * 1024)
    file_name = os.path.basename(filepath)
    
    try:
        result = pd.read_excel(filepath, sheet_name = sheet_name, **kwargs)
        
        metadata = {
            'filename': file_name,
            'file_size_mb': file_size
        }
        
        if isinstance(result, pd.DataFrame):
            metadata['rows'] = len(result)
            metadata['columns'] = list(result.columns)
            metadata['column_types'] = {col: str(dtype) for col, dtype in result.dtypes.items()}
            metadata['sheet_name'] = sheet_name if isinstance(sheet_name, (str, int)) else 'unknown'
        else:
            metadata['sheets'] = list(result.keys())
            metadata['sheet_info'] = {
                sheet: {
                    'rows': len(df),
                    'columns': list(df.columns)
                }
                for sheet, df in result.items()
            }
            
        return result, metadata
    
    except Exception as e:
        raise ValueError(f"Error handling Excel file: {str(e)}")
    
def load_json(filepath: str, normalize: bool = True, record_path: Optional[Union[str, List[str]]] = None, **kwargs) -> Tuple[pd.DataFrame, Dict]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    file_size = os.path.getsize(filepath) / (1024*1024)
    file_name = os.path.basename(filepath)
    
    try:
        with open(filepath, 'r', encoding = 'utf-8') as f:
            json_data = json.load(f)
        
        if normalize:
            if record_path:
                df = pd.json_normalize(json_data, record_path = record_path, **kwargs)
            else:
                if isinstance(json_data, list):
                    df = pd.json_normalize(json_data, **kwargs)
                else:
                    df = pd.json_normalize([json_data], **kwargs)
        else:
            df = pd.DataFrame(json_data)
        
        
        metadata = {
            'filename': file_name,
            'file_size_mb': file_size,
            'rows': len(df),
            'columns': list(df.columns),
            'column_types': {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        
        return df, metadata
    
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON file format")
    except Exception as e:
        raise ValueError(f"Error loading JSON file: {str(e)}")

def load_data(filepath: str, file_type: Optional[str] = None, **kwargs) -> Tuple[pd.DataFrame, Dict]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found {filepath}")
    
    if file_type is None:
        file_extension = os.path.splitext(filepath)[1].lower()
        if file_extension in ['.csv', '.txt', '.tsv', '.dat']:
            file_type = 'csv'
        elif file_extension in ['.xlsx', '.xls', '.xlsm']:
            file_type = 'excel'
        elif file_extension in ['.json']:
            file_type = 'json'
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")
    else:
        file_extension = os.path.splitext(filepath)[1].lower()
        if file_type == 'csv' and file_extension not in ['.csv', '.txt', '.tsv', '.dat']:
            raise ValueError(f"File with extension {file_extension} is not compatible with 'csv' file type")
        elif file_type == 'excel' and file_extension not in ['.xlsx', '.xls', '.xlsm']:
            raise ValueError(f"File with extension {file_extension} is not compatible with 'excel' file type")
        elif file_type == 'json' and file_extension not in ['.json']:
            raise ValueError(f"File with extension {file_extension} is not compatible with 'json' file type")
    
    if file_type == 'csv':
        if 'delimiter' not in kwargs and filepath.endswith('.tsv'):
            kwargs['delimiter'] = '\t'
        return load_csv(filepath, **kwargs)

    elif file_type == 'excel':
        return load_excel(filepath, **kwargs)
    
    elif file_type == 'json':
        return load_json(filepath, **kwargs)
    
    else:
        raise ValueError(f"Unsupported file type: {file_type}")