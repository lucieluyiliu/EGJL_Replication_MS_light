#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created:       2026-09-29
Last modified: 2026-09-29
Author:        Lucie Lu <lucie.lu@unimelb.edu.au>

Cuts the two bond files shipped in Data/ from the full third-party files. It is NOT a
step of the build pipeline (Step1_PrepareAllData.py does not run it): the package ships
the extracts, and MakeCreditSpread.py reads them. This script documents how the
extracts were made and lets a replicator who holds the full files rebuild them.

Full files (not shipped):
  trace_29_04_2025.parquet                  Dickerson, Robotti, and Rossetti TRACE dataset,
                                            2025 vintage (openbondassetpricing.com)
  WRDS_MMN_Corrected_Data_2024_July.csv     MMN-corrected bond data, July 2024 version
                                            (openbondassetpricing.com)
Extracts (shipped): the same rows, only the columns MakeCreditSpread.py uses.
  trace_29_04_2025_extract.parquet          cusip_id, date, bond_maturity, CREDIT_SPREAD
  WRDS_MMN_2024_July_link.parquet           date, cusip, permno
"""

import os
import pandas as pd
import duckdb      # pyarrow cannot read the full TRACE file (repetition-level metadata); duckdb can

# Path config (MNSC item 13: relative paths; run from the package root).
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import path

data_dir='Data/'

trace_file = path+data_dir+'trace_29_04_2025.parquet'
# The file has both credit_spread and CREDIT_SPREAD. duckdb resolves names
# case-insensitively and returns the upper-case duplicate as CREDIT_SPREAD_1, so read
# every column and take the upper-case one under its original name.
trace = duckdb.query(f"SELECT * FROM '{trace_file}'").to_df()
trace = trace[['cusip_id', 'date', 'bond_maturity', 'CREDIT_SPREAD_1']]\
    .rename(columns={'CREDIT_SPREAD_1': 'CREDIT_SPREAD'})
trace.to_parquet(path+data_dir+'trace_29_04_2025_extract.parquet', index=False)
print('Saved Data/trace_29_04_2025_extract.parquet:', len(trace), 'bond-months')

link = pd.read_csv(path+data_dir+'WRDS_MMN_Corrected_Data_2024_July.csv',
                   usecols=['date', 'cusip', 'permno'])
link.to_parquet(path+data_dir+'WRDS_MMN_2024_July_link.parquet', index=False)
print('Saved Data/WRDS_MMN_2024_July_link.parquet:', len(link), 'bond-months')
