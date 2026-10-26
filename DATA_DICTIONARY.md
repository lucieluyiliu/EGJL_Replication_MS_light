# Data dictionary

This file lists the variables used in the paper, for every dataset the code reads or writes under
`Data/`, with the names used in the code and the files. Section 1 covers the files in the package;
Sections 2 and 3 describe the files the Python data build reads and writes, which are available
on request (see `README.md`, Section 2, for sources and provenance). Columns of a file that are
not listed are not used by the code. Definitions of the firm variables follow Table OA.3 of the
Online Appendix.

## Conventions

**Dates.** `date` and `jdate` are calendar period ends (month end or quarter end). Empirical
panels are quarterly unless stated otherwise.

**Units.** Compustat items are in millions of dollars. CRSP market equity (`me`, `EQUITY`) is in
thousands of dollars, so the code multiplies Compustat items by 1,000 when it combines the two.
Rates, returns, and ratios are decimals (0.05 = 5%).

**Suffixes.** Many variables are one base variable plus a suffix that gives the transformation and
the horizon. They are defined once here and not repeated in the tables.

| Suffix | Meaning |
|---|---|
| `_diff_1q`, `_diff_1y` | First difference over 1 quarter and over 4 quarters, x(t) - x(t-k) |
| `_pct_1q`, `_pct_1y` | Growth rate over 1 quarter and over 4 quarters, x(t)/x(t-k) - 1 |
| `_1q`, `_1y` (returns and averages) | Value over the last quarter and over the last 4 quarters; see each variable |

Firm-level changes and the levels `sales_at`, `gp_at`, `book_leverage`, and `market_leverage` are
winsorized at the 5th and 95th percentiles (`MakePortfolios_v2.py`).

**Labels in the R code and in the estimate files.** `Step2_MakeCorrelations_V4.R` renames the
variables of `industry_sorts.csv` as follows; the labels on the right appear in `Data/Estimates/`
and in the tables.

| Name in `industry_sorts.csv` | Label in R and in the tables |
|---|---|
| `cdr` | `PROB` |
| `market_leverage` | `MKTLEV` |
| `book_leverage` | `BOOKLEV` |
| `sales_at` | `SALES` |
| `gp_at` | `PROFIT` |
| `ret_exc` | `EXRET` |
| all other variables | unchanged (`SIGMA`, `CS5y`, `EBITDA`, `NIMTA`, `CASHMTA`, `ASSETS`, `EARN1Q`) |

## 1. Analysis data (read by the code that produces the exhibits)

### `industry_sorts.csv`
Quarterly panel of the 48 Fama-French industries, 1987Q2 to 2024Q4. Built by `MakeSorts.py`. Every
firm characteristic is the value-weighted average across the firms of the industry, with weights
equal to the firm's market equity at the end of the previous quarter. Read by
`Step2_MakeCorrelations_V4.R`, which drops financials, utilities, and "Other" and keeps the sample
period of the paper, 30 June 1987 to 31 December 2023. The correlations use the 1-quarter and
1-year changes of each characteristic, so the columns used are the ones with a suffix.

| Variable | Description |
|---|---|
| `date` | Quarter end |
| `ffi48` | Fama-French 48 industry code (1 to 48); names are in `FF48_industry.csv` |
| `SIGMA_diff_1q`, `SIGMA_diff_1y` | Change in equity return volatility, the annualized standard deviation of daily returns over the past 3 months |
| `cdr_diff_1q`, `cdr_diff_1y` | Change in the default probability (PROB) of Campbell, Hilscher, and Szilagyi (2008), computed in `MakePROB.py` |
| `market_leverage_diff_1q`, `market_leverage_diff_1y` | Change in market leverage, total liabilities divided by total liabilities plus market equity, `ltq / (me + ltq)` |
| `book_leverage`, `book_leverage_diff_1q`, `book_leverage_diff_1y` | Book leverage, total liabilities divided by total assets (`ltq / atq`), and its change. The level is used to sort industries into leverage terciles |
| `CS5y_diff_1q`, `CS5y_diff_1y` | Change in the 5-year firm credit spread (`CS.parquet`). Available from 2002Q3 |
| `ret_exc_1q`, `ret_exc_1y` | Stock return in excess of the 90-day Treasury bill return, over the quarter and compounded over the last 4 quarters |
| `EBITDA_pct_1q`, `EBITDA_pct_1y` | Growth of EBITDA summed over the last 4 quarters, where quarterly EBITDA = `saleq - cogsq - xsgaq`; annual EBITDA when the quarterly sum is missing |
| `NIMTA_pct_1q`, `NIMTA_pct_1y` | Growth of net income to market-valued total assets, `niq / (me + ltq)` |
| `CASHMTA_pct_1q`, `CASHMTA_pct_1y` | Growth of cash and short-term investments to market-valued total assets, `cheq / (me + ltq)` |
| `ASSETS_pct_1q`, `ASSETS_pct_1y` | Growth of total assets (`atq`) |
| `sales_at_pct_1q`, `sales_at_pct_1y` | Growth of sales over the last 4 quarters divided by total assets |
| `gp_at_pct_1q`, `gp_at_pct_1y` | Growth of gross profit (`saleq - cogsq`) over the last 4 quarters divided by total assets |
| `EARN1Q_pct_1q`, `EARN1Q_pct_1y` | Growth of `EARN1Q`, the I/B/E/S median 1-quarter-ahead earnings forecast (median EPS forecast times shares outstanding) divided by total assets |
| `mktcap_share` | Industry share of aggregate market equity; used to sort industries into size terciles |

