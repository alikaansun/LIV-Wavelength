import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d
from sympy import false

#File format
#PS_f#_Cl_bar#_Sl_Ff_las#

class spectrum:
    def __init__(self,path):
        self.pat=path
        #print("path",self.pat)
        self.rowskip=2 #14 or #2 change if u get a text in rows || NaN 
        self.frames=self.get_data(path)
        self.siz=np.size(os.listdir())
        
    def get_data(self,path):
        os.chdir(path)
        #sort according to float values
        temp=(np.sort([float(os.listdir()[x].replace(".txt","")) for x in range(np.size(os.listdir()))]))
        list_offiles=[str(x) for x in temp]
        for i in range(len(list_offiles)):
            list_offiles[i]+=".txt" 
        #print(list_offiles)
        df = pd.read_csv(
        os.listdir()[0], sep="\t",names=["x",os.listdir()[0].replace(".txt","")],skiprows=self.rowskip)["x"]
        frames = [pd.read_csv(x,sep="\t",names=["x",x.replace(".txt","")],skiprows=self.rowskip)[x.replace(".txt","")] for x in list_offiles]
        cframes=pd.concat(frames,axis=1)
        cframes=pd.concat([df,cframes],axis=1)
        
        return cframes

    def plotspec(self):
        fig=plt.figure(figsize=(9,5))
        j=0
        ax = fig.add_subplot(111)
        x=self.frames["x"]
        facecolors = plt.colormaps['viridis_r'](np.linspace(0, 1, self.siz))
        for i in self.frames.columns[1:]:
            ax.plot(x,self.frames[i]/self.frames[i].max(),color=facecolors[j],label="I="+i)
            j+=1
        ax.set_xlim(850, 960)
        ax.set_ylim([-0.1,1.1])
        ax.set_xlabel("Wavelength (nm)")
        ax.set_ylabel("Intensity (a.u.)")
        ax.set_title(self.pat)
        plt.legend()
        #fig.colorbar("mappable",cmap='viridis_r',ax=ax)
        plt.show()
        ###
        ### make a second plot where the x axis is wavelength and y axis is peak locations 
        
        

class liv: 
    def __init__(self,path,file):
        self.pat=os.path.join(path,file)
        self.sheets=pd.ExcelFile(self.pat).sheet_names
        self.frames={x:pd.read_excel(self.pat,sheet_name=x) for x in self.sheets} 
        self.pat=self.pat.replace(r".xlsx","").replace(path,"")
        #self.pat=self.pat.replace("_LIV-Lambda","").replace(r"\PS_LI-Lambda_","")
        #print(self.pat)
        self.info={self.pat:self.getinfo(file)}
        #print(self.info)
        self.allframes={self.pat:self.frames.copy()}
        self.isjori=0 #information for function calling, 

    def reload(self,path,file):
        self.pat=os.path.join(path,file)
        self.sheets=pd.ExcelFile(self.pat).sheet_names
        self.frames={x:pd.read_excel(self.pat,sheet_name=x) for x in self.sheets}
        self.pat=self.pat.replace(r".xlsx","").replace(path,"")
        #print(self.pat)
        #print(self.info)
        self.allframes.update({self.pat:self.frames.copy()})
        self.info.update({self.pat:self.getinfo(file)})
        self.isjori=0

    def getinfo(self,file): #get the device information with the formatted name
        file = file.replace(r".xlsx","")
        indx=[]
        for s in range(len(file)):
            if file[s]=="_":
                indx.append(s)
        info={"fab":int(file[indx[0]+1:indx[0+1]]),
        "cl":int(file[indx[1]+1:indx[1+1]]),
        "bar":int(file[indx[2]+1:indx[2+1]]),
        "sl":int(file[indx[3]+1:indx[3+1]]),
        "ff":int(file[indx[4]+1:indx[4+1]]),
        "las":int(file[indx[5]+1::])
        }
        return info

    def powercorrection(self,const): ##need calibration
        #oldconst=8.757467378818607
        for i in self.sheets:
                self.frames[i][self.frames[i].keys()[1]]=2*self.frames[i][self.frames[i].keys()[1]]*const
        self.allframes.update({self.pat:self.frames.copy()})

    def totalcurrent(self): #should be called b4 densitycurrent for ps lasers 
        totali=[x.replace('I2_','').replace('I1_','') for x in self.sheets]
        totali=[float(i) for i in totali]
        j=0
        for i in self.sheets:
            for x in range(len(self.frames[i][self.frames[i].keys()[0]])):
                self.frames[i][self.frames[i].keys()[0]][x]+=totali[j]
            j+=1
        self.allframes.update({self.pat:self.frames.copy()})
        self.isjori=3

    def densitycurrent(self):
        #deadspace per mesa-2 etch + nitride left per trench 
        ds=0.011  #microns 
        #total cavity area 
        A=self.info[self.pat]["cl"]*0.1
        #injection area
        if self.info[self.pat]["sl"]==0: #ref laser
            cA=self.info[self.pat]["cl"]-0.4 #0.4 for unpumped sections 2*0.2
        else: #PS laser
            cA=(self.info[self.pat]["cl"]-0.4)-2*(self.info[self.pat]["cl"]-0.4)*ds/(self.info[self.pat]["sl"]*10**-3)
        for i in self.sheets:  #sheet 0 is current 
                self.frames[i][self.frames[i].keys()[0]]=self.frames[i][self.frames[i].keys()[0]]/(A/cA)
        self.allframes.update({self.pat:self.frames.copy()})
        self.isjori=1
    
    def selection(self,sheets):
        datas={}
        for x in sheets:
            datas[x]=self.frames[x] 
        self.frames=datas
        self.sheets=sheets
        #reloads the allframe
        self.allframes.update({self.pat:self.frames.copy()})

    def heatload(self,fpath):  #1*4-2
        self.getvoltage(fpath)
        #according to voltages, calculate waste power, Pwaste==Pelectrical-Poptical
        for i in self.sheets:
                self.frames[i][self.frames[i].keys()[0]]=self.frames[i][self.frames[i].keys()[0]]*self.frames[i][self.frames[i].keys()[3]]-self.frames[i][self.frames[i].keys()[1]]/1000
        self.allframes.update({self.pat:self.frames.copy()})
        self.isjori=2

    def getvoltage(self,fpath): #first read IV, do interpolation on the voltage and write corresponding voltages
        
        dd=pd.read_csv(r"C:\Users\alika\OneDrive\NanoPHD\Tests\PS-IV\200-AP.csv",sep=",")
        dd=pd.read_csv(fpath,sep=",")
    
        for i in range(3):
            del dd[dd.keys()[0]]
        del dd[dd.keys()[2]]
        for i in self.sheets:
            newx=self.frames[i][self.frames[i].keys()[0]]
            self.frames[i]['Voltage']=interp1d(dd[dd.keys()[1]],dd[dd.keys()[0]],kind="cubic")(newx)  
        #plt.plot(newx,a,"o",label=i)
        #plt.plot(dd[dd.keys()[1]],dd[dd.keys()[0]])
        #plt.show()

        self.allframes.update({self.pat:self.frames.copy()})
