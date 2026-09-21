import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.pipeline import STEPS
cell=int(sys.argv[1])
print(STEPS[cell]())
