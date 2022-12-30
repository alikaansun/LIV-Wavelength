from dataread import spectrum as spec
from dataread import liv as liv

#####
path=""
#####
#path+=r"\I2_0.5"
####
file1=r"PS_2_3_1_0_0_1.xlsx"
file2=r"PS_2_3_1_300_50_2.xlsx"
file3=r"PS_2_6_2_0_0_1.xlsx"

#####
IVpath="..."

'''spc = spec(path)
spc.plotspec("a")'''

#correction factor for power measurements.
ca=0.135
cb=91.5

#call the class for LIV-wavelength analysis
li=liv(path,file1)
li.selection([li.sheets[1]])
li.powercorrection(ca)


#add extra files to your datapool by with the .reload
li.reload(path,file2)
#li.totalcurrent() #add current of secondary source to x axis
li.selection([li.sheets[5],li.sheets[10],li.sheets[15]])
li.powercorrection(ca)

#
#If **true, wavelength plot will be delta wavelength
li.plotli(True)
