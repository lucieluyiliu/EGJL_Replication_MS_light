#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created:       2024-12-17
Last modified: 2026-09-29
Author:        Lucie Lu <lucie.lu@unimelb.edu.au>

Builds firm-level corporate credit spreads from the Dickerson, Robotti, and
Rossetti TRACE dataset (2025 vintage). Bonds (keyed by
cusip) are linked to firms via the cusip->permno crosswalk in the WRDS
MMN-corrected file (July 2024 version).
Inputs (extracts of the two files above with only the columns used here; see
MakeBondExtracts.py for how they are cut):
  trace_29_04_2025_extract.parquet   cusip_id, date, bond_maturity, CREDIT_SPREAD
  WRDS_MMN_2024_July_link.parquet    date, cusip, permno
Output:
  CS.parquet  firm 5Y and 10Y credit spreads, interpolated by bond maturity
"""

import os
import pandas as pd
import numpy as np
from tqdm import tqdm
tqdm.pandas()


# Path config (MNSC item 13: relative paths; run from the package root).
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import path

data_dir='Data/'

BOND_id=pd.read_parquet(path+data_dir+'WRDS_MMN_2024_July_link.parquet')

BOND_id['date'] = pd.to_datetime(BOND_id['date'], errors='coerce')

WRDS_BOND = pd.read_parquet(path+data_dir+'trace_29_04_2025_extract.parquet')
WRDS_BOND.rename(columns={'cusip_id':'cusip'}, inplace=True)

WRDS_BOND=pd.merge(WRDS_BOND, BOND_id, how='left', on=['cusip','date'])

WRDS_BOND['permno']=WRDS_BOND.groupby('cusip')['permno'].ffill() #forward fill permno from july2024 version of WRDS MMN data

WRDS_BOND['date']=pd.to_datetime(WRDS_BOND['date'])

def get_credit_spread(group, mat):
    if len(group)==1:
        # Only one bond, return its credit spread
        return group['CREDIT_SPREAD'].values[0]
    else:
        return np.interp(mat, group['bond_maturity'], group['CREDIT_SPREAD'])

# 10Y credit spread, interpolated from bonds with 8-12 years to maturity.
mat_short=8

mat_long=12

target=10

filtered_WRDS_BOND=WRDS_BOND[(WRDS_BOND['bond_maturity']>=mat_short)&(WRDS_BOND['bond_maturity']<=mat_long)]

CS10y=filtered_WRDS_BOND.groupby(['permno','date'], group_keys=False).apply(
    lambda group: get_credit_spread(group, target)
    ).reset_index()

CS10y.columns=['permno','date','CS10y']

# 5Y credit spread, interpolated from bonds with 3-7 years to maturity.
mat_short=3

mat_long=7

target=5 #target maturity in years

filtered_WRDS_BOND=WRDS_BOND[(WRDS_BOND['bond_maturity']>=mat_short)&(WRDS_BOND['bond_maturity']<=mat_long)]

CS5y=filtered_WRDS_BOND.groupby(['permno','date'], group_keys=False).apply(
    lambda group: get_credit_spread(group, target)
    ).reset_index()

CS5y.columns=['permno','date','CS5y']

CS=pd.merge(CS5y, CS10y, how='outer', on=['permno','date'])

#Save merged CS
CS.to_parquet(path+data_dir+'CS.parquet', index=False)




