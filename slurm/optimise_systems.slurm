#!/bin/bash
## Job Name
#SBATCH --job-name=radius-valley-optimise-systems
#SBATCH --account=astro
#SBATCH --partition=ckpt
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=28
#SBATCH --time=6:00:00
#SBATCH --mem=100G
#SBATCH -o /gscratch/astro/wagg/radius-valley/slurm/logs/opt_logs%a_%A.out
#SBATCH -e /gscratch/astro/wagg/radius-valley/slurm/logs/opt_logs%a_%A.err
#SBATCH --chdir=/gscratch/astro/wagg/radius-valley/slurm
#SBATCH --mail-type=ALL
#SBATCH --mail-user=TODO
#SBATCH --export=all

source ~/.bashrc
conda activate    # path to conda environment (something like /gscratch/astro/wagg/conda_envs/radius_valley)

SCRIPT_PATH=/gscratch/astro/wagg/radius-valley/slurm/optimise_system.py
OUTPUT_PATH=/gscratch/astro/wagg/radius-valley/slurm/output/

python $SCRIPT_PATH -s $SLURM_TASK_ID -o $OUTPUT_PATH
