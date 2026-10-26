#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created:       2025-01-29
Last modified: 2026-09-29
Author:        Lucie Lu <lucie.lu@unimelb.edu.au>

Computes the firm-level default probability (cdr/PROB). Builds the Campbell-style
predictors from raw_data.parquet + sigma.parquet (winsorized 5%/95%), applies the logit
coefficients in drcoefficients2021.xlsx (originally from Jens Hilscher, shared by
Kevin Aretz), and aggregates equal- and value-weighted PROB. The S&P 500 series (for
rsize/exret) comes from sp500.csv, written by MakeSP500.py.
Inputs:  raw_data.parquet, sigma.parquet, sp500.csv, drcoefficients2021.xlsx
Outputs: PROB.parquet (only the columns read by MakePortfolios_v2.py), PROB_agg.csv
"""

#* ************************************** */
#* Libraries                              */
#* ************************************** */

import pandas as pd
import numpy as np
import os
from tqdm import tqdm
from pandas.tseries.offsets import *
tqdm.pandas()

# Path config (MNSC item 13: relative paths; run from the package root).
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import path

data_dir='Data/'

os.chdir(path)

# Read stock characteristic anomalies
dfstock=pd.read_parquet(path+data_dir+'raw_data.parquet')

# S&P 500 monthly index value and return (pulled from WRDS by MakeSP500.py)
sp500=pd.read_csv(path+data_dir+'sp500.csv', parse_dates=['jdate'])

#Check variable first start date at the stock level

dfstock_start_dic={}

for column in dfstock.columns:
    first_non_null_date=dfstock.dropna(subset=[column]).jdate.min()
    dfstock_start_dic[column]=first_non_null_date

dfstock_start=pd.DataFrame(list(dfstock_start_dic.items()), columns=['variables','start'])    


#Merge with S&P500

dfe=dfstock.merge(sp500, how='left',on='jdate')

#Merge with Sigma
sigma_df=pd.read_parquet(path+data_dir+'sigma.parquet')

dfe=pd.merge(dfe, sigma_df, on=['permno','permco','jdate'])

# Resample #
dfe = dfe.set_index(['jdate'])

# Check default prob predictors one by one

#NIMTA (0.77)

#Do not recompute NIMTA, use the one from the raw data

w='nimta'

dfe.loc[dfe[w] > np.nanpercentile(dfe[w],95),w] = np.nanpercentile(dfe[w],95)

dfe.loc[dfe[w] < np.nanpercentile(dfe[w],5),w] = np.nanpercentile(dfe[w],5)

#TLMTA

#Do not recompute TLMTA, use the one from the raw data

w='tlmta'

dfe.loc[dfe[w] > np.nanpercentile(dfe[w],95),w] = np.nanpercentile(dfe[w],95)

dfe.loc[dfe[w] < np.nanpercentile(dfe[w],5),w] = np.nanpercentile(dfe[w],5)

#CASHMTA

#Do not recompute CASHMTA, use the one from the raw data

w='cashmta'

dfe.loc[dfe[w] > np.nanpercentile(dfe[w],95),w] = np.nanpercentile(dfe[w],95)

dfe.loc[dfe[w] < np.nanpercentile(dfe[w],5),w] = np.nanpercentile(dfe[w],5)

#MB

dfe['me_be']=dfe['me']/dfe['beq0']/1000

w='me_be'

dfe.loc[dfe[w] > np.nanpercentile(dfe[w],95),w] = np.nanpercentile(dfe[w],95)

dfe.loc[dfe[w] < np.nanpercentile(dfe[w],5),w] = np.nanpercentile(dfe[w],5)

#EXRET (ok)

dfe['exret']=np.log(1+dfe['rets'])-np.log(1+dfe['sprtrn'])

w='exret'

dfe.loc[dfe[w] > np.nanpercentile(dfe[w],95),w] = np.nanpercentile(dfe[w],95)

dfe.loc[dfe[w] < np.nanpercentile(dfe[w],5),w] = np.nanpercentile(dfe[w],5)

#SIGMA

w='sigma'

dfe.loc[dfe[w] > np.nanpercentile(dfe[w],95),w] = np.nanpercentile(dfe[w],95)

dfe.loc[dfe[w] < np.nanpercentile(dfe[w],5),w] = np.nanpercentile(dfe[w],5)

#Size (ok)

dfe['rsize']=np.log(dfe['me']/dfe['usdval'])

w='rsize'

dfe.loc[dfe[w] > np.nanpercentile(dfe[w],95),w] = np.nanpercentile(dfe[w],95)

dfe.loc[dfe[w] < np.nanpercentile(dfe[w],5),w] = np.nanpercentile(dfe[w],5)


#PRICE (ok)

dfe['logprice'] = np.log(np.minimum(dfe['prc'], 15))

w='logprice'

dfe.loc[dfe[w] > np.nanpercentile(dfe[w],95),w] = np.nanpercentile(dfe[w],95)

dfe.loc[dfe[w] < np.nanpercentile(dfe[w],5),w] = np.nanpercentile(dfe[w],5)

# Winsorization increases the correlation with Kevin Aretz's predictors.


# Compute CDR default probability
CDR_coef=pd.read_excel(path+data_dir+'drcoefficients2021.xlsx')

CDR_coef.rename(columns={'YEAR':'year'}, inplace=True)

dfe['year']=dfe.index.year

dfe=dfe.reset_index()

CDR_merged=dfe.merge(CDR_coef, on='year', how='left').sort_values('year')

#forward fill the constant and beta coefficients

coefs = ['CONSTANT', 'BETA_NIMTA', 'BETA_TLMTA', 'BETA_RET','BETA_RSIZ',
       'BETA_SIGMA', 'BETA_PRICE', 'BETA_CASHMTA', 'BETA_MB']

CDR_merged[coefs] = CDR_merged[coefs].ffill()

fitted_values=CDR_merged['CONSTANT'] + \
    CDR_merged['nimta']*CDR_merged['BETA_NIMTA'] + \
    CDR_merged['tlmta']*CDR_merged['BETA_TLMTA'] + \
    CDR_merged['exret']*CDR_merged['BETA_RET']+ \
    CDR_merged['rsize']*CDR_merged['BETA_RSIZ']+ \
    CDR_merged['sigma']*CDR_merged['BETA_SIGMA']+ \
    CDR_merged['logprice']*CDR_merged['BETA_PRICE']+ \
    CDR_merged['cashmta']*CDR_merged['BETA_CASHMTA']+ \
    CDR_merged['me_be']*CDR_merged['BETA_MB']
    
    
logit_values=1 / (1 + np.exp(-fitted_values))      
    
CDR_merged['cdr']=logit_values

PROB=CDR_merged[['permno','jdate','year','me','nimta','cashmta','sigma','cdr']]

# Keep only the columns read by MakePortfolios_v2.py (me is used below for the
# value-weighted aggregate but is not needed downstream: EQUITY comes from raw_data).
PROB.drop(columns=['me']).to_parquet(path+data_dir+'PROB.parquet', index=False)


# 2025-09-30: Add aggregate default probability.
PROB = PROB.copy()

PROB.rename(columns={'jdate': 'date'}, inplace=True)

# --- Equal-weighted ---
# Equal-weighted mean + counts
prob_ew = (
    PROB.groupby('date', as_index=False)
        .agg(
            PROB_ew=('cdr', 'mean'),   # EW default prob (NA-safe)
            n_firms=('cdr', 'count'),  # number of firms with non-NA cdr
            # n_total=('cdr', 'size')  # <-- uncomment if you want all rows incl. NA
        )
)

# --- Value-weighted by EQUITY ---
# keep only rows with finite cdr and positive weights
tmp = PROB.loc[(PROB['cdr'].notna()) & (PROB['me'] > 0), ['date', 'cdr', 'me']].copy()
tmp['wx'] = tmp['cdr'] * tmp['me']

prob_vw = (
    tmp.groupby('date', as_index=False)
       .agg(wx_sum=('wx', 'sum'), w_sum=('me', 'sum'))
)
prob_vw['PROB_vw'] = prob_vw['wx_sum'] / prob_vw['w_sum']
prob_vw = prob_vw[['date', 'PROB_vw']]

# --- Combine ---
PROB_agg = prob_ew.merge(prob_vw, on='date', how='outer').sort_values('date')

PROB_agg.to_csv(path+'Data/'+'PROB_agg.csv', index=False)

