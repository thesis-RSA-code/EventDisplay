A simple interactive event display for water Cherenkov cylindrical experiments. For now, it supports SK, HK and WCTE. The program takes for input a root file containing a series of events, each event being a list of the activated PMTs 3D positions, their corresponding detected charge as well the time the PMTs were triggered. The program will open a tkinter interactive window, in which one can browse through the events stored in the root file, either through a slider or an entry box, and look at the time distribution of each event with a slider.

# Installation

The program runs with Python 3. The right version, as well as the necessary modules are list in requirements.txt. To setup the adequate environment using conda, simply type 

```bash
conda env create -f requirements.yml
```

in your terminal, then activate it with

```bash
conda activate event_display
```

Note that the code opens an interactive Tkinter window or a matplotlib window, so X11 forwarding should be enabled when executing the program remotely through a ssh connection. When connecting with a terminal, this is done with

```bash
ssh -X user@remote_ip
```

To enable X11 forwarding with the vscode ssh extension, open the ssh config file of your local vscode (usually in `home/.ssh/config`), and add the last two lines under the desired remote host

```bash
Host hostname
    HostName host.domain
    User username
    IdentityFile ssh_key
    ForwardX11 yes
    ForwardX11Trusted yes
```

Examples on how to execute the different programs are located in `scripts/`

# Event Display

The program `event_display.py` shows a 2D projection of Cherenkov events in the tank. One can either display a single event in a matplotlib window, or browse through several events in a tkinter interactive window. Details on how to use the program can be accessed by typing

```bash 
python3 event_display.py -h
```

Enjoy !

![SK_readme](https://github.com/user-attachments/assets/aa897064-af3e-4370-921d-4ed503fc7917)



# 3D Display

The program `3D_display.py` shows a 3D view of the event inside the detector using pyvista. Once again, one can browse through the different options with 

```bash 
python3 3D_display.py -h
```


# Showering Display

The program `showering_display.py` also shows a 3D view of the event inside the detector using pyvista. However, it is meant to display the tracks of the particles that were tracked in the WCSim simulation. The input root file has to be the output of `WCSimRoot_to_root_all_tracks`. The program also includes checkbox widgets to only display particles which were created by specific processes (pair annihilation, Bremsstrahlung, photon conversion etc...).

![image](https://github.com/user-attachments/assets/690c374d-363b-450d-8add-036d43b55562)

# TO DO

- It would be great the read the geometry characterics of the detectors (height, radius, PMT radius) directly from the root file, so as to support any cylindrical tank without having to manually add it to the `detector_geom` dictionnary. It would first require the modification of the `wcsimroot_to_root` software. The tag indicating whether a PMT sits on the cylinder, the bottom or top cap would also be appreciable, so as to facilitate the projection.

- Purely cosmetics, but maybe have a better widget layout... really not a priority.