#label=frametitle.replace("\REF","")+"-"+sheet
    def plotli(self,delta):
        
        fig1=plt.figure(figsize=(12,5))#power
        #fig2=plt.figure(figsize=(6,5))#wav  
        ax1=fig1.add_subplot(121)
        ax2=fig1.add_subplot(122)  
        for frametitle in self.allframes.keys():
            data=self.allframes[frametitle]
            info=self.info[frametitle]
           
            for sheet in data.keys():
                if delta==True:
                    for x in range(len(data[sheet][data[sheet].keys()[2]])):
                        if data[sheet][data[sheet].keys()[2]][x] > 0:
                            fitnz=data[sheet][data[sheet].keys()[2]][x]
                            break
                else:
                    fitnz=0
                ax1.plot(
                    data[sheet][data[sheet].keys()[0]],
                    data[sheet][data[sheet].keys()[1]],
                    '*-',markersize=2,
                    label="CL="+str(info["cl"])+", SL="+str(info["sl"])+", FF="+str(info["ff"])+", "+sheet.replace("_","="))
                    #label=sheet.replace("_","="))
                ax2.plot(
                    data[sheet][data[sheet].keys()[0]],
                    data[sheet][data[sheet].keys()[2]]-fitnz,
                    '*-',markersize=2,
                    label="CL="+str(info["cl"])+", SL="+str(info["sl"])+", FF="+str(info["ff"])+", "+sheet.replace("_","="))
                    #label=sheet.replace("_","="))
                 
        ax1.legend()
        ax1.set_ylabel("Power (mW)")
        ax2.legend()
        ax2.set_ylabel("Wavelength (nm)")
        
        if self.isjori==1:           
            ax1.set_xlabel("Current Density (A/mm2)")       
            ax2.set_xlabel("Current Density (A/mm2)")
        elif self.isjori==2:
            ax1.set_xlabel("Heat Load (W)")       
            ax2.set_xlabel("Heat Load (W)")
        elif self.isjori==3:
            ax1.set_xlabel("Total Current (A)")       
            ax2.set_xlabel("Total Current (A)")
        else:
            ax1.set_xlabel("Current (A)")       
            ax2.set_xlabel("Current (A)")
        plt.show()


    def plotliv(self):
        
        fig1=plt.figure(figsize=(15,5))#power
        #fig2=plt.figure(figsize=(6,5))#wav  
        ax1=fig1.add_subplot(121)
        ax3=ax1.twinx()
        ax2=fig1.add_subplot(122)  
        for frametitle in self.allframes.keys():
            data=self.allframes[frametitle]
            for sheet in data.keys():
                ax1.plot(
                    data[sheet][data[sheet].keys()[0]],
                    data[sheet][data[sheet].keys()[1]],
                    label=frametitle.replace("\REF","")+"-"+sheet)

                ax2.plot(
                    data[sheet][data[sheet].keys()[0]],
                    data[sheet][data[sheet].keys()[2]],
                    label=frametitle.replace("\REF","")+"-"+sheet)
                
                ax3.plot(
                    data[sheet][data[sheet].keys()[0]],
                    data[sheet][data[sheet].keys()[3]],
                    "--",
                    label=frametitle.replace("\REF","")+"- "+sheet+"Voltage")
                #"CL="+str(info["cl"])+", SL="+str(info["sl"])+", FF="+str(info["ff"])+", "+sheet.replace("_","=")

        ax1.legend()
        #ax1.set_xlabel("Current (A)")
        ax1.set_ylabel("Power (mW)")
        ax2.legend()
        #ax2.set_xlabel("Current (A)")
        ax2.set_ylabel("Wavelength (nm)")
        if self.isjori==1:           
            ax1.set_xlabel("Current Density (A/mm2)")       
            ax2.set_xlabel("Current Density (A/mm2)")
        elif self.isjori==2:
            ax1.set_xlabel("Heat Load (W)")       
            ax2.set_xlabel("Heat Load (W)")
        elif self.isjori==3:
            ax1.set_xlabel("Total Current (A)")       
            ax2.set_xlabel("Total Current (A)")
        else:
            ax1.set_xlabel("Current (A)")       
            ax2.set_xlabel("Current (A)")
        ax3.set_ylabel("Voltage (V)")
        ax3.legend(loc="upper center")
        plt.legend()
        plt.show()


        
    





    
