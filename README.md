# cs_jiffies
A personal respository for short scripts to do things in CryoSPARC

# Usage:
## Dependencies:
* cryosparc-tools
* jupyter notebook
* python-dotenv

## Install:

```
conda create -n cs_jiffies python=3.11
conda activate cs_jiffies
pip install -r requirements.txt
```

Create a `.env` in the repository's directory for the constants
```
cs_license = 'asdf1348-replace-me-123lkj12'
cs_hostname = 'mycryosparcinstance.mysupercoolinstitution.com'
cs_port = 39000
```

## Instructions:
For Jupyter Notebooks files (files ending in `.ipnyb`, in a Python environment with cryosparc-tools and Jupyter Notebooks installed, open a new Jupyter notebook instance with `jupyter notebook`. Load the `.ipnyb` file in the Jupyter notebook, and follow the prompts from top to bottom.

For Python scripts (files ending in `.py`), typically make sure you have cryosparc-tools available (if using conda, load the conda environment)
```
python cs_mdoc_image_shift.py -h
usage: cs_mdoc_image_shift.py [-h] [--email EMAIL] [--project PROJECT] [--workspace WORKSPACE] [--job JOB] [--mdoc_dir MDOC_DIR] [--recursive]

options:
  -h, --help            show this help message and exit
  --email EMAIL, -e EMAIL
                        Email or account used in cryosparc
  --project PROJECT, -p PROJECT
                        Cryosparc project. i.e. P83
  --workspace WORKSPACE, -w WORKSPACE
                        Workspace number, i.e. W1
  --job JOB, -j JOB     Input job number, i.e. J56
  --mdoc_dir MDOC_DIR, -d MDOC_DIR
                        Directory where the exposures mdoc files are located
  --recursive, -r       Whether to look for the mdoc file recursively from the mdoc_dir.
```

You will need to be on a filesystem that has access to the data at the same path as CryoSPARC.
