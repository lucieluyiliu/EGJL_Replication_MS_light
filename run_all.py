#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created:       2026-09-29
Last modified: 2026-09-29
Author:        Lucie Lu <lucie.lu@unimelb.edu.au>

Single driver for the EGJL "Excess Co-movement in Default Risk" replication package.
Runs the three stages in order, each as a subprocess, and writes one timestamped log,
output/log/replication.log, that contains the console output of every stage (the
stages also keep their own logs in output/log/). Stops at the first stage that fails.

    python run_all.py [--wrds] [--bootstrap] [--saved-model] [--no-matlab] [--matlab PATH]

Stages and options (defaults reproduce every exhibit from the shipped data):
  1. Python data build (code/python/Step1_PrepareAllData.py). Only with --wrds:
     needs a WRDS account (see config.py) and rebuilds Data/ from WRDS, ~30 min.
  2. R: Rscript master.R. Knits the empirical exhibits (Table 3, Tables OA.4-OA.9,
     Figure OA.5) from Data/. With --bootstrap it first re-estimates the correlations
     and bootstrap standard errors in Data/Estimates/ (~1 h).
  3. MATLAB: main.m in code/matlab (Tables 1-2, OA.1-OA.2, OA.10, Figures 2-6,
     OA.1-OA.4). It solves the model from scratch (~10 h) and saves the solutions to
     Data/DataFile.mat; with --saved-model it reads that file from an earlier run
     instead (~30 min; if the file is missing it solves anyway).
     --no-matlab skips the stage; --matlab gives the MATLAB executable if it is not
     on the PATH (on macOS it is /Applications/MATLAB_<release>.app/bin/matlab).

The flags reach the stage scripts as environment variables (EGJL_RUN_STEP2 for
master.R, EGJL_RECOMPUTE for main.m); running those scripts by hand without the
variables set gives the same defaults.
"""

import argparse
import glob
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime

# Package root = the directory that contains this file (relative paths, MNSC item 13).
root = os.path.dirname(os.path.abspath(__file__))
os.chdir(root)

parser = argparse.ArgumentParser(description='Run the EGJL replication package end to end.')
parser.add_argument('--wrds', action='store_true', help='rebuild Data/ from WRDS (stage 1)')
parser.add_argument('--bootstrap', action='store_true', help='re-estimate Data/Estimates/ (R Step 2)')
parser.add_argument('--saved-model', action='store_true',
                    help='MATLAB reads Data/DataFile.mat from an earlier run instead of solving the model')
parser.add_argument('--no-matlab', action='store_true', help='skip the MATLAB stage')
parser.add_argument('--matlab', default=None, help='path to the MATLAB executable')
args = parser.parse_args()


def find_matlab(explicit):
    """The MATLAB executable: --matlab, then the PATH, then the macOS application folder."""
    if explicit:
        return explicit
    on_path = shutil.which('matlab')
    if on_path:
        return on_path
    apps = sorted(glob.glob('/Applications/MATLAB_R*.app/bin/matlab'))
    return apps[-1] if apps else None


def version_of(cmd):
    """First line printed by `cmd`, or the error if it cannot run."""
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        text = (out.stdout or out.stderr).strip().splitlines()
        return text[0] if text else '(no output)'
    except Exception as e:                       # not installed, not on the PATH, ...
        return f'not available ({e})'


# ---- Stages: (name, command, working directory, extra environment) --------------
env = dict(os.environ,
           EGJL_RUN_STEP2='TRUE' if args.bootstrap else 'FALSE',
           EGJL_RECOMPUTE='false' if args.saved_model else 'true')

stages = []
if args.wrds:
    stages.append(('Python data build (Step1_PrepareAllData.py)',
                   [sys.executable, os.path.join('code', 'python', 'Step1_PrepareAllData.py')], root))
stages.append(('R correlations and exhibits (master.R)', ['Rscript', 'master.R'], root))
matlab = None
if not args.no_matlab:
    matlab = find_matlab(args.matlab)
    if matlab is None:
        sys.exit('MATLAB not found: give its path with --matlab, or skip the stage with --no-matlab.')
    stages.append(('MATLAB theory exhibits (main.m)', [matlab, '-batch', 'main'],
                   os.path.join(root, 'code', 'matlab')))

# ---- One log for the whole run --------------------------------------------------
log_dir = os.path.join('output', 'log')
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'replication.log')

with open(log_path, 'w') as log:
    def tee(text):
        sys.stdout.write(text)
        sys.stdout.flush()
        log.write(text)
        log.flush()

    t_run = datetime.now()
    tee(f"EGJL replication run started {t_run:%Y-%m-%d %H:%M:%S}\n")
    tee(f"Package root : {root}\n")
    tee(f"Command      : {' '.join(sys.argv)}\n")
    tee(f"Flags        : wrds={args.wrds} bootstrap={args.bootstrap} saved_model={args.saved_model} "
        f"matlab={'skipped' if args.no_matlab else matlab}\n")
    tee(f"Platform     : {platform.platform()} ({platform.machine()})\n")
    tee(f"Python       : {sys.version.split()[0]} ({sys.executable})\n")
    tee(f"R            : {version_of(['Rscript', '--version'])}\n")
    if matlab:
        tee(f"MATLAB       : {matlab}\n")
    tee(f"Stages       : {len(stages)} ({', '.join(name.split(' (')[0] for name, _, _ in stages)})\n")

    for name, cmd, cwd in stages:
        t0 = datetime.now()
        tee(f"\n{'=' * 78}\n=== {name}\n=== started {t0:%Y-%m-%d %H:%M:%S}   command: {' '.join(cmd)}\n{'=' * 78}\n")
        try:
            proc = subprocess.Popen(cmd, cwd=cwd, env=env,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        except FileNotFoundError as e:
            tee(f"Cannot start the stage: {e}. Stopping.\n")
            break
        for line in proc.stdout:
            tee(line)
        proc.wait()
        minutes = (datetime.now() - t0).total_seconds() / 60
        if proc.returncode != 0:
            tee(f"\n=== {name} FAILED (exit {proc.returncode}) after {minutes:.1f} min. Stopping.\n")
            break
        tee(f"\n=== {name} done in {minutes:.1f} min\n")
    else:
        tee(f"\nAll stages done. Tables -> output/tables/, figures -> output/figures/\n")

    tee(f"\nEGJL replication run ended {datetime.now():%Y-%m-%d %H:%M:%S} "
        f"(total {(datetime.now() - t_run).total_seconds() / 3600:.2f} h)\n")
