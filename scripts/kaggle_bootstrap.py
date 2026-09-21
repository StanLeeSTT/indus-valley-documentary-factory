# Run from Kaggle after adding the project ZIP as notebook data.
from pathlib import Path
import glob,zipfile,shutil,subprocess,sys,os
REPO=Path('/kaggle/working/indus-valley-documentary-factory')
files=glob.glob('/kaggle/input/**/*.zip',recursive=True)
files=[x for x in files if 'indus-valley-documentary-factory-v1' in Path(x).name]
if not files: raise FileNotFoundError('Add indus-valley-documentary-factory-v1.zip to the notebook with Add Data -> Upload.')
if REPO.exists(): shutil.rmtree(REPO)
REPO.mkdir(parents=True)
with zipfile.ZipFile(files[0]) as z: z.extractall(REPO)
subprocess.run([sys.executable,'-m','pip','install','-q','-r',str(REPO/'requirements.txt')],check=True)
subprocess.run(['git','init'],cwd=REPO,check=True); subprocess.run(['git','branch','-M','main'],cwd=REPO,check=True); subprocess.run(['git','remote','add','origin','https://github.com/StanLeeSTT/indus-valley-documentary-factory.git'],cwd=REPO,check=True)
subprocess.run(['git','add','.'],cwd=REPO,check=True); subprocess.run(['git','commit','-m','Initialize fresh Indus Valley documentary factory'],cwd=REPO,check=True)
push=subprocess.run(['git','push','-u','origin','main'],cwd=REPO,text=True)
if push.returncode!=0: raise SystemExit('GitHub push failed. Configure Kaggle GitHub authentication, then run: git push -u origin main')
print('Source checkpoint pushed to GitHub.')
subprocess.run([sys.executable,str(REPO/'scripts/run_all.py'),'--from-cell','1','--to-cell','27'],check=True)
