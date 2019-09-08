- Python 3.5 (or above) is required to run this program.
- Ensure that python3, pip3, and tkinter are installed with `sudo apt install python3 python3-tk python3-pip`
- Install required packages with `python3 -m pip install --user -r requirements.txt`
- Generate resource failure and log files with a particular configuration file
- Usage instructions (also provided with `python3 ./sim-viz.py -h`):
    - `python3 ./sim_viz.py config log` to visualise the contents of a simulation that used the
    config file `config` which had produced the log file named `log`.
    - `-f failures` to visualise failures from a resource failures file `failures`
    - `-c num` to specify the height of server cores to `num` pixels. Default is 4.
    - `-s num` to specify the initial scaling factor to `num`. Default is 0. The scaling factor will determine
    the maximum number of cores to display per server, represented as an exponent of 2. E.g. a scale factor of 3
    will display at most 8 cores per server.
- The following example will produce a visualisation of the server log saved in `g5k06-config100.xml.log`, using
the system information from `config100.xml` and the resource failure information from `g5k06-config100-fails.txt`.
Each core will be `10` pixels tall and the initial scaling factor is set to `2` (maximum of 4 cores per server).

        python3 ./sim_viz.py ./config100.xml -f ./g5k06-config100-fails.txt ./g5k06-config100.xml.log -c 10 -s 2

- Runtime instructions:
    - Click on the tabs above the information windows to switch between `Current Server` and `Current Job` for
    the left window, and `Current Results` and `Final Results` for the right window.
    - Change the currently selected server by moving the `Server` slider. The information in `Current Server` will
    update accordingly, and the green highlight will move to the selected server.
    - Change the currently selected job by moving the `Job` slider. The information in `Current Job` will
    update accordingly. If `Show Job` is selected, then the currently selected job will be highlighted in yellow.
    - Change the time shown in the visualisation by moving the `Time` slider. The information in `Current Server`,
    `Current Job`, and `Current Results` will update accordingly.
    - Press the `-` or `+` button to decrease or increase the scaling factor, respectively.