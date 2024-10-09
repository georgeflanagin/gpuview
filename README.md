# gpuview

This is a command line utility aimed at high performance computing clusters where the nodes have
a number of GPUs. The purpose is to use a full screen text mode presentation to show the use at
a glance.

## Use

### Requirements

`gpuview` makes use of the code library from University of Richmond named
`hpclib`. It is available at https://github.com/georgeflanagin/hpclib and
a number of other locations. Python 3.11 is the minimum required version.

### The configuration file.

`gpuview` will attempt to read the contents of a TOML file named
gpuview.toml that is in the same directory with the program, itself. The
primary data in the TOML file is a list of the hosts where the program
is to collect the data. `gpuview` can be used on localhost, but there
are many ways to get GPU use statistics for the local computer.

Currently, the TOML file supports these entries:

`block_x_dim` -- the width of each block that displays data about a host.

`block_y_dim` -- the height of the block that displays data about a host.

`hosts` -- a list of hostnames to query.

`keepers` -- a list of properties that this program finds interesting,
and that this program will display.

`outfile` -- name of the disk file where the queries will be recorded
for analysis. This is a temporary file that is locked and written to by each child
process that collects data from a host.

`toolname` -- the command and options that are used to retrieve the
data from the hosts.

`x_offset` -- how far over from the left edge to start the first block.

`y_offset` -- how far below the top of the screen to start the first 
row of blocks.

### Command line options

`--loglevel` -- Any of the standard Python logging levels work. The
default is `logging.INFO`.

`--num-readings` -- number of observations to make. The default is
`sys.maxsize`, which is to say, "a lot."

`--output {filename}` -- redirects `stdout` to the named file.

`--time` -- the number of seconds to wait between each query.

`--zap` -- remove old records from `gpuview.log` before writing the
first new logfile record.

### Running gpuview

```bash
`gpuview`
```
