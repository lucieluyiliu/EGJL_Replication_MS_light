# README

**Manuscript title:** Excess Co-movement in Default Risk

**Manuscript ID:** MS-FIN-2025-00698

**Author(s):** Jan Ericsson, Kristoffer Glover, Alexandre Jeanneret, Lucie Yiliu Lu

## 1. Overview
This is the replication package for the paper (Management Science). It has two self-contained
components:

- **Theory (MATLAB)**: the calibrated two-tree model. Produces Tables 1–2, OA.1–OA.2, and OA.10, and
  Figures 2–6 and OA.1–OA.4. Code in `code/matlab/`.
- **Empirics (Python + R)**: industry-pair **total** and **excess** correlations of default risk and
  equity moments. Produces Table 3, Online Appendix Tables OA.4–OA.9, and the default-probability
  (PROB) goodness-of-fit Figure OA.5. Code in `code/python/` and `code/r/`.

Contents of the package:

| Path | Content |
|---|---|
| `README.md` | This file |
| `DATA_DICTIONARY.md` | Variable dictionaries for the datasets in `Data/` (see Section 3) |
| `config.py`, `config.R` | Central paths, all relative to the package root, so no path needs editing |
| `run_all.py` | Single driver: runs the data build (optional), the empirical exhibits, and the theory exhibits in order, and writes one log (Section 5) |
| `master.R` | Master script for the empirical exhibits (called by `run_all.py`; can also be run on its own) |
| `code/matlab/` | Theory code: `main.m` plus its functions (documented in `code/matlab/readme.txt`) |
| `code/python/` | Data build from WRDS: the driver `Step1_PrepareAllData.py` runs `iclink.py` and the `Make*.py` scripts. `MakeBondExtracts.py` is documentation only |
| `code/r/` | Correlations and block bootstrap (`Step2_MakeCorrelations_V4.R`, `functions_V4.1.R`) and the exhibits (`main_empirics.Rmd`) |
| `Data/` | The series the analysis code reads (see Section 2) |
| `output/tables/`, `output/figures/` | The tables (`.tex`) and figures of the paper, as produced by the code |
| `output/main_empirics.html` | Report knitted by `main_empirics.Rmd` |
| `output/log/` | Log files of our runs: `step1_build.log` (Python data build), `master_R.log` (bootstrap and exhibits), `matlab_run.log` (theory). `run_all.py` adds `replication.log` when it runs |
| `renv.lock`, `renv/`, `install_R_packages.R` | R environment |
| `.Rprofile` | Hidden file that activates the `renv` environment when R starts in the package folder |
| `pyproject.toml`, `uv.lock`, `requirements.txt`, `environment.yml` | Python environment |
| `.python-version` | Hidden file that pins Python 3.11 for `uv` |

How to proceed from beginning to end:

1. Set up the software environment (Section 4).
2. From the package root, run

       python run_all.py

   It knits the empirical exhibits from the data shipped in `Data/` (no WRDS access needed, under a
   minute) and then runs `code/matlab/main.m`, which solves the calibrated model and simulates it
   (about 10 hours on 18 cores). Every exhibit of the paper is then in `output/`. To see the empirical
   part alone first, run `python run_all.py --no-matlab`.
3. Optional: `python run_all.py --bootstrap` also re-estimates the bootstrap standard errors
   (about 1 h more). Section 5 describes the options, how to run each stage on its own, and how
   the data in `Data/` were prepared from WRDS with the Python code (rerunning that build needs a
   WRDS account; it is not needed to reproduce the exhibits).

## 2. Data availability and provenance
This paper relies on data. The replication package includes the series that the analysis
code reads to produce every exhibit (the industry panel, the aggregate shocks, the aggregate
default probability, the bootstrap estimates, and the public series behind Figure OA.5), together
with the code that builds those series from WRDS and from the bond data, and every input to that
code other than WRDS itself (the bond extracts, the default-probability coefficients, and the
public macro sources). The firm-level files pulled from WRDS and the intermediate files derived
from them are not in the package: a fresh run of the build regenerates them from WRDS, subject to
WRDS data revisions (see Data vintage below), and the frozen vintage behind the published numbers
is available to the journal's code and data editor on request. This section describes every
dataset used, where it comes from, and how it can be obtained or rebuilt.

