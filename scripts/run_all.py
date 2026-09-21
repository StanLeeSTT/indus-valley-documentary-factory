import argparse,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.pipeline import STEPS
p=argparse.ArgumentParser(); p.add_argument("--from-cell",type=int,default=1); p.add_argument("--to-cell",type=int,default=27); a=p.parse_args()
for i in range(a.from_cell,a.to_cell+1):
    print(f"\n===== CELL {i} =====")
    print(STEPS[i]())
print("\nPIPELINE COMPLETE")
