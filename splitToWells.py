import photo

folder = r"C:\Users\nangel\Desktop\Mor\Spinning Disk\2023-9-7 N tag mini Pex Library H2O2 2mM again"
# sp = photo.SpinninDick(folder=folder)
# sp.move(folder)

# folder = r"C:\Users\nangel\Desktop\Mor\2023-Sep-7 Screen minipex library C' H2O2 2mM\plate_001"
mic = photo.Microscope(folder=folder)
mic.move(folder)
