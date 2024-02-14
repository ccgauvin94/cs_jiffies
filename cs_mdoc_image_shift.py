from pathlib import Path
import re
import sys
from cryosparc.tools import CryoSPARC
from getpass import getpass
from dotenv import dotenv_values
import argparse
from typing import Iterable, Dict, List
import numpy as np



##### Instructions #####
# Place a copy of this file in each directory you have .mdoc
# files in, load the cryosparc-tools conda environment (if using)
# and run this script: python3 cs_mdoc_image_shift.py

##### Variables #####
CONFIG = dotenv_values(".env")
CS_JOB_OUTPUT_TYPE = 'all_exposures'


def parser(args:List) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--email','-e',type=str, help="Email or account used in cryosparc")
    parser.add_argument('--project', '-p',type=str, help='Cryosparc project. i.e. P83')
    parser.add_argument('--workspace','-w',type=str, help='Workspace number, i.e. W1')
    parser.add_argument('--job','-j',type=str,help='Input job number, i.e. J56')
    parser.add_argument('--mdoc_dir','-d',type=str, help='Directory where the exposures mdoc files are located')
    parser.add_argument('--recursive', '-r', action='store_true', default=False, help="Whether to look for the mdoc file recursively from the mdoc_dir.")
    args =  parser.parse_args(args)
    if any([args.email is None, args.project is None, args.job is None, args.workspace is None]):
        parser.print_help()
        sys.exit(1)
    return args


def recursively_find_mdoc(mdoc_dir:Path, filename:'str') -> Iterable:
    ##### (il)Logic #####
    #Set directory and get list of mdocs
    mdoc_directory = Path(mdoc_dir)
    if not mdoc_dir.exists():
        raise NotADirectoryError(f'Directory {mdoc_dir} does not exist.')
    
    mdoc_list = mdoc_directory.glob(f'**/{filename}')
    return next(mdoc_list)

#Iterate through list of mdoc files
def parse_mdoc(mdoc_file:Path) -> Dict:
    #Open individual mdoc file
    mdoc = mdoc_file.read_text()
    pattern = r"ImageShift = (-?\d+\.\d+)\s+(-?\d+\.\d+)"
    matches = re.findall(pattern, mdoc)
    if matches:
        return np.array(matches[0]).astype(float)
                

def get_exposures_from_job(project:str,job) -> np.ndarray:
    cs_project = cs.find_project(project)
    cs_job = cs.find_job(project,job)
    cs_exposures = cs_job.load_output(CS_JOB_OUTPUT_TYPE)
    return cs_project, cs_job, cs_exposures.copy()    


def progress(i,total,interval=2):
    completion = round(i/total*100)
    if completion % interval == 0:
        print(f'{completion}% completed. {i}/{total}', end='\r')

if __name__ == "__main__":
    
    args = parser(sys.argv[1:])
    cs_password = getpass("Please enter CryoSPARC password: ")
    #Connect to CS
    cs = CryoSPARC(license=CONFIG['cs_license'], email=args.email, password=cs_password, host=CONFIG['cs_hostname'], base_port=int(CONFIG['cs_port']))
    assert cs.test_connection(), "Connection to cryosparc failed"

    #Find dataset and copy it to a new dataset
    cs_project, cs_job, grouped_exposures = get_exposures_from_job(args.project,args.job)
    #For every row in the dataset, search entire mdoc data and see if it fits a known movie and image shift. There's probably a much faster way to do this.
    total = len(grouped_exposures)
    for ind,row in enumerate(grouped_exposures.rows()):
        exposure = row['movie_blob/path'].rsplit(sep='/')[-1]
        mdocfile = Path(args.mdoc_dir,exposure+'.mdoc')
        if args.recursive:
            mdocfile = recursively_find_mdoc(Path(args.mdoc_dir),filename=exposure+'.mdoc')  
        mdoc = parse_mdoc(mdocfile)
        # if exposures[i]['exposure'] == row['movie_blob/path'].rsplit(sep='/')[-1]:
        row['mscope_params/beam_shift'] = mdoc
        row['mscope_params/beam_shift_known'] = 1
        progress(ind,total)

    #Make a new external job with the updated values, and passthrough the remaining, non-updated values
    cs_project.save_external_result(
        workspace_uid=args.workspace,
        dataset=grouped_exposures,
        type="exposure",
        name="exposure",
        slots=["mscope_params"],
        passthrough=(args.job,CS_JOB_OUTPUT_TYPE),
        title="ImageShift Updated Exposures"
        )
