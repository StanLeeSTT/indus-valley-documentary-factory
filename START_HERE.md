# Start Here

1. Add the ZIP to Kaggle with **Add Data -> Upload**.
2. Run `scripts/kaggle_bootstrap.py` (or paste its contents into a Kaggle Python cell).
3. It installs dependencies, initializes Git, creates the first Git checkpoint, pushes to GitHub, then runs Cells 1-27.
4. For the first build, it is safer to comment out the final `run_all.py` line and execute one cell at a time using `scripts/run_cell.py 1`, `scripts/run_cell.py 2`, etc.
5. After each cell, verify the checkpoint and confirm the Git push.
