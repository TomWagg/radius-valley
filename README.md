<h1 align="center">Exploring the planetary radius valley through the lens of multi-transiting systems</h1>
<p align="center">Fitting an exoplanet can be hard, fitting multiple can be harder, but can we leverage planetary multiplicity to better constrain our models for the radius valley?<br>
In many cases there are degeneracies when fitting a system with a single exoplanet, but with multiple planets we can break these degeneracies since they are all orbiting the same star and must be simultaneously fit.</p>

## How to run this code
First you'll need to get the code locally. Go to the directory where you want to put it and clone the repository with
```
  git clone https://github.com/TomWagg/radius-valley.git
  cd radius-valley
```
Now we need to get the right packages installed. Assuming that you have conda installed you need to do the following
```
  conda env create --file environment.yml
```
This may take a little time to solve the environment but will install everything that you need. Once it finishes you can enter the new environment with
```
  conda activate radius-valley
```
After this it's just a matter of getting the Jupyter server going and trying out the notebooks!

## A (very) brief tour
`notes/` contains any notes I keep on project planning, `helpers/` contains the helper functions I made for fitting these systems and `notebooks/` is where I test out the code and try to fit systems.
