import unittest
import pandas as pd
import numpy as np
import warnings

class TestCleaner(unittest.TestCase):
    """Test cases for the cleaner module"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Sample DataFrame with various data types and issues
        self.df = pd.DataFrame({
            'ID': [1, 2, 3, 4, 5, None, 7],
            'Name': ['John', 'Jane', None, 'Bob', 'Alice', 'Charlie', 'David'],
            'Age': [30, 25, 40, None, 35, 22, 28],
            'Salary': [75000, 82000, 95000, 110000, np.nan, 68000, 79000],
            'Department': ['Engineering', 'Marketing', 'Finance', 'Management', 'Engineering', None, 'Marketing'],
            'StartDate': ['2020-01-15', '2019-05-20', None, '2018-10-10', '2021-02-28', '2020-07-15', '2019-12-01'],
            'Rating': [4.5, 3.8, 4.2, 4.7, 3.9, 4.1, 10.0],  # 10.0 is an outlier
            'Active': [True, False, True, None, True, False, True],
            'ZeroCol': [0, 0, 0, 0, 0, 0, 0],
            'DuplicateID': [1, 2, 3, 4, 5, 6, 1]  # First and last values are duplicates
        })
        
        # DataFrame with duplicate rows
        self.dup_df = pd.DataFrame({
            'A': [1, 2, 3, 1, 2],
            'B': ['x', 'y', 'z', 'x', 'y'],
        })
        
        # DataFrame with mixed column names
        self.mixed_cols_df = pd.DataFrame({
            'First Name': ['John', 'Jane', 'Bob'],
            'last_name': ['Doe', 'Smith', 'Johnson'],
            'AGE': [30, 25, 40],
            'email-address': ['john@example.com', 'jane@example.com', 'bob@example.com'],
            'phone#': ['555-1234', '555-5678', '555-9012']
        })
        
        # DataFrame with mixed data types
        self.types_df = pd.DataFrame({
            'StringNumbers': ['1', '2', '3', '4', '5'],
            'MixedDates': ['2020-01-01', '2020/02/01', '03-Mar-2020', '04/Apr/2020', '2020-05-05'],
            'BoolStrings': ['true', 'false', 'yes', 'no', 'True'],
            'FloatInts': [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        
        # Ignore warnings during tests
        warnings.filterwarnings('ignore')