### `AggShocks/Agg_shocks.csv`
Quarterly aggregate macroeconomic and financial series. Built by `MakeAggShocks_v1.py` from the
source files in `Data/AggShocks/`. Monthly series are sampled at the last month of the quarter.
Read by `Step2_MakeCorrelations_V4.R`, which uses the 1-quarter and 1-year columns below as the
aggregate shocks.

| Variable | Description |
|---|---|
| `date` | Quarter end |
| `IP_pct_1q`, `IP_pct_1y` | Growth of the industrial production index (FRED `INDPRO`) |
| `DeltaLiq_1q`, `DeltaLiq_1y` | Pastor and Stambaugh (2003) innovations in aggregate liquidity, averaged over the last 3 and the last 12 months |
| `CFNAI_diff_1q`, `CFNAI_diff_1y` | Change in the Chicago Fed National Activity Index, real-time vintage of December 2024 |
| `EPU_pct_1q`, `EPU_pct_1y` | Growth of the news-based U.S. economic policy uncertainty index of Baker, Bloom, and Davis |
| `UNRATE_diff_1q`, `UNRATE_diff_1y` | Change in the unemployment rate (FRED `UNRATE`), decimal |
| `MacroU_diff_1q`, `MacroU_diff_1y`, `RealU_diff_1q`, `RealU_diff_1y` | Change in macroeconomic and real uncertainty of Jurado, Ludvigson, and Ng, 3-month horizon |
| `NGDP_1q`, `NGDP_1y` | Survey of Professional Forecasters mean forecast of nominal GDP growth for the next quarter (decimal), and its average over the last 4 quarters |
| `FEDFUNDS_diff_1q`, `FEDFUNDS_diff_1y` | Change in the effective federal funds rate (FRED `FEDFUNDS`), decimal |
| `DeltaICR_1q`, `DeltaICR_1y` | Intermediary capital risk factor of He, Kelly, and Manela (2017), and its average over the last 4 quarters |

### `PROB_agg.csv`
Monthly aggregate default probability. Built by `MakePROB.py`. Read by `main_empirics.Rmd` for
Figure OA.5.

| Variable | Description |
|---|---|
| `date` | Month end |
| `n_firms` | Number of firms with a non-missing `cdr` in the month |
| `PROB_vw` | Average of the firm default probability `cdr`, weighted by market equity |

### Public series used for Figure OA.5 (read by `main_empirics.Rmd`)

| File | Variable | Description |
|---|---|---|
| `BAA10Y.csv` | `observation_date`, `BAA10Y` | Daily Moody's seasoned Baa corporate bond yield minus the 10-year Treasury yield, percent (FRED `BAA10Y`) |
| `BAMLC0A0CM.csv` | `observation_date`, `BAMLC0A0CM` | Daily ICE BofA U.S. corporate index option-adjusted spread, percent (FRED `BAMLC0A0CM`). Loaded with the other series but not among the predictors of the fit |
| `Market_CMDI.xlsx` | `eow_friday` | Week-ending Friday |
| | `Market` | Corporate Bond Market Distress Index for the whole market |
| `Moodys_US_defaults_quarterly.csv` | `quarter` | Quarter label, in the form `1970/QTR-1` |
| | `defaults` | Number of U.S. corporate defaults in the quarter, all industries |

