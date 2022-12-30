from dataread import spectrum as spec
from dataread import liv as liv


#path+=r"\200-1"
#path+=r"\ref"
#path+=r"\I2_0.5"
#####
path1=r"C:\Users\alika\Documents\GitHub\PolySection\Tests\Fab1"
path2=r"C:\Users\alika\Documents\GitHub\PolySection\Tests\Fab2"
#path+=r"\200-2"
#path+=r"\I1_1"
#path+=r"\Spec"
####

file=r"PS_1_3_1_100_50_1.xlsx"
file1=r"PS_1_3_1_200_50_1.xlsx"
file2=r"PS_2_3_1_300_50_2.xlsx"
file21=r"PS_2_6_3_300_50_1.xlsx"
file22=r"PS_2_6_2_300_75_1.xlsx"
file03=r"PS_2_3_1_0_0_1.xlsx"
file061=r"PS_2_6_1_0_0_2.xlsx"
file062=r"PS_2_6_2_0_0_1.xlsx"
#####
IVpath="..."

'''spc = spec(path)
spc.plotspec("a")'''
ca=0.135
cb=91.5

#path=os.path.join(main_path1,file3)
li=liv(path2,file03)
li.selection([li.sheets[1]])
li.powercorrection(ca)

#print(li.frames,"\n",li.sheets[0])
#li.selection([])
#li.totalcurrent()
#li.densitycurrent()

#li.heatload(IVpath)


li.reload(path2,file21)
#li.totalcurrent()
li.selection([li.sheets[2]])
li.powercorrection(cb)


li.plotli(True)
