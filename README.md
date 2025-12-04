A simple interactive event display for water Cherenkov cylindrical experiments. For now, it supports SK, HK and WCTE. The program takes for input a root file containing a series of events, each event being a list of the activated PMTs 3D positions, their corresponding detected charge as well the time the PMTs were triggered. The program will open a tkinter interactive window, in which one can browse through the events stored in the root file, either through a slider or an entry box, and look at the time distribution of each event with a slider.

# Installation

The program runs with Python 3. The right version, as well as the necessary modules are list in requirements.txt. To setup the adequate environment using conda, simply type 

# Showering Display

The program `showering_display.py` also shows a 3D view of the event inside the detector using pyvista. However, it is meant to display the tracks of the particles that were tracked in the WCSim simulation. The input root file has to be the output of `WCSimRoot_to_root_all_tracks`. The program also includes checkbox widgets to only display particles which were created by specific processes (pair annihilation, Bremsstrahlung, photon conversion etc...).

![image](https://github.com/user-attachments/assets/690c374d-363b-450d-8add-036d43b55562)

# TO DO

- It would be great the read the geometry characterics of the detectors (height, radius, PMT radius) directly from the root file, so as to support any cylindrical tank without having to manually add it to the `detector_geom` dictionnary. It would first require the modification of the `wcsimroot_to_root` software. The tag indicating whether a PMT sits on the cylinder, the bottom or top cap would also be appreciable, so as to facilitate the projection.

- Purely cosmetics, but maybe have a better widget layout... really not a priority.