### `FF48_industry.csv`

| Variable | Description |
|---|---|
| `Code` | Fama-French 48 industry code (1 to 48) |
| `Name` | Short industry name (for example `Agric`, `Food`) |

### `Estimates/` (correlation and bootstrap estimates)
Built by `Step2_MakeCorrelations_V4.R` and read by `main_empirics.Rmd`. Standard errors come from
a stationary block bootstrap (block length 4 quarters, 1,000 draws); the folder `length4/` is named
after the block length.

File names combine the following parts.

| Part of the file name | Meaning |
|---|---|
| `unconCorr` | Total (unconditional) correlations between industry pairs |
| `defCorrEq` | Excess correlations of the default risk variables, after removing the part explained by the equity moments |
| `allCorrFdAgEx1q` | Excess correlations of all variables, after removing the part explained by firm fundamentals, aggregate shocks, and expected earnings |
| `defCorrEqFdAgEx1q` | Excess correlations of the default risk variables, after removing equity moments, firm fundamentals, aggregate shocks, and expected earnings |
| `Bstrap` | Average across industry pairs with bootstrap standard errors |
| `18` | Computed over the 18 unrelated industry pairs; without `18`, over all industry pairs |
| `MV3`, `BOOKLEV3` | Comparison of the top and the bottom tercile of industry pairs sorted by market-capitalization share (`MV3`) or by book leverage (`BOOKLEV3`) |

| Variable | Description |
|---|---|
| `variable` | Variable label (`PROB`, `CS5y`, `MKTLEV`, `BOOKLEV`, `EXRET`, `SIGMA`, and in the total correlation files also the fundamentals `EBITDA`, `NIMTA`, `CASHMTA`, `ASSETS`, `PROFIT`, `SALES`, `EARN1Q`) |
| `subsample` | `Full Sample`, `Pre-GFC`, `Post-GFC`, `Ex-Recessions` (quarterly changes), or `Annual` (1-year changes, full sample) |
| `corr` | Correlation: for one industry pair in `unconCorr.RData`, averaged across pairs in the `Bstrap` files |
| `se` | Bootstrap standard error of `corr` |
| `p` | One-sided p-value, `1 - pnorm(corr / se)` |
| `corr1`, `corr2`, `se1`, `se2` | Tercile files: average correlation and standard error in the top tercile (1) and in the bottom tercile (2) |
| `diff`, `sediff` | Tercile files: `corr1 - corr2` and its bootstrap standard error |
| `Code1`, `Code2`, `Ind1`, `Ind2`, `pairname` | `unconCorr.RData` only: industry codes, industry names, and label of the pair |

### `DataFile.mat` (theory)
Solutions of the calibrated two-tree model, computed and saved by `code/matlab/main.m` when it
solves the model (`RECOMPUTE = true`, the default) and read back by a run with `RECOMPUTE = false`.
The file is about 2 GB and is not shipped; a full run creates it. Functions of the state are
stored on a grid: rows are `y = log(X)` for tree A,
1,001 points on [-3, 3]; columns are the output share `s` of tree A, 501 points on [0, 1].
Default boundaries are vectors over the `s` grid. The calibration is described in Sections 2.1,
2.6, and 3.3 of the paper.

