```text
___ _ __   _____  ____  ___   _ 
/ __| '_ \ / _ \ \/ /\ \/ / | | |
\__ \ |_) |  __/>  <  >  <| |_| |
|___/ .__/ \___/_/\_\/_/\_\\__, |
    | |     A spectrum      __/ |
    |_| fitting framework  |___/ 
```

*spexxy* is a framework for the analysis of astronomical spectra. It provides both two executables
that wrap the framework using a YAML configuration file and provide some additional command line
tools, respectively.


### Documentation

You can find the documentation for spexxy at <https://spexxy.readthedocs.io/>.


### Build status

| master  | develop |
| --- | --- |
| ![master build status](https://api.travis-ci.com/thusser/spexxy.svg?branch=master) | ![develop build status](https://api.travis-ci.com/thusser/spexxy.svg?branch=develop) |


### References

*spexxy* requires Python 3.6 or later and depends on a couple of amazing external packages:

* [Astropy](http://www.astropy.org/) is used for handling FITS file, times and coordinates, and other
  astronomical calculations.
* [LMFIT](https://lmfit.github.io/lmfit-py/) is a central part of *spexxy*, for it handles the main
  optimization routines.
* [NumPy](http://www.numpy.org/) is mainly used for array handling.
* [pandas](https://pandas.pydata.org/) provides easy access to CSV files and allows for easy table
  handling.
* [PyYAML](https://pyyaml.org/) adds support for YAML configuration files.
* [SciPy](https://www.scipy.org/) is used for optimization, interpolation, and integration at several
  places.

Thanks to everyone putting time and efforts into these (and other!) open source projects!
