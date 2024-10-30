A simple interactive event display for water Cherenkov experiments. For now, it supports SK, HK and WCTE. The program takes for input a root file containing a series of events, each event being a list of the activated PMTs 3D positions, their corresponding detected charge as well the time the PMTs were triggered. The program will open a tkinter interactive window, in which one can browse through the events stored in the root file, either through a slider or an entry box, and look at the time distribution of each event with a slider.

# Installation

The program runs with Python 3. The right version, as well as the necessary modules are list in requirements.txt. To setup the adequate environment using conda, simply type 

```bash
conda env create -f requirements.yml
```

in your terminal, then activate it with

```bash
conda activate event_display
```

# Run the program

To execute the program, first indicate the location and of the root file whose events you wish to display. Simply change the variables `path2event` and `events_file` in `event_display.py`. The variable `events_to_display` selects the specific events you want to display, `"all"` being all of the events in the root file, an integer only a specific event and a tuple of integers all of the events between the first index and the second index (particularly useful if the root file contains a lot of events, which could potentially take up too much RAM and processing time to open the event display). Then simply execute the program with

```bash 
python3 event_display.py
```

Note that the code opens an interactive Tkinter window, so X11 forwarding should be enabled when executing the program remotely through a ssh connection. When connecting with a terminal, this is done with

```bash
ssh -X user@remote_ip
```

To enable X11 forwarding with the vscode ssh extension, open the ssh config file of your local vscode, and add the last two lines to the desired remote host

```bash
Host hostname
    HostName host.domain
    User username
    IdentityFile ssh_key
    ForwardX11 yes
    ForwardX11Trusted yes
```