| Variable | Size | Description |
|---|---|---|
| `E00`, `D00` | 1001 x 501 | Equity and debt value of tree A, baseline (perpetual debt, coupon `c = 0.4`) |
| `B00` | 501 x 1 | Optimal default boundary, baseline |
| `BM0`, `BP0` | 501 x 1 | Default boundary with low (`c = 0.2`) and high (`c = 0.6`) leverage (Figure 3) |
| `Bcorm09` ... `Bcorm01`, `Bcorp01` ... `Bcorp09` | 501 x 1 | Default boundary when the correlation between the trees' output is -0.9 ... -0.1 (`m`) and 0.1 ... 0.9 (`p`). `Bcorm05` uses -0.4999 and `Bcorp05` uses 0.5001 for numerical stability (Figure 4) |
| `E0M`, `D0M`, `B0M` | grid, grid, 501 x 1 | Equity value, debt value, and default boundary with 30-year average debt maturity |
| `E0`, `D0`, `B0` | as above | The same with 10-year average debt maturity |
| `E0P`, `D0P`, `B0P` | as above | The same with 5-year average debt maturity (Table 1, Figures 3 and 5) |
| `B00q`, `B0Mq`, `B0q`, `B0Pq` | 501 x 1 | Default boundary with renegotiation in default, for perpetual, 30-year, 10-year, and 5-year debt (Table 1, Panel B) |
| `BmuMM` ... `BmuPP` | 501 x 1 | Default boundary by borrower characteristics (Table OA.1). First letter: output volatility of tree A (`M` = 15%, `0` = 20%, `P` = 25%); second letter: expected output growth of tree A (`M` = 1.5%, `0` = 2.0%, `P` = 2.5%) |
| `probP`, `probQ` | 1001 x 501 | 10-year default probability of tree A under the physical and the risk-neutral measure |
| `xA`, `xB` | 2520 x 20000 | Simulated output of trees A and B: daily steps over 10 years (rows) for 20,000 simulated economies (columns); 0 after default |
| `sims` | 2520 x 20000 | Simulated output share of tree A |
| `DefA`, `DefB` | 2520 x 20000 | Default indicator of trees A and B (1 from the default date onwards) |
| `xAstat`, `xBstat`, `simsstat`, `DefAstat`, `DefBstat` | 2520 x 20000 | The same simulated quantities when the default boundary is held fixed at its value for the initial output share (static boundary) |
| `E00count`, `D00count` | 1001 x 501 | Equity and debt value of tree A in the counterfactual with a constant interest rate (Figure OA.1) |
| `D7`, `D15`, `D7mu`, `D7sig` | 1001 x 501 | Debt value in the sovereign debt case study (Table OA.10): 7-year maturity (baseline), 15-year maturity, higher growth (2.5%), and higher volatility (24%) |

## 2. Intermediate files built by the code in this package
Firm-level files created along the way from WRDS to `industry_sorts.csv`. The first five
(`raw_data.parquet`, `sigma.parquet`, `sp500.csv`, `FF48_map.csv`, `iclink.pkl`) are the frozen
WRDS extracts, written by the scripts that query WRDS; the others are built from them without
WRDS access. Each file holds only the columns listed here. Firms are identified by the CRSP
`permno`; `jdate` is the calendar month end (quarter end in `_main_data_2.parquet` and
`_ret_quarterly_2.parquet`).

### `raw_data.parquet`
Monthly firm panel that merges CRSP, Compustat (quarterly and annual), and I/B/E/S. Built by
`MakeMainDataFile_V1.py`. The sample is U.S. common stocks of corporations listed on the NYSE,
NYSE American, or Nasdaq. Accounting data are made available 2 months after the fiscal period end.
Compustat items are the mnemonics `atq`, `ltq`, `saleq`, `cogsq`, `xsgaq`, `niq`, `cheq`, the
book-equity components `seqq`, `ceqq`, `pstkq`, `pstkrq`, `pstknq`, `txditcq`, and the annual
`ebitda`. Read by `MakePROB.py` and `MakePortfolios_v2.py`.

| Variable | Description |
|---|---|
| `permno`, `permco`, `jdate` | CRSP security and company identifiers, and month end |
| `rets` | Monthly stock return (CRSP `mthret`) |
| `prc` | Month-end share price (CRSP `mthprc`) |
| `t90ret` | Monthly return on the 90-day Treasury bill (CRSP `mcti`) |
| `me` | Market equity of the company, price times shares outstanding summed over its securities, thousands of dollars |
| `atq` | Total assets (Compustat quarterly) |
| `beq0` | Book equity: shareholders' equity plus deferred taxes and investment tax credit, minus preferred stock |
| `ebitda_sum` | EBITDA (`saleq - cogsq - xsgaq`) summed over the last 4 quarters |
| `ebitdaA` | Annual EBITDA (Compustat annual `ebitda`); used when `ebitda_sum` is missing |
| `sales_at` | Sales over the last 4 quarters divided by total assets |
| `gp_at` | Gross profit (`saleq - cogsq`) over the last 4 quarters divided by total assets |
| `book_leverage_ltq` | Book leverage, `ltq / atq` |
| `market_leverage` | Market leverage, `ltq / (me + ltq)` |
| `earn1q_at` | I/B/E/S median 1-quarter-ahead earnings forecast (median EPS forecast times shares outstanding) divided by total assets |
| `nimta` | Net income to market-valued total assets, `niq / (me + ltq)` |
| `tlmta` | Total liabilities to market-valued total assets, `ltq / (me + ltq)` |
| `cashmta` | Cash and short-term investments to market-valued total assets, `cheq / (me + ltq)` |

