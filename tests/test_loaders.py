import os
import unittest
import pandas as pd
import numpy as np
import tempfile
import json
from io import StringIO
from unittest.mock import patch, mock_open

from EDA_toolkit.loaders import load_csv, load_excel, load_json

class TestLoaders(unittest.TestCase):
    """Test Cases for loaders module."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.TemporaryDirectory()
        
        self.csv_data = """id,name,age,salary,department\n
1,John Doe,30,75000,Engineering\n
2,Jane Smith,28,82000,Marketing\n
3,Bob Johnson,35,95000,Finance\n
4,Alice Brown,25,68000,Engineering\n
5,Charlie Wiilson,25,68000,Engineering"""

        self.json_data = [
            {"id": 1, "name": "John Doe", "age": 30, "salary": 75000, "department": "Engineering"},
            {"id": 2, "name": "Jane Smith", "age": 28, "salary": 82000, "department": "Marketing"},
            {"id": 3, "name": "Bob Johnson", "age": 35, "salary": 95000, "department": "Finance"},
            {"id": 4, "name": "Alice Brown", "age": 42, "salary": 110000, "department": "Management"},
            {"id": 5, "name": "Charlie Wilson", "age": 25, "salary": 68000, "department": "Engineering"}
        ]
        
        # Create test files
        self.csv_path = os.path.join(self.temp_dir.name, "test_data.csv")
        self.excel_path = os.path.join(self.temp_dir.name, "test_data.xlsx")
        self.json_path = os.path.join(self.temp_dir.name, "test_data.json")
        self.tsv_path = os.path.join(self.temp_dir.name, "test_data.tsv")
        
        # Write CSV file
        with open(self.csv_path, 'w') as f:
            f.write(self.csv_data)
        
        # Write TSV file (tab-separated)
        with open(self.tsv_path, 'w') as f:
            f.write(self.csv_data.replace(',', '\t'))
        
        # Create Excel file
        pd.DataFrame(self.json_data).to_excel(self.excel_path, index=False)
        
        # Write JSON file
        with open(self.json_path, 'w') as f:
            json.dump(self.json_data, f)
        
    def tearDown(self):
        """Clean up test fixtures after each test method."""
        self.temp_dir.cleanup()
    
    def test_load_csv_basic(self):
        """Test Basic CSV loading functionality."""
        df, metadata = load_csv(self.csv_path)
        self.assertEqual(len(df), 5)
        self.assertEqual(list(df.columns), ['id', 'name', 'age', 'salary', 'department'])
        
        self.assertEqual(metadata['rows'], 5)
        self.assertEqual(metadata['columns'], ['id', 'name', 'age', 'salary', 'department'])
        self.assertEqual(os.path.basename(metadata['filename']), "test_data.csv")
        self.assertIn('column_types', metadata)

    def test_loada_csv_with_options(self):
        """Test CSV loading with additional options."""
        df, metadata = load_csv(
            self.csv_path,
            delimiter = ',',
            encoding = 'utf-8',
            infer_types = True,
            parse_dates = False,
            usecols = ['name', 'age', 'department']
        )

        self.assertEqual(list(df.columns), ['name', 'age', 'department'])
        self.assertEqual(len(df), 5)
        
        self.assertEqual(df['age'].dtype, np.int64)

    def test_load_csv_missing_file(self):
        """Test handling of missing CSV file."""
        with self.assertRaises(FileNotFoundError):
            load_csv('non_existent_file.csv')

    def test_load_csv_bad_encoding(self):
        """Test handling of encoding issues."""
        # Create mock CSV with non-UTF8 characters
        mock_csv_data = b'id,name\n1,\xff\xfeTest'
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            f.write(mock_csv_data)
            bad_encoding_path = f.name
        
        try:
            df, metadata = load_csv(bad_encoding_path)
            self.assertIn('encoding_used', metadata)
        except:
            pass
        
        os.unlink(bad_encoding_path)

    def test_load_excel_basic(self):
        """Test Basic Excel loading functionality."""
        df, metadata = load_excel(self.excel_path)
        
        self.assertEqual(len(df), 5)
        self.assertEqual(list(df.columns), ['id', 'name', 'age', 'salary', 'department'])
        
        self.assertEqual(metadata['rows'], 5)
        self.assertEqual(metadata['columns'], ['id', 'name', 'age', 'salary', 'department'])
        self.assertEqual(os.path.basename(metadata['filename']), "test_data.xlsx")
    
    def test_load_excel_missing_file(self):
        """Test handling of missing Excel file."""
        with self.assertRaises(FileNotFoundError):
            load_excel('non_existent_file.xlsx')

    def test_load_excel_with_sheet_name(self):
        """Test Excel loading with specific sheet name."""
        with pd.ExcelWriter(self.excel_path, engine='openpyxl') as writer:
            pd.DataFrame(self.json_data).to_excel(writer, sheet_name='Sheet1', index=False)
            pd.DataFrame({'A': [1, 2], 'B': [3, 4]}).to_excel(writer, sheet_name='Sheet2', index=False)
        
        df, metadata = load_excel(self.excel_path, sheet_name='Sheet2')
        self.assertEqual(list(df.columns), ['A', 'B'])
        self.assertEqual(len(df), 2)
        
        dfs, metadata = load_excel(self.excel_path, sheet_name=None)
        self.assertIsInstance(dfs, dict)
        self.assertIn('Sheet1', dfs)
        self.assertIn('Sheet2', dfs)
        self.assertIn('sheets', metadata)
        self.assertEqual(metadata['sheets'], ['Sheet1', 'Sheet2'])

    def test_load_json_basic(self):
        """Test basic JSON loading functionality."""
        df, metadata = load_json(self.json_path)
        
        self.assertEqual(len(df), 5)
        self.assertEqual(list(df.columns), ['id', 'name', 'age', 'salary', 'department'])
        
        self.assertEqual(metadata['rows'], 5)
        self.assertEqual(metadata['columns'], ['id', 'name', 'age', 'salary', 'department'])
        self.assertEqual(os.path.basename(metadata['filename']), "test_data.json")
        
    def test_load_json_nested(self):
        """Test loading nested JSON with normalization"""
        nested_json = {
            "data": [
                {"user": {"id": 1, "name": "John"}, "stats": {"visits": 10}},
                {"user": {"id": 2, "name": "Jane"}, "stats": {"visits": 20}}
            ]
        }
        
        with tempfile.NamedTemporaryFile(suffix = '.json', delete=False, mode = 'w') as f:
            json.dump(nested_json, f)
            nested_json_path = f.name
        
        try:
            df, metadata = load_json(nested_json_path, normalize = True, record_path = ['data'])
            self.assertEqual(len(df), 2)
            
            self.assertIn('user.id', df.columns)
            self.assertIn('stats.visits', df.columns)
        finally:
            os.unlink(nested_json_path)
    
    def test_load_json_invalid(self):
        """Test handling invalid JSON file"""
        with tempfile.NamedTemporaryFile(suffix = '.json', delete = False) as f:
            f.write(b'{"invalid": JSON')
            invalid_json_path = f.name
        
        try:
            with self.assertRaises(ValueError):
                load_json(invalid_json_path)
        finally:
            os.unlink(invalid_json_path)
        
if __name__ == '__main__':
    unittest.main()