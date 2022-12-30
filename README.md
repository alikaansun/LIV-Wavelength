# LIV-Wavelength
Optical-Electrical Analysis Tool to be used in standard and multi-section waveguide lasers

Two main class for utilized,

.liv(path,file) class: reads data from .xlsx files, capable of selecting data sheets and loading as many files posible.
Loading data from separate files requires .reload function
File name format: PS_f_Cl_bar_Sl_Ff_las#
f : fabrication number
Cl: Cavity length
bar: Bar number
Sl: Section length of our polysection lasers
Ff: Fillfactor is the active injection area (I1) to total injection area. Passive section pumped with less current defined as I2 
for each data loaded,
.powercorrection(x): x will be the multiplication correction factor according to your setup calibration
.totalcurrent(): calculates total current depending on the laser type. If two sources used, I1_x or I2_x writen on the sheetnames, x will be added to current-data
.currentdensity(): according to the laser information collected, calculates current injection area and divides the current accordingly
.heatload(): reads the corresponding voltage, interpolates to get the exact value and calculates Pwaste=Pelectric=Poptical
functions can be called to alter data and plot accordingly.

.spectrum(path) class: plots multiple optical spectrum data read from .csv files
.plotspec() :plots the file data given in the path




#Polysection laser design
...