### `sigma.parquet`
Built by `MakeSIGMA.py` from CRSP daily returns. Read by `MakePROB.py`.

| Variable | Description |
|---|---|
| `permno`, `permco`, `jdate` | Identifiers and month end |
| `sigma` | Annualized standard deviation of daily stock returns over the past 3 months; missing values are replaced by the cross-sectional mean of the month |

### `sp500.csv`
Monthly S&P 500 index series from CRSP (`msp500_v2`). Built by `MakeSP500.py`. Read by
`MakePROB.py`.

| Variable | Description |
|---|---|
| `jdate` | Month end |
| `usdval` | Total market value of the index, thousands of dollars |
| `sprtrn` | Monthly return of the index |

### `FF48_map.csv`
One row per CRSP stock with monthly data up to 31 December 2023. Built by `MakeFF48.py` from the
CRSP name history and Kenneth French's SIC ranges (`Siccodes48.txt`). Read by
`MakePortfolios_v2.py`.

| Variable | Description |
|---|---|
| `permno` | CRSP identifier |
| `sic` | SIC code of the stock: its last CRSP name record on or before 31 December 2023 (one code per stock) |
| `ffi48` | Fama-French 48 industry code implied by `sic`; SIC 9999 is assigned to industry 48 (Other); missing when `sic` is outside French's ranges |

### `PROB.parquet`
Monthly firm default probability. Built by `MakePROB.py`, following Campbell, Hilscher, and
Szilagyi (2008) with the coefficients in `drcoefficients2021.xlsx`. The eight predictors are
winsorized at the 5th and 95th percentiles: `nimta`, `tlmta`, `cashmta` from `raw_data.parquet`;
`sigma` from `sigma.parquet`; `exret`, the monthly log stock return minus the monthly log return of
the S&P 500; `rsize`, the log of the firm's market equity over the total market value of the
S&P 500; `me_be`, the market-to-book ratio of equity, `me / beq0`; and `logprice`, the log of the
share price capped at 15 dollars. Only the columns below are kept. Read by `MakePortfolios_v2.py`.

| Variable | Description |
|---|---|
| `permno`, `jdate`, `year` | Identifier, month end, and calendar year (used to match the coefficients) |
| `nimta`, `cashmta` | Winsorized predictors, as in `raw_data.parquet` |
| `sigma` | Winsorized equity return volatility, from `sigma.parquet` |
| `cdr` | Default probability (PROB): logistic function of the eight predictors with the coefficients of the year |

### `CS.parquet`
Monthly firm credit spreads. Built by `MakeCreditSpread.py`. Read by `MakeSorts.py`.

| Variable | Description |
|---|---|
| `permno`, `date` | Identifier and month end |
| `CS5y` | 5-year credit spread of the firm, interpolated at 5 years across its bonds with 3 to 7 years to maturity (the spread of the bond if there is only one) |

### `_ret_quarterly_2.parquet`
Quarterly firm excess returns. Built by `MakePortfolios_v2.py`. Read by `MakeSorts.py`.

| Variable | Description |
|---|---|
| `permno`, `jdate` | Identifier and quarter end |
| `ret_exc_1q` | Stock return over the quarter minus the 90-day Treasury bill return for the quarter |
| `ret_exc_1y` | Stock return compounded over the last 4 quarters minus the Treasury bill return compounded over the same quarters |

### `_main_data_2.parquet`
Quarterly firm panel. Built by `MakePortfolios_v2.py`. Read by `MakeSorts.py`, which aggregates it
by industry into `industry_sorts.csv`.

| Variable | Description |
|---|---|
| `permno`, `jdate` | Identifier and quarter end |
| `EQUITY` | Market equity (`me`), thousands of dollars; its lag is the weight of the industry averages |
| `SIGMA`, `cdr`, `NIMTA`, `CASHMTA` | Quarter-end values of `sigma`, `cdr`, `nimta`, and `cashmta` from `PROB.parquet` |
| `ASSETS`, `EBITDA`, `sales_at`, `gp_at`, `book_leverage`, `market_leverage` | Quarter-end values of `atq`, EBITDA (`ebitda_sum`, or `ebitdaA` when missing), `sales_at`, `gp_at`, `book_leverage_ltq`, and `market_leverage` from `raw_data.parquet` |
| variables with a suffix | 1-quarter and 1-year changes of the variables above and of `EARN1Q` (`earn1q_at` from `raw_data.parquet`; only its changes are kept), winsorized at the 5th and 95th percentiles (see Conventions) |
| `ffi48` | Fama-French 48 industry of the firm, from `FF48_map.csv` |

