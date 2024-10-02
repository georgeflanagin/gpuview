# gpuview

This is a command line utility aimed at high performance computing clusters where the nodes have
a number of GPUs. The purpose is to use a full screen text mode presentation to show the use at
a glance.

## Use

### Requirements

`gpuview` makes use of the code library from University of Richmond named `hpclib`. It is available
at https://github.com/georgeflanagin/hpclib and a number of other locations. Python 3.11 is the 
minimum required version.

### The configuration file. 

`gpuview` will attempt to read the contents of a TOML file named gpuview.toml that is in the
same directory with the program, itself. The primary data in the TOML file is a list of the
hosts where the program is to collect the data. `gpuview` can be used on localhost, but there
are many ways to get GPU use statistics for the local computer. 

### Command line options

`--test {hostname}` -- this option supersedes all others, and executes the core code to gather
data exactly once, prints the result to `stdout`, and then terminates.

`-o {filename}` -- redirects `stdout` to the named file. 

`--zap` -- remove old records from `gpuview.log` before writing the first new logfile record.

`

### Running gpuview

```bash
```
