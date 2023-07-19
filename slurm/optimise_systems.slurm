#!/bin/bash
## Job Name
#SBATCH --job-name=radius-valley-optimise-systems
#SBATCH --account=astro
#SBATCH --partition=astro
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --time=1:00:00
#SBATCH --mem=100G
#SBATCH -o /gscratch/astro/wagg/radius-valley/slurm/logs/opt_logs%a_%A.out
#SBATCH -e /gscratch/astro/wagg/radius-valley/slurm/logs/opt_logs%a_%A.err
#SBATCH --chdir=/gscratch/astro/wagg/radius-valley/slurm
#SBATCH --mail-type=ALL
#SBATCH --mail-user=tomwagg@uw.edu          <--- CHANGE THIS TO YOUR EMAIL!!!
#SBATCH --export=all

# we probably only need one of these two lines, may need to delete one eventually?
source ~/.bashrc
module load anaconda3_5.3

conda activate /gscratch/astro/wagg/radius-valley/conda_env

SCRIPT_PATH=/gscratch/astro/wagg/radius-valley/slurm/optimise_system.py
OUTPUT_PATH=/gscratch/astro/wagg/radius-valley/slurm/output/

python $SCRIPT_PATH -s $SLURM_TASK_ID -o $OUTPUT_PATH