### `iclink.pkl`
CRSP to I/B/E/S link table. Built by `iclink.py`. Read by `MakeMainDataFile_V1.py`, which keeps
the links with `score` of 0 or 1.

| Variable | Description |
|---|---|
| `ticker` | I/B/E/S ticker |
| `permno` | CRSP identifier |
| `score` | Quality of the link, from 0 (best: CUSIP, dates, and company name match) to 6 (worst) |

## 3. Third-party input files

### `trace_29_04_2025_extract.parquet`
Monthly corporate bond data of Dickerson, Robotti, and Rossetti, 2025 vintage, cut
to the four columns below (`MakeBondExtracts.py`). Read by `MakeCreditSpread.py`. The other
columns of the full file are documented by the provider (openbondassetpricing.com).

| Variable | Description |
|---|---|
| `cusip_id` | Bond CUSIP |
| `date` | Month end |
| `bond_maturity` | Time to maturity of the bond, years |
| `CREDIT_SPREAD` | Credit spread of the bond, computed from the MMN-adjusted signal price (the full file also has `credit_spread`, from the month-end price, which is not used) |

### `WRDS_MMN_2024_July_link.parquet`
Bond-to-firm link, cut from the MMN-corrected bond data of Open Source Bond Asset Pricing, July
2024 version (`MakeBondExtracts.py`). `MakeCreditSpread.py` uses it to link bonds to firms; the
link is carried forward for the months after the end of this file.

| Variable | Description |
|---|---|
| `date` | Month end |
| `cusip` | Bond CUSIP |
| `permno` | CRSP identifier of the issuer |

### `Siccodes48.txt`
Kenneth French's definition of the 48 industries: for each industry, its number, short name, long
name, and the list of 4-digit SIC ranges it covers. Read by `MakeFF48.py`.

### `drcoefficients2021.xlsx`
Coefficients of the default probability model, one row per year. Read by `MakePROB.py`; the last
available year is carried forward.

| Variable | Description |
|---|---|
| `YEAR` | Calendar year in which the coefficients apply |
| `CONSTANT` | Intercept of the logit model |
| `BETA_NIMTA`, `BETA_TLMTA`, `BETA_CASHMTA` | Coefficients on `nimta`, `tlmta`, and `cashmta` |
| `BETA_RET`, `BETA_RSIZ`, `BETA_SIGMA`, `BETA_PRICE`, `BETA_MB` | Coefficients on `exret`, `rsize`, `sigma`, `logprice`, and `me_be` |

### Source files in `AggShocks/`
Read by `MakeAggShocks_v1.py`, which builds `Agg_shocks.csv` from them.

| File | Variable | Description |
|---|---|---|
| `INDPRO.csv`, `UNRATE.csv`, `FEDFUNDS.csv` | `observation_date`, and the series | Monthly industrial production index, unemployment rate (percent), and effective federal funds rate (percent), from FRED |
| `liq_data_1962_2024.csv` | `% Month`, `Innov Liq (eq8)` | Month (`yyyymm`) and the Pastor and Stambaugh (2003) innovation in aggregate liquidity |
| `cfnai-realtime-3-xlsx.xlsx` | `Date`, `CF122024` | Month and the Chicago Fed National Activity Index as published in December 2024; the other columns are earlier real-time vintages |
| `US_Policy_Uncertainty_Data.xlsx` | `Year`, `Month`, `News_Based_Policy_Uncert_Index` | News-based economic policy uncertainty index of Baker, Bloom, and Davis |
| `MacroFinanceUncertainty_202506Update/` (`MacroUncertaintyToCirculate.xlsx`, `RealUncertaintyToCirculate.xlsx`, `FinancialUncertaintyToCirculate.xlsx`) | `Date`, `h=3` | Month and the uncertainty index of Jurado, Ludvigson, and Ng at the 3-month horizon (June 2025 update). The macroeconomic and the real index are used |
| `meanGrowth.xlsx` (sheet `NGDP`) | `YEAR`, `QUARTER`, `dngdp3` | Survey of Professional Forecasters mean forecast of nominal GDP growth for the next quarter, percent |
| `HKM_Factors.csv` | `yyyyq`, `intermediary_capital_risk_factor` | Quarter and the intermediary capital risk factor of He, Kelly, and Manela (2017) |

