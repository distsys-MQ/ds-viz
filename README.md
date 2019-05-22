- Python 3.5 (or above) is required to run this program.
- Ensure that pip3 is installed with `sudo apt install python3-pip`
- Install required packages with `pip3 install -r ./requirements.txt`
- Create a server log file by redirecting the server output to a file. For example, start the server with
`./ds-server -c config_simple1.xml -v all > serverOut.log` and run your client. The output from the server
will be saved in `serverOut.log` which can then be visualised by using this program.
- Usage instructions (also provided with `python3 ./main.py -h`):

    - `python3 ./main.py filename` to visualise the contents of a server log file named `filename`.
    - `-d [graph|text|both]` to specify graphical output, textual output, or both. Default is 'both'.
    - `-w [num]` to specify the width of the graphical display in as 'num' columns. Default is 80.
    - `-s filename` to specify a `system.xml` to use for server information in cases where it would be
    impossible to gain server information from just the logs. Such cases may occur when using scheduling
    algorithms such as 'AllToLargest' where it is unnecessary for the client to request server information.
    This option is also required for when server logs are produced without using the `-v all` option.
    
- The following example will produce a visualisation of the server log saved in `serverOut.log`, using the
system information from `system.xml`. It will only create a graphical view with a width set to 100 columns.

    `python3 ./main.py ./serverOut.log -s ./system.xml -d graph -w 100`

- The graphical output shows each server core as a line. A job starts its execution at the point specified
by its ID, prefixed with 'j'. The execution time of a job is represented by forward slashes ('/'), a job
completes at the last forward slash.
