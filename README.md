- Python 3.5 (or above) is required to run this program.
- Ensure that pip3 is installed with `sudo apt install python3-pip`
- Install required packages with `pip3 install -r ./requirements.txt`
- Usage instructions (also provided with `python3 ./main.py -h`):

    - `python3 ./main.py filename` to visualise the contents of `filename`.
    - `-d [graph|text|both]` to specify graphical output, textual output, or both. Default is 'both'.
    - `-w [num]` to specify the width of the graphical display in as 'num' columns. Default is 80.
    - `-s filename` to specify a `system.xml` to use for server information in cases where it would be
    impossible to gain server information from just the logs. Such cases may occur when using scheduling
    algorithms such as 'AllToLargest' where it is unnecessary for the client to request server information.
    This option is also required for when server logs are produced without using the `-v all` option.
    
- The graphical output shows each server core as a line. A job starts its execution at the point specified
by its ID, prefixed with 'j'. The execution time of a job is represented by forward slashes ('/'), a job
completes at the last forward slash.
