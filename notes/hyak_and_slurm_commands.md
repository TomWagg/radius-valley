# Hyak and SLURM cheatsheet

I figured this was a more permanent and findable location than some random message in Slack!

## Things for your `~/.bashrc`

These are some shortcuts and style things that you _could_ add to your bashrc if you so desire. Quick reminder that bashrc files are basically what gets run every time you open a new terminal so anything you can write in a terminal you can also write in this file.

### For your local laptop

Make your prompt a little prettier and more functional. You can [learn more about how to change this here](https://www.cyberciti.biz/faq/bash-shell-change-the-color-of-my-shell-prompt-under-linux-or-unix/). You could definitely put this in your file on hyak too.
```bash
export PS1="\[\e[31m\][\[\e[m\]\[\e[38;5;172m\]\u\[\e[m\]@\[\e[38;5;153m\]\h\[\e[m\] \[\e[38;5;214m\]\W\[\e[m\]\[\e[31m\]]\[\e[m\]\\$ "
```

Quickly ssh into hyak without typing a bunch
```bash
alias hyak="ssh YOURNAME@mox.hyak.uw.edu"
```

### For hyak

You can define this nifty little function for tracking jobs whilst they are on the go.
```bash
jobstats() {
   sacct -j ${1}.batch -o "JobID, State, Elapsed, MaxRSS" --units=G
}
```
You then run this in your terminal as
```bash
jobstats JOB_ID
```

## SLURM commands

DON'T EVER RUN ANY INTENSIVE CODE ON THE FIRST NODE YOU LOGIN ON. (Sorry for shouting, but the IT people will shout at you if you do it so )

### Interactive nodes

So if you do want to run some quick python script without creating an asynchronous job you can instead create an interactive node with something like
```bash
srun -p astro -A astro --nodes=1 --ntasks-per-node=4 --time=2:00:00 --mem=100G --pty /bin/bash
```
Where this gives you 4 cores on an astro node with 100Gb of memory for 2 hours. Alternatively if you want a build node something like this would do
```bash
srun -p build --time=2:00:00 --mem=20G --pty /bin/bash
```
Learn more about these [here](https://wiki.cac.washington.edu/display/hyakusers/Mox_scheduler).

### Running jobs

The main way we'll be running jobs is using `sbatch`. You can do this like
```bash
sbatch --array=1-5 SOMEFILE.slurm
```
where that array can be a range like above or a comma-separated list. These get passed to the script and are accessed with `$SLURM_TASK_ID` in the file. In our case these numbers refer to rows in the input file.

Once you run that command you'll get some output about how the job has been queued with some ID. You can check in on this job with this (as long as you added it to your bashrc, see above)
```bash
jobstats JOB_ID
```

If you ever need to cancel a job you submitted by accident or something that's just
```bash
scancel JOB_ID
```

## Miscellaneous

Don't forget you can activate our shared conda environment by running:
```bash
conda activate /gscratch/astro/wagg/radius-valley/conda_env
```
You could also create an alias in your hyak bashrc for this if you fancy.