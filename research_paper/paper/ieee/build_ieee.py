"""Compile both manuscript PDFs with Tectonic; retain original manuscript files."""
import argparse
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tectonic',default=shutil.which('tectonic'))
    args=parser.parse_args()
    if not args.tectonic:
        parser.error('Install Tectonic or pass --tectonic /absolute/path/to/tectonic')
    output=REPO/'output/pdf/ieee_20261023'
    output.mkdir(parents=True,exist_ok=True)
    for name in ['recovery_transfer_ieee','recovery_transfer_supplement']:
        subprocess.run([args.tectonic,'--keep-logs','--outdir',str(output),str(HERE/(name+'.tex'))],cwd=REPO,check=True)
        print(output/(name+'.pdf'))

if __name__=='__main__':main()
