#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created:       2026-09-30
Last modified: 2026-09-30
Author:        Lucie Lu <lucie.lu@unimelb.edu.au>

Pulls the monthly S&P 500 index series from WRDS: total market value (usdval) and
return (sprtrn), used by MakePROB.py for the relative-size and excess-return
predictors of the default probability.
Inputs:  WRDS (crsp.msp500_v2)
Outputs: Data/sp500.csv (columns jdate, usdval, sprtrn; jdate is the month end)
"""

import os
import pandas as pd
import wrds
from pandas.tseries.offsets import MonthEnd

# Path config (MNSC item 13: relative paths; run from the package root).
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import path, wrds_username

data_dir='Data/'

start_date='1/1/1986'

end_date='12/31/2024'

os.chdir(path)

conn=wrds.Connection(wrds_username=wrds_username)   # WRDS username from config.py

sp500 = conn.raw_sql(f"""
    SELECT caldt as date, usdval, sprtrn
    FROM crsp.msp500_v2
  where caldt>='{start_date}' and caldt<='{end_date}'
""")

conn.close()

sp500['jdate']=pd.to_datetime(sp500['date'])+MonthEnd(0)

sp500[['jdate','usdval','sprtrn']].sort_values('jdate').to_csv(path+data_dir+'sp500.csv', index=False)

print('Saved Data/sp500.csv:', len(sp500), 'months,', sp500['jdate'].min().date(), 'to', sp500['jdate'].max().date())