The theory component uses no external data. The empirical analysis uses data from **WRDS**
(CRSP, Compustat, IBES), corporate bond data from the **Open Source Bond Asset Pricing** project
(Dickerson, Robotti, and Rossetti), public sources (FRED and authors' websites), a Moody's default
series, and the default-probability coefficients shared with us by other researchers. Each file is listed below with its
source.

### Data vintage
WRDS revises its databases continuously, so a fresh download does not return exactly the data
behind the paper. The WRDS extracts are frozen as of the build run of 31 October 2026 that
produced the results in the paper. The package ships the series built from this vintage, together
with the code that rebuilds every extract from WRDS (`code/python/`, "how the data were prepared"
in Section 5). Researchers with WRDS access can rerun that code; results from a later vintage can
differ slightly from the published ones. The frozen extracts themselves, which reproduce the
published numbers exactly, are available on request.

The Python scripts obtain the WRDS data by querying the WRDS server directly, for January 1986 to
December 2024. They need a WRDS subscription that covers CRSP, Compustat, and I/B/E/S. Five scripts
query WRDS and write the frozen extracts (`iclink.py`, `MakeFF48.py`, `MakeMainDataFile_V1.py`,
`MakeSIGMA.py`, `MakeSP500.py`); the queries themselves are in those scripts. The remaining scripts
run from the extracts and need no WRDS access, so the whole empirical build can be repeated from
the frozen extracts without a WRDS account.

### The data (`Data/`)
Every file keeps only the variables the code reads. The tables below say for each file whether it
is in the package or is produced by the build (the files pulled from WRDS and derived from those
pulls, about 300 MB in total, are not shipped; the frozen vintage is available on request).

#### Frozen WRDS extracts (written by the five WRDS scripts; not in the package: regenerated by a fresh run, frozen vintage on request)
| File | Description | Source and how to obtain |
|---|---|---|
| `raw_data.parquet` | Merged CRSP, Compustat, and IBES firm-month panel: returns, price, market equity, the balance-sheet and profitability variables, the IBES earnings forecast, and the default-probability predictors (19 columns) | WRDS (CRSP, Compustat, IBES). Built by `MakeMainDataFile_V1.py` |
| `iclink.pkl` | CRSP to IBES link table | WRDS (CRSP, IBES). Built by `iclink.py` |
| `FF48_map.csv` | One row per CRSP stock: SIC code as of 31 December 2023 (the end of the sample period) and the Fama–French 48 industry it maps to | WRDS (CRSP `msf_v2`, `stocknames`) and Kenneth French's SIC ranges (`Siccodes48.txt`). Built by `MakeFF48.py` |
| `sigma.parquet` | Firm-month equity return volatility (annualized standard deviation of daily returns over a trailing 3-month window) | WRDS (CRSP daily). Built by `MakeSIGMA.py` |
| `sp500.csv` | Monthly S&P 500 index value and return | WRDS (CRSP `msp500_v2`). Built by `MakeSP500.py` |

#### Other raw data
| File | Description | Source and how to obtain |
|---|---|---|
| `trace_29_04_2025_extract.parquet` | Corporate bond credit spreads (MMN-adjusted) and time to maturity, bond-month, August 2002 to March 2025 (columns `cusip_id`, `date`, `bond_maturity`, `CREDIT_SPREAD`) | Extract of the Dickerson, Robotti, and Rossetti TRACE dataset, 2025 vintage (file dated 29 April 2025), Open Source Bond Asset Pricing (openbondassetpricing.com). `code/python/MakeBondExtracts.py` documents how the extract is cut from the full file |
| `WRDS_MMN_2024_July_link.parquet` | Bond to firm link (`date`, `cusip`, `permno`) | Extract of the MMN-corrected bond data, July 2024 version, downloaded from openbondassetpricing.com. Cut by `code/python/MakeBondExtracts.py` |
| `drcoefficients2021.xlsx` | Default-risk (CDR) logit coefficients applied by `MakePROB.py` to compute the default probability | Originally from Jens Hilscher, shared by Kevin Aretz |
| `Moodys_US_defaults_quarterly.csv` | Quarterly number of U.S. corporate defaults, 1970Q1 to 2020Q1 (columns `quarter`, `defaults`); used in Figure OA.5 (`main_empirics.Rmd`) | Moody's (proprietary), extract dated 21 July 2020. Provided by Alexandre Jeanneret |

`trace_29_04_2025_extract.parquet` and `WRDS_MMN_2024_July_link.parquet` are extracts of the full files, cut by `code/python/MakeBondExtracts.py`. 

#### Derived data (constructed by the code in this package, without WRDS access)
| File | Description | Built by | Underlying source | In the package |
|---|---|---|---|---|
| `PROB.parquet` | Firm-month default probability (with its winsorized predictors), computed in-house from the coefficients in `drcoefficients2021.xlsx` | `MakePROB.py` | `raw_data.parquet`, `sigma.parquet`, `sp500.csv` | no, produced by the build |
| `PROB_agg.csv` | Equal- and value-weighted average of the firm default probability, monthly | `MakePROB.py` | `PROB.parquet` | yes |
| `CS.parquet` | Firm-month 5-year and 10-year credit spreads | `MakeCreditSpread.py` | The two bond extracts | no, produced by the build |
| `_main_data_2.parquet`, `_ret_quarterly_2.parquet` | Firm-quarter panel (levels and 1-quarter and 1-year changes, with the industry tag) and quarterly excess returns | `MakePortfolios_v2.py` | `raw_data.parquet`, `PROB.parquet`, `FF48_map.csv` | no, produced by the build |
| `industry_sorts.csv` | Value-weighted Fama–French 48 industry panel (the input to the correlation step) | `MakeSorts.py` | The two files above and `CS.parquet` | yes |
| `AggShocks/Agg_shocks.csv` | Quarterly aggregate macro and financial shocks | `MakeAggShocks_v1.py` | Public macro sources (below) | yes |
| `Estimates/`, `Estimates/length4/` | Correlation and block-bootstrap estimates that feed the tables | `Step2_MakeCorrelations_V4.R` | `industry_sorts.csv`, `Agg_shocks.csv` | yes |

#### Public data
These series were downloaded by hand from the websites below; no code is needed to obtain them.
"Retrieved" is the date of the download we used.

Public files in the package, read by `main_empirics.Rmd` (Figure OA.5) and
`Step2_MakeCorrelations_V4.R`:

| File | Content | Source | Retrieved | Coverage |
|---|---|---|---|---|
| `BAA10Y.csv` | Moody's Baa corporate bond yield minus the 10-year Treasury yield, daily | FRED, https://fred.stlouisfed.org/series/BAA10Y | 21 Oct 2025 | Jan 1986 to Oct 2025 |
| `BAMLC0A0CM.csv` | ICE BofA U.S. corporate index option-adjusted spread, daily | FRED, https://fred.stlouisfed.org/series/BAMLC0A0CM | 30 Sep 2025 | Dec 1996 to Sep 2025 |
| `Market_CMDI.xlsx` | Corporate Bond Market Distress Index, weekly | Federal Reserve Bank of New York, https://www.newyorkfed.org/research/policy/cmdi | 30 Sep 2025 | Jan 2005 to Sep 2025 |
| `FF48_industry.csv` | Fama–French 48 industry codes and short names; lookup table read by `Step2_MakeCorrelations_V4.R` | Kenneth French's data library, https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html | Feb 2024 | not dated |

Sources of the aggregate shocks in `AggShocks/Agg_shocks.csv`. The source files are in
`Data/AggShocks/` and are read by `MakeAggShocks_v1.py`, which builds `Agg_shocks.csv` from them:

| Variable in `Agg_shocks.csv` | Source file in `AggShocks/` | Source series | Source | Retrieved | Coverage |
|---|---|---|---|---|---|
| `IP`, `UNRATE`, `FEDFUNDS` | `INDPRO.csv`, `UNRATE.csv`, `FEDFUNDS.csv` | Industrial production index, unemployment rate, effective federal funds rate, monthly | FRED, https://fred.stlouisfed.org/series/INDPRO (and `/UNRATE`, `/FEDFUNDS`) | 2 Jul 2025 | Start of each series to mid-2025 |
| `DeltaLiq` | `liq_data_1962_2024.csv` | Aggregate liquidity innovations of Pastor and Stambaugh (2003), monthly | Lubos Pastor's website, https://faculty.chicagobooth.edu/lubos-pastor/data | 2 Jul 2025 | Aug 1962 to Dec 2024 |
| `CFNAI` | `cfnai-realtime-3-xlsx.xlsx` | Chicago Fed National Activity Index, real-time vintage of December 2024, monthly | Federal Reserve Bank of Chicago, https://www.chicagofed.org/research/data/cfnai/current-data | 2 Jul 2025 | Mar 1967 to Dec 2024 |
| `EPU` | `US_Policy_Uncertainty_Data.xlsx` | News-based U.S. economic policy uncertainty index of Baker, Bloom, and Davis, monthly | https://www.policyuncertainty.com/us_monthly.html | 2 Jul 2025 | Jan 1900 to Jun 2025 |
| `MacroU`, `RealU` | `MacroFinanceUncertainty_202506Update/` (`MacroUncertaintyToCirculate.xlsx`, `RealUncertaintyToCirculate.xlsx`; the folder also holds `FinancialUncertaintyToCirculate.xlsx`, which is read but not used) | Macroeconomic and real uncertainty indexes of Jurado, Ludvigson, and Ng (3-month horizon), monthly | Sydney Ludvigson's website, https://www.sydneyludvigson.com/macro-and-financial-uncertainty-indexes | June 2025 update | Jul 1960 to Apr 2025 |
| `NGDP` | `meanGrowth.xlsx` (sheet `NGDP`) | Survey of Professional Forecasters, mean forecast of nominal GDP growth, quarterly | Federal Reserve Bank of Philadelphia, https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/mean-forecasts | 2 Jul 2025 | 1968Q4 to 2025Q2 |
| `DeltaICR` | `HKM_Factors.csv` | Intermediary capital risk factor of He, Kelly, and Manela (2017), quarterly | Zhiguo He's website, https://zhiguohe.net/data-and-empirical-patterns/intermediary-capital-ratio-and-risk-factor/ | 3 Nov 2024 | 1970Q1 to 2024Q2 |

`Siccodes48.txt` (the SIC ranges that define the Fama–French 48 industries, Kenneth French's data
library, same page as above, retrieved 21 Sep 2026) is read by `MakeFF48.py` to build the industry
map.

### Access and licensing
CRSP, Compustat, IBES, TRACE, and Moody's data are subject to their license agreements. The
firm-level files pulled from WRDS (the frozen extracts) and the intermediate files derived from
them are not in the package; a fresh run regenerates them, and we provide the frozen vintage to
the journal's code and data editor on request, for the purpose of verifying the results, and not
for public redistribution. The bond extracts and the Moody's series are provided for the same
purpose.
Researchers with the relevant WRDS subscriptions can rebuild the WRDS extracts with the code in
`code/python/`. The bond data of Dickerson, Robotti, and Rossetti are distributed through
openbondassetpricing.com. Public series (FRED and authors' websites) are included under their terms.

## 3. Variable dictionaries
The data dictionaries are in `DATA_DICTIONARY.md`. For every dataset the code reads or writes under
`Data/` it lists the variables used in the paper, with the names used in the code and the files and
a one-line description. It has three parts:

1. **Analysis data**, read by the code that produces the exhibits: `industry_sorts.csv`,
   `AggShocks/Agg_shocks.csv`, `PROB_agg.csv`, the public series behind Figure OA.5, the estimate
   files in `Estimates/`, and the model solutions that `main.m` saves in `DataFile.mat`.
2. **Intermediate firm-level files** built by the Python code: `raw_data.parquet`, `sigma.parquet`,
   `sp500.csv`, `FF48_map.csv`, `PROB.parquet`, `CS.parquet`, `_ret_quarterly_2.parquet`,
   `_main_data_2.parquet`, and `iclink.pkl`.
3. **Third-party input files**: the bond extracts, the SIC ranges of the industries, the default
   probability coefficients, and the macroeconomic source files.

The definitions of the firm variables follow Table OA.3 of the Online Appendix.

## 4. Computational requirements

### Software
The runs reported in the paper and in `output/log/` were made on **macOS 26.5** (Tahoe, build 25F71)
on an Apple M5 Pro (arm64).

- **MATLAB R2026a** (version 26.1, Update 3) for the theory exhibits, with the **Statistics and
  Machine Learning Toolbox** 26.1 (`normrnd`, `unifrnd`, `prctile`) and the **Parallel Computing
  Toolbox** 26.1 (`parfor`; the code still runs without it, just serially). The code was developed
  and tested on R2026a. It uses the figure `theme` function, which older MATLAB releases do not have.
- **R 4.5.1**. The packages loaded by the code, with the versions we used:

  | Package | Version | Package | Version |
  |---|---|---|---|
  | tidyverse (dplyr 1.1.4, tidyr 1.3.2, purrr 1.2.0, ggplot2 4.0.1) | 2.0.0 | psych | 2.5.6 |
  | fixest | 0.13.2 | broom | 1.0.9 |
  | kableExtra | 1.4.0 | modelsummary | 2.5.0 |
  | rhdf5 (Bioconductor) | 2.52.1 | viridis | 0.6.5 |
  | zoo | 1.8-15 | ggforce | 0.5.0 |
  | readxl | 1.4.5 | ggrepel | 0.9.6 |
  | openxlsx | 4.2.8 | cowplot | 1.2.0 |
  | stringi | 1.8.7 | gt | 1.0.0 |
  | knitr | 1.50 | pander | 0.6.6 |
  | rmarkdown | 2.29 | renv | 1.2.3 |

  The block bootstrap also uses the `parallel` package, which is part of R. `renv.lock` records
  these versions together with the versions of all their dependencies (161 packages in total), and
  `renv::restore()` installs exactly those versions (see Environment setup below).
- **Python 3.11** (we used 3.11.15), only needed to rerun the data build (Section 5). The packages
  used by the code, with the versions we used:

  | Package | Version | Used for |
  |---|---|---|
  | pandas | 2.2.2 | data handling |
  | numpy | 1.26.4 | numerical routines |
  | pyarrow | 19.0.0 | reading and writing the `.parquet` files |
  | wrds | 3.2.0 | WRDS connection (CRSP, Compustat, IBES) |
  | openpyxl | 3.1.2 | reading the `.xlsx` files |
  | fuzzywuzzy | 0.18.0 | company name matching in `iclink.py` |
  | python-dateutil | 2.8.2 | date arithmetic |
  | tqdm | 4.66.4 | progress bars |
  | duckdb | 1.3.2 | only by `MakeBondExtracts.py`, to read the full TRACE file (not part of the build) |

  The same versions are pinned in `pyproject.toml`, `uv.lock`, and `requirements.txt`, and the
  setup commands below install exactly those versions. `run_all.py` itself uses only the Python
  standard library.
- **Pandoc ≥ 1.12.3** (we used 3.10), a system tool `rmarkdown` needs to knit the exhibits.
- A **WRDS account** with CRSP, Compustat, and I/B/E/S access, only to rerun the data build. The
  bond data are not pulled from WRDS; the extracts are in `Data/` (see Section 2).

### Environment setup (do this first)
A fresh clone ships the **lockfiles, not the packages**, so build the environment before running anything.

**R packages** (exact versions from `renv.lock`), from the package root:

    Rscript -e 'if (!requireNamespace("renv", quietly=TRUE)) install.packages("renv"); renv::restore()'

`renv::restore()` installs every package at its locked version into a project-local library, and warns
if your R version differs from the lock. When R starts in the package folder it may print
"The project is out-of-sync -- use `renv::status()` for details." This is expected and harmless:
`renv.lock` also records a few packages that the code does not load, and `renv` reports them. All
packages that the code loads are installed at their locked versions. (Quick alternative, *not* version-pinned: `Rscript install_R_packages.R`.)

**Pandoc** (required to knit the exhibits; command-line `Rscript` has no bundled pandoc):

    brew install pandoc          # macOS   (Linux: sudo apt-get install pandoc;  conda: conda install -c conda-forge pandoc)

Verify with `pandoc --version`. If R is already open, restart it (or
`Sys.setenv(RSTUDIO_PANDOC = dirname(Sys.which("pandoc")))`).

**Python** (`run_all.py` needs any Python 3.11 or later; the packages are needed only to rerun the
data build from WRDS):

    uv sync                                  # from pyproject.toml + uv.lock (exact versions)
    # or:  pip install -r requirements.txt
    # or:  conda env create -f environment.yml && conda activate egjl-replication

### Random seeds
The theory code fixes MATLAB's random number generator at the top of `main.m` with
`rng(0,'twister')`; the simulation block (`Simulation.m`) is its only source of randomness. The
block bootstrap in `Step2_MakeCorrelations_V4.R` uses seed = 123.

### Sample, key settings, and runtime
Sample: 1987-06-30 to 2023-12-31. Block bootstrap: block length 4 quarters, B = 1000, seed = 123.

**Approximate runtime** (MacBook Pro, Apple M5 Pro, 18 cores, 64 GB). The times are taken from the
log files in `output/log/`.

| Stage | Script | Runtime |
|---|---|---|
| Default run (`python run_all.py`): empirical exhibits from the shipped estimates, then the theory exhibits from a full solve | `run_all.py` | ~10 h, almost all of it MATLAB |
| Theory, default (`RECOMPUTE=true`): full solve + simulation | `code/matlab/main.m` | ~10 h (10 h 3 min); 18 cores for the PDE solves, the simulation phase is single-threaded |
| Theory from a saved `Data/DataFile.mat` (`--saved-model`, `RECOMPUTE=false`): tables and figures from the saved solutions | `code/matlab/main.m` | ~25 to 30 min |
| Empirics, default: knit exhibits | `master.R` (`main_empirics.Rmd`) | under a minute |
| Empirics Step 2: block bootstrap (B = 1000), `--bootstrap` | `Step2_MakeCorrelations_V4.R` | ~1 h (58 min; capped at 15 cores, hardcoded for reproducibility) |
| Empirics: data build from WRDS, `--wrds` | `Step1_PrepareAllData.py` | ~30 min (27 min), of which `MakeSIGMA.py` (CRSP daily returns) 19 min and `MakeMainDataFile_V1.py` 6 min; the other scripts take under 1 min each. Depends on the load of the WRDS server: an earlier run of the same build took 55 min |

The full solve saves its solutions to `Data/DataFile.mat` (~2 GB, not shipped because of its size).
A later run with `--saved-model` loads that file instead of re-solving, which skips the multi-hour
solve and simulation; it still computes the statistics of the tables from the simulated economies
and draws all figures, which took 26 minutes in our run.

Step 2 and the full Python rebuild are only needed to regenerate the estimates or the
firm/industry panels from scratch. Both depend on the number of cores and on the load of the WRDS
server, so the time can differ across machines and days.

## 5. Programs/Code

### The driver `run_all.py`
`run_all.py` runs the stages of the package in order, each as a subprocess, stops at the first
failure, and writes one log, `output/log/replication.log`, with the date, the options, the
software versions, and the console output of every stage. From the package root:

    python run_all.py                       # empirical exhibits from the shipped data, then the theory exhibits (~10 h, MATLAB)
    python run_all.py --no-matlab           # empirical part only (under a minute)
    python run_all.py --bootstrap           # also re-estimate the bootstrap standard errors first (~1 h more)
    python run_all.py --wrds --bootstrap    # also rebuild the empirical data from WRDS first (~30 min more; needs a WRDS account)
    python run_all.py --saved-model         # MATLAB reads Data/DataFile.mat saved by an earlier run instead of solving (~30 min)
    python run_all.py --matlab /Applications/MATLAB_R2026a.app/bin/matlab   # if matlab is not on the PATH

The options reach the stage scripts as environment variables (`EGJL_RUN_STEP2` for `master.R`,
`EGJL_RECOMPUTE` for `main.m`), so each stage can also be run on its own, as described below, and
then uses the same defaults (no bootstrap; full solve). On macOS `run_all.py` finds MATLAB in
`/Applications` by itself.

### Package root and paths
All code uses relative paths that point to files inside the package, so no path needs editing.
The paths are centralized in `config.py` and `config.R`, which must stay at the package root.

- **Python:** `config.py` derives the package root from its own location, so the scripts work from
  any working directory.
- **R:** `config.R` defines the paths relative to the package root, so R must be started from the
  package root. `master.R` checks this and stops with a message otherwise. `main_empirics.Rmd` also
  knits correctly when opened from `code/r/`.
- **MATLAB:** `main.m` finds its own folder and reads and writes relative to it, so it runs from any
  working directory.

### Theory component (MATLAB)
The model exhibits are produced by the MATLAB code in `code/matlab/` (author: Kristoffer Glover).
Per-function documentation is in `code/matlab/readme.txt`.

**Run:** open `code/matlab/main.m` in MATLAB and run it (it sets its own working directory, so the
helper functions resolve from any starting folder). Alternatively, run it from a terminal without
opening the MATLAB desktop:

    cd code/matlab
    matlab -batch "main"

(On macOS the `matlab` command is inside the application, for example
`/Applications/MATLAB_R2026a.app/bin/matlab`.) The script writes Tables 1–2, OA.1–OA.2, and OA.10
as `.tex` files to `output/tables/`, writes Figures 2–6 and OA.1–OA.4 (`.pdf`/`.eps`) to
`output/figures/`, and prints the asset-pricing moment values reported in Sections 2.1 and 3.3.
The console output is saved to `output/log/matlab_run.log`. Calibration parameters are those in
Sections 2.1, 3.3, and 2.6.

Two ways to run, set by the `RECOMPUTE` flag at the top of `main.m` (`run_all.py --saved-model` sets
it through the environment variable `EGJL_RECOMPUTE`):

- **Path A: solve the model (the default).** With `RECOMPUTE = true` (the default), `main.m` solves
  the model and runs the simulation (~10 h, see Section 4), saves the solutions to
  `Data/DataFile.mat` (~2 GB), then produces the exhibits. The package does not ship `DataFile.mat`.
- **Path B: read saved solutions (fast).** With `RECOMPUTE = false` (`run_all.py --saved-model`, or
  `EGJL_RECOMPUTE=false` in the environment), `main.m` loads the solutions from a `Data/DataFile.mat`
  saved by an earlier run and produces all theory exhibits without re-solving (~25 to 30 min). If
  the file is missing, `main.m` says so and solves the model instead.

All theory exhibits are produced by `code/matlab/main.m`.

| Paper exhibit | Output file |
|---|---|
| Table 1: default risk correlation and rollover risk | `output/tables/Table1_corr_by_maturity.tex` |
| Table 2: co-movement in default risk and equity moments from simulated economies | `output/tables/Table2_histograms.tex` |
| Figure 2: equilibrium asset pricing quantities | `output/figures/Fig2.eps` |
| Figure 3: optimal default policy in a two-tree economy | `output/figures/Fig3.eps` |
| Figure 4: excess default risk correlation by level of fundamental correlation | `output/figures/Fig4.pdf` |
| Figure 5: co-movement in default probabilities and in credit spreads | `output/figures/Fig5.pdf` |
| Figure 6: co-movement in equity volatility and in equity risk premium | `output/figures/Fig6.pdf` |
| Table OA.1: default risk correlation by borrower characteristics | `output/tables/TableOA1_by_characteristics.tex` |
| Table OA.2: co-movement in simulated economies, excluding defaults | `output/tables/TableOA2_histograms_nodefault.tex` |
| Table OA.10: sovereign debt spillover, case study | `output/tables/TableOA10_CPE_spillover.tex` |
| Figure OA.1: equilibrium asset pricing quantities, counterfactual | `output/figures/FigOA1.eps` |
| Figure OA.2: distribution of asset pricing moments across simulations | `output/figures/FigOA2.pdf` |
| Figure OA.3: distribution of default risk correlations, model vs. counterfactual case | `output/figures/FigOA3.pdf` |
| Figure OA.4: distribution of the correlations in asset pricing moments | `output/figures/FigOA4.pdf` |

The asset-pricing moment values reported in Sections 2.1 and 3.3 are printed to the MATLAB console
and recorded in `output/log/matlab_run.log`.

In the paper, Panel A of Figure 3 carries two arrows and the label "Distance-to-default". They are an
illustration added by hand and are not drawn by the code. `Fig3.eps` contains all plotted data of the
figure.

Key functions (full list in `code/matlab/readme.txt`): `TWOTREEY.m` (debt and equity value with the
optimal default boundary, via the PSOR finite-difference method), `CorrEst.m` (distance-to-default
correlation, Equation 11), `Simulation.m` and `DefaultTimes.m` (simulated economies and default
rates), `PROBDEF.m` (default probabilities under P and Q), and `CSpread.m` / `CPE1D.m` (equilibrium
credit spreads, Table OA.10).

`polyfix.m` (polynomial fit constrained to pass through given points, used by `Elasticity.m`) was
written by Are Mjaavatten (Telemark University College, version 1.3, 2019) and is included with its
original header.

### Empirics: reproducing the exhibits
The package ships the series the analysis reads, so **every empirical exhibit** is regenerated
without WRDS:

    Rscript master.R                          # or: python run_all.py --no-matlab

This knits `code/r/main_empirics.Rmd`, writing the tables to `output/tables/`, Figure OA.5 to
`output/figures/`, and an HTML report to `output/main_empirics.html`. It reads the shipped
`Data/Estimates/` directly. To recompute those bootstrap estimates first (from
`Data/industry_sorts.csv` + `Data/AggShocks/Agg_shocks.csv`; stationary block bootstrap,
~1 h, see Section 4), run `python run_all.py --bootstrap --no-matlab`, or set the environment
variable `EGJL_RUN_STEP2=TRUE` before `Rscript master.R`. `Step2_MakeCorrelations_V4.R` computes
the industry-pair correlations, the first-pass regressions that remove the part explained by
equity moments, firm fundamentals, and aggregate shocks, and the block-bootstrap standard errors;
`main_empirics.Rmd` turns the estimates into the tables and the figure.

### Empirics: how the data were prepared
The series in `Data/` were built from WRDS and from the bond data by the Python code in
`code/python/`. Running it is not needed to reproduce the exhibits; the code is included to
document how every variable is constructed, and `DATA_DICTIONARY.md` (Sections 2 and 3) lists
the variables of each file it reads and writes. The driver `Step1_PrepareAllData.py` runs the
scripts in this order:

| Script | What it does | Writes |
|---|---|---|
| `iclink.py` | Links CRSP to I/B/E/S by CUSIP, ticker, and company name (the WRDS ICLINK program of Qingyi (Freda) Song Drechsler, 2019, updated 2020, adapted to read the WRDS username from `config.py`) | `iclink.pkl` |
| `MakeFF48.py` | Gives every CRSP stock the SIC code of its last CRSP name record on or before 31 December 2023 and maps it to the Fama–French 48 industries with Kenneth French's SIC ranges (`Siccodes48.txt`); SIC 9999 is assigned to industry 48 (Other), other codes outside French's ranges are left unclassified | `FF48_map.csv` |
| `MakeMainDataFile_V1.py` | Pulls Compustat quarterly and annual fundamentals, CRSP monthly returns and prices with the risk-free rates, the CRSP–Compustat link, and I/B/E/S EPS forecasts; builds the firm-month panel with book equity, leverage, profitability, the one-quarter-ahead earnings forecast, and the default-probability predictors | `raw_data.parquet` |
| `MakeSIGMA.py` | Annualized volatility of daily CRSP returns over a trailing 3-month window at each month end | `sigma.parquet` |
| `MakeSP500.py` | Monthly S&P 500 index value and return | `sp500.csv` |
| `MakePROB.py` | Winsorizes the eight predictors at 5%/95% and applies the logit coefficients of `drcoefficients2021.xlsx` (Campbell, Hilscher, and Szilagyi, 2008) to obtain the firm-month default probability; aggregates it with equal and market-equity weights | `PROB.parquet`, `PROB_agg.csv` |
| `MakeCreditSpread.py` | Attaches the issuing firm to each bond and interpolates, for each firm and month, the credit spreads of its bonds with 3 to 7 (8 to 12) years to maturity to the 5-year (10-year) point | `CS.parquet` |
| `MakePortfolios_v2.py` | Merges the firm-month panel with the default probability, samples it at quarter ends, computes 1-quarter and 1-year changes, winsorizes them at 5%/95%, and tags each firm with its industry | `_main_data_2.parquet`, `_ret_quarterly_2.parquet` |
| `MakeSorts.py` | Averages every characteristic within industry and quarter, weighted by the firm's market equity at the end of the previous quarter, and adds the industry shares of market equity, EBITDA, and assets | `industry_sorts.csv` |
| `MakeAggShocks_v1.py` | Builds the quarterly aggregate shocks from the public series in `AggShocks/` | `AggShocks/Agg_shocks.csv` |

The first five scripts query WRDS and write the frozen extracts; the last five run from those
files. `MakeBondExtracts.py` is not part of the build: it documents how the two bond extracts
were cut from the full Open Source Bond Asset Pricing files.

The build can be rerun by a replicator with a WRDS subscription (CRSP, Compustat, I/B/E/S), from
the package root with the Python environment of Section 4 active:

    python run_all.py --wrds --bootstrap       # rebuild the data, then everything else
    python code/python/Step1_PrepareAllData.py # the data build alone (~30 min, see Section 4)

Before that, set `wrds_username` in `config.py` to your own and store your WRDS password in
`~/.pgpass` (`python -c "import wrds; wrds.Connection(wrds_username='your_username').create_pgpass_file()"`;
the build is non-interactive and stops at the first WRDS call otherwise). Every other input of the
build (the two bond extracts, `drcoefficients2021.xlsx`, `Siccodes48.txt`, and the source files in
`AggShocks/`) is in `Data/`. The build runs with the Python interpreter that
started it, so start it from the environment that has the packages installed (`uv run python ...`,
or activate the environment first). It writes `output/log/step1_build.log` and overwrites the
frozen extracts with the current WRDS vintage, so the results can differ slightly from the
published ones (see Data vintage in Section 2). With the frozen extracts obtained from us, the
last five scripts alone (about 2 minutes, no WRDS) reproduce the shipped `industry_sorts.csv`,
`PROB_agg.csv`, and `Agg_shocks.csv` exactly.

### Empirics: exhibit and output file
All empirical exhibits are produced by `code/r/main_empirics.Rmd` (run via `master.R`).

| Paper exhibit | Output file |
|---|---|
| Table 3: excess correlations across industries | `output/tables/Table3_Excess_Corr_Industries.tex` |
| Table OA.4: firm fundamentals (unrelated pairs) | `output/tables/TableOA4_Funda_Corr_Unrelated.tex` |
| Table OA.5: default risk & equity moments (unrelated pairs) | `output/tables/TableOA5_DefRisk_Equity_Corr_Unrelated.tex` |
| Table OA.6: firm fundamentals robustness | `output/tables/TableOA6_Funda_Corr_Unrelated_Robustness.tex` |
| Table OA.7: total & excess corr, unrelated, robustness | `output/tables/TableOA7_Total_Excess_Corr_Unrelated_Robustness.tex` |
| Table OA.8: total & excess corr, all industries, robustness | `output/tables/TableOA8_Total_Excess_Corr_All_Robustness.tex` |
| Table OA.9: size & book-leverage terciles | `output/tables/TableOA9_Excess_Corr_Size_BookLev_Terciles.tex` |
| Figure OA.5: PROB vs. fitted value | `output/figures/FigureOA5_PROB_fit.png` |

### Notes
- The pre-shipped `output/tables` and `output/figures` are the paper's exact exhibits; reproduction
  should overwrite them with identical content.
- The log files in `output/log/` record our runs: `step1_build.log` is the WRDS build of
  31 October 2026 that wrote the frozen extracts; `master_R.log` is the run of
  `master.R` with the bootstrap (`python run_all.py --bootstrap`) on the shipped data, which
  re-estimated the bootstrap standard errors and produced every empirical exhibit in `output/`;
  `matlab_run.log` is the full solve of 30 October 2026 (`RECOMPUTE = true`) that produced the
  theory exhibits. The default run (`python run_all.py`) repeats the full solve and reads the shipped
  bootstrap estimates, and reproduces the same exhibits.
- **Running the code overwrites these log files.** `main.m` replaces `matlab_run.log`, `master.R`
  replaces `master_R.log`, and `Step1_PrepareAllData.py` replaces `step1_build.log`, each with the
  log of the new run; `run_all.py` also writes `replication.log`, the console output of the whole
  run. To keep our logs for comparison, copy the folder `output/log/` before running.
- Contact: Kristoffer Glover (Kristoffer.Glover@uts.edu.au), Lucie Lu (lucie.lu@unimelb.edu.au).
