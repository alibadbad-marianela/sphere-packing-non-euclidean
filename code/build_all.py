"""build_all.py -- master script.  Runs validation tests, every experiment, all statistics,
all figures, and then builds the plan, paper, code listing, and data package.

Usage:  python3 build_all.py            (reuses cached runs if present)
        python3 build_all.py --rerun    (recomputes every run; takes about 17 minutes)
All random seeds are fixed (seeds 1-30 for evaluation, 9001-9004 for pilot tuning, 9101-9105 for unit tests), so a
rerun reproduces every value.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # folder that contains code/ and out/
STEPS = [
    ("unit tests", ["python3", "tests.py"], "unit_test_output.txt"),
    ("experiments", ["python3", "experiments.py"] + (["--rerun"] if "--rerun" in sys.argv else []), None),
    ("statistics", ["python3", "analyze.py"], None),
    ("supplementary analyses", ["python3", "supplementary.py"] + (["--rerun"] if "--rerun" in sys.argv else []), None),
    ("confirmatory round: environment", ["python3", "record_env.py"], None),
    ("confirmatory round: tuning", ["python3", "confirm_tune.py"], None),
    ("confirmatory round: runs", ["python3", "confirm_run.py"] + (["--rerun"] if "--rerun" in sys.argv else []), None),
    ("confirmatory round: count-based problem", ["python3", "confirm_count.py"], None),
    ("confirmatory round: analysis", ["python3", "confirm_analyze.py"], None),
    ("confirmatory round: saved configurations and wall metrics", ["python3", "confirm_configs.py"], None),
    ("confirmatory round: re-tuning (extended grids)", ["python3", "confirm_retune.py"], None),
    ("confirmatory round: re-tuned runs", ["python3", "confirm_run_retuned.py"], None),
    ("mini-round: runs", ["python3", "confirm_mini.py", "run"], None),
    ("mini-round: analysis", ["python3", "confirm_mini.py", "analyze"], None),
    ("follow-up: runs", ["python3", "confirm_followup.py", "run"], None),
    ("follow-up: L-BFGS-B on the mini-round conditions", ["python3", "confirm_followup.py", "run_mini_lbfgsb"], None),
    ("follow-up: analysis", ["python3", "confirm_followup.py", "analyze"], None),
    ("final round: part A runs", ["python3", "confirm_round3.py", "runA"], None),
    ("final round: part B runs", ["python3", "confirm_round3.py", "runB"], None),
    ("final round: analysis", ["python3", "confirm_round3.py", "analyze"], None),
    ("confirmatory round: additional analyses", ["python3", "confirm_extra.py"], None),
    ("figures", ["python3", "make_figures.py"], None),
    ("research paper", ["python3", "make_paper.py"], None),
    ("code listing", ["python3", "make_code_listing.py"], None),
    ("data package", ["python3", "make_package.py"], None),
    ("final checks", ["python3", "checks.py"], None),
]

if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "out", "data"), exist_ok=True)
    for name, cmd, log in STEPS:
        print("== " + name, flush=True)
        if log:
            with open(os.path.join(ROOT, "out", log), "w") as fh:
                r = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT)
        else:
            r = subprocess.run(cmd)
        if r.returncode != 0:
            sys.exit("step failed: " + name)
    print("all steps finished")
