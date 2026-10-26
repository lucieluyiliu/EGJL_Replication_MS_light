#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created:       2026-09-21
Last modified: 2026-09-29
Author:        Lucie Lu <lucie.lu@unimelb.edu.au>

Builds the stock-level Fama-French 48 industry map FF48_map.csv from WRDS.

Every CRSP stock (permno with monthly data up to end_date) gets a single SIC code for
its whole history: the last SIC code in the CRSP name history (crsp.stocknames) that
is effective on or before end_date, the end of the sample period of the paper
(31 December 2023). SIC codes are mapped to the 48 industries with the SIC ranges
published by Kenneth French (Siccodes48.txt). The unclassified SIC code 9999 is
assigned to industry 48 (Other); any other SIC code outside French's ranges is left
unclassified (missing ffi48). MakePortfolios_v2.py merges the map on permno and drops
unclassified stocks.

The map replaces the firm-month industry table originally shared by Alex Dickerson
(FF48_Stocks.h5, CRSP header SIC codes as of end-2022). Rebuilt with end-2022 codes,
this script reproduced that table for 99.76% of stock-months (the differences come
from later CRSP revisions of SIC codes).

Inputs:  WRDS (crsp.msf_v2, crsp.stocknames); Data/Siccodes48.txt (Kenneth French's
         data library)
Outputs: Data/FF48_map.csv (columns permno, sic, ffi48)
"""

#* ************************************** */
#* Libraries                              */
#* ************************************** */

import os
import re
import pandas as pd
import numpy as np
import wrds

# Path config (MNSC item 13: relative paths; run from the package root).
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import path, wrds_username

data_dir='Data/'

end_date='12/31/2023'      # SIC codes are taken as of this date (end of the sample period)

os.chdir(path)


#* ************************************** */
#* SIC -> FF48 map (Kenneth French)       */
#* ************************************** */

# Siccodes48.txt lists each industry as a header line ("<number> <short name> <long
# name>") followed by its SIC ranges ("<first>-<last> <description>").
ranges = []
industry = None
with open(path+data_dir+'Siccodes48.txt', encoding='latin-1') as f:
    for line in f:
        sic_range = re.match(r'^\s+(\d{4})-(\d{4})', line)
        header = re.match(r'^\s*(\d{1,2})\s+(\S+)\s+\S', line)
        if sic_range and industry is not None:
            ranges.append((industry[0], industry[1], int(sic_range.group(1)), int(sic_range.group(2))))
        elif header:
            industry = (int(header.group(1)), header.group(2))

ff48 = pd.DataFrame(ranges, columns=['ffi48', 'ffi48_desc', 'sic_first', 'sic_last'])
assert ff48['ffi48'].nunique() == 48, 'Siccodes48.txt did not parse into 48 industries'

# Lookup table indexed by the 4-digit SIC code (0-9999); NaN = not classified.
sic_to_ff48 = np.full(10000, np.nan)
for r in ff48.itertuples(index=False):
    sic_to_ff48[r.sic_first:r.sic_last+1] = r.ffi48
sic_to_ff48[9999] = 48          # SIC 9999 -> Other


#* ************************************** */
#* CRSP stocks and SIC codes              */
#* ************************************** */

conn=wrds.Connection(wrds_username=wrds_username)   # WRDS username from config.py

# Stocks with monthly data on or before end_date.
crsp_m = conn.raw_sql(f"""
                      select distinct permno
                      from crsp.msf_v2
                      where mthcaldt <= '{end_date}'
                      """)

# CRSP name history: each row is a period (namedt to nameenddt) with its SIC code.
names = conn.raw_sql(f"""
                     select permno, namedt, siccd
                     from crsp.stocknames
                     where namedt <= '{end_date}'
                     """, date_cols=['namedt'])

conn.close()

# Header SIC as of end_date: the SIC code of the last name period that started on or
# before end_date. It is constant within a stock.
hsic = names.sort_values(['permno', 'namedt']).groupby('permno', as_index=False).last()
hsic = hsic[['permno', 'siccd']].rename(columns={'siccd': 'sic'})

df = crsp_m.merge(hsic, how='left', on='permno')

print('CRSP stocks:', len(df))
print('  of which without a SIC code (dropped):', int(df['sic'].isnull().sum()))
df = df[~df['sic'].isnull()].copy()

df['permno'] = df['permno'].astype(int)
df['sic'] = df['sic'].astype(int)

in_range = df['sic'].between(0, 9999)
df['ffi48'] = np.nan
df.loc[in_range, 'ffi48'] = sic_to_ff48[df.loc[in_range, 'sic'].values]

df = df.sort_values('permno')[['permno', 'sic', 'ffi48']].reset_index(drop=True)

df.to_csv(path+data_dir+'FF48_map.csv', index=False)

print('Saved Data/FF48_map.csv:', len(df), 'stocks,',
      int(df['ffi48'].notnull().sum()), 'classified into 48 industries')
