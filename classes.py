import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import os
from IPython.display import Image, display


class PlotClass():

    cases = {"No Fea":"01", "FEA":"04"}
    energies = np.arange(6000,36000,1000)
    title = "Title"
    xlabel, y1label, y2label = 'x-Label', 'y-label', 'y2-label'
    plot_size = [15,8]
    xfontsize, y1fontsize, y2fontsize = 10, 10, 10
    legend, anchor = True, (.8,.2)
    dpi = 1000

    def __init__(self, data={"":""}):
        for key, value in data.items(): setattr(self, key, value)

    def optics(self):
        directory = "data/Scan{}/res/fig/setup.png".format(self.scan_number)
        display(Image(directory))

    def USGExtrema(self,):
        for legend, case in self.cases.items():
            filename = "data/Scan{}/res/{}/fea_output_{}.tsv".format(self.scan_number, case,self.optical_element)
            try:
                df = pd.read_csv(filename, delim_whitespace=True)
                df.columns=['x','y','z','T','stress','def','strain','dStrain','CTE','TC']
                max, min = df['dStrain'].max(), df['dStrain'].min()
                #print("Case {}: Max, Min USG is {},{}".format(case, max,min))
                print("Case {}: Max, Min USG is {},{}".format(case, max,min))
            except: print("Can't find Case {}".format(case))
    
    def AllUSG(self): pass
	

    def plot(self):
        #Basic Plot Parameters
        plt.rcParams['figure.figsize'] = self.plot_size
        fig, ax1 = plt.subplots()
        minor_ticks = self.energies
        ax1.set_xticks(minor_ticks, minor=True)
        ax1.grid(which='minor', alpha=0.25)
        ax1.grid(which='major', alpha=0.5)
        #try: self.title += ': Element {}'.format(self.optical_element)
        #except: pass
        plt.title(self.title)
        ax1.set_xlabel(self.xlabel, fontsize = self.xfontsize)
        ax1.set_ylabel(self.y1label, fontsize = self.y1fontsize)


        # Plot First Y-Axis data
        i=0
        for legend, df in self.y1data.items():
            try:
                try: mark = self.markers[i]
                except: mark = "."
                try: 
                    color = self.colors[i]
                    ax1.plot(df, marker=mark, color=color, label=legend,)
                except:  ax1.plot(df, marker=mark, label=legend,)
                #ax1.legend()#bbox_to_anchor=(.04,1))#,loc="lower left", ncol=2)
            except: pass
            i+=1

        # Plot Second Y-Axis Data if Defined
        try:
            self.y2data
            ax2 = ax1.twinx()
            ax2.set_ylabel(self.y2label, fontsize = self.y2fontsize)

            #Try to Manually Limit Axes
            try: ax2.set_ylim([0,self.y2limit])
            except: pass

            for legend,df in self.y2data.items():
                try: mark = self.markers[i]
                except: mark = "."
                ax2.plot(df, marker=mark, color='green', label=legend)
                #ax2.legend()#bbox_to_anchor=(.8,1))#,loc="lower left")
                i += 1
        except: pass

        # Add Letter Box to Plot
        try: 
            self.text
            props = dict(boxstyle='round', facecolor='white', alpha=1)
            ax1.text(0.05, 0.95, text, transform=ax1.transAxes, fontsize=20,
            verticalalignment='top', bbox=props)
        except: pass
        if legend: fig.legend(loc="lower right", bbox_to_anchor=self.anchor)
        plt.tight_layout()
        
        # Save Plot to File
        try:
            self.filename
            directory = "data/Scan{}/pyplot/".format(self.scan_number)
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename = directory + "{}.png".format(self.filename)
            plt.savefig(filename, bbox_inches = 'tight', format='png', dpi=self.dpi)
            print("Plot saved to {}".format(filename))
        except: pass
        plt.show()
		
class CaseComparison(PlotClass):
    xlabel = "Central Energy (eV)"
    y2label = 'Percentage'
    plot_difference = False
	
    def get_statistics(self, case, column_name=None, skip=4,):
        try:
            statistics =  pd.read_csv("data/Scan{}/res/{}/{}_{}.tsv".format(self.scan_number, case,self.file,self.optical_element), 
                                   delim_whitespace=True, skiprows=skip, header=None, index_col=0)
            try:
                self.statistics_column
                statistics = statistics[[self.statistics_column]]
                statistics.columns = [column_name]
            except: pass
        except: statistics = np.NaN
        return statistics

    def plot(self):
        self.y1data = pd.DataFrame(index=self.energies, columns=self.cases.keys())
        for legend, case in self.cases.items(): self.y1data[legend] = self.get_statistics(case)
        
        if self.plot_difference:
            def x(i): return self.y1data[list(self.cases.keys())[i]]
            self.y2data = {"Difference" : abs(x(0)-x(1))*100/x(0)}
        
        super().plot()
        
class AngleOptimization(CaseComparison):
    statistics_column = 16
    file = 'focus_savg'
    y1label = "Photons/s"

    def plot(self):
        print("This class is a little touchy to get working.")
        print("Better copy and paste a working example and go from there.")
        self.y1data = pd.DataFrame(index=self.energies, columns=self.cases.keys())
        for legend, case in self.cases.items(): self.y1data[legend] = self.get_statistics(case)
        a = self.y1data.drop(columns='No Fea')
        a = a.max(axis=1)
        a.name = "Max"
        self.y1data = pd.concat([self.y1data[['No Fea', '0']],a], axis = 1)
        list = ['No Fea', 'Max']
        if self.plot_difference:
            def x(i): return self.y1data[list[i]]
            self.y2data = {"Difference" : abs(x(0)-x(1))*100/x(0)}
        PlotClass.plot(self)
		
class Bandwidth(CaseComparison):
    title = 'Monochromator Bandwidth'
    y1label = 'dE/E'
    file = 'focus_savg'
    statistics_column = 26
    
    def get_statistics(self, case):
        def div(y): 
            try: return y.div(y.index.to_series(), axis=0)
            except: return None
        return div(super().get_statistics(case))

		
class PowerPlot(CaseComparison):
    title = 'Normalized Power'
    y1label = 'Photons/s'
    statistics_column = 16
    file = 'focus_savg'
    i=0
    def get_statistics(self, case):
        y1 = super().get_statistics(case)
        a = [1,2,3,4]*2
        y1=y1/a[self.i]
        self.i += 1

        return y1
    def plot(self):
        print("Warning: PowerPlot class may have glitches when"
             +" it comes to normalizing")
        super().plot()


class AbsorbedPower(CaseComparison):
    title = 'Absorbed Power'
    y1label = 'Watts'
    statistics_column = 6
    file = 'power_abs_stat'
	
class IncidentPower(AbsorbedPower):
    title = 'Incident Power'
    file = 'power_inc_stat'
	
class PowerArea(AbsorbedPower):
	title = 'Absorbed Power per Area'
	y1label= 'Watts/cm/cm'
	statistics_column = 1

class MaxTemperature(CaseComparison):
    title = 'Max Temperature'
    y1label = 'Kelvin'
    statistics_column = 1
    file = 'temp_stat'

class MaxDeformation(CaseComparison):
    title = 'Max Deformation'
    y1label = 'dz [cm]'
    statistics_column = 1
    file = 'deform_stat'
    
    
class Flux(CaseComparison):
    title = 'Reflected Photon Flux'
    y1label = 'Photons/s'
    statistics_column = 16
    file = 'focus_savg'
    
class Spectra(PlotClass):
    break_loop = False
    plot_size = [10,8]

    def get_spectrum(self, scan_number, case, energy, optical_element):
        try:
            a = pd.read_csv("data/Scan{}/res/{}/{}_{}.tsv".format(scan_number, case, self.file, optical_element),
                            delim_whitespace=True, header=None, index_col=0, comment='#')
            y = a.loc[a.index == energy]
            y.set_index(self.index, inplace=True)
            #y[self.statistics_column] = y.max(axis=1)
            #y.to_frame()
            #y.columns = [self.statistics_column]
            #print(y)
            return y
        except: return None


    def plot(self):
        for energy in self.energies:
            self.y1data = pd.DataFrame(columns=self.cases.keys())
            for legend, case in self.cases.items():
                try: self.y1data[legend] = self.get_spectrum(self.scan_number, case, energy, self.optical_element)[self.statistics_column]
                except: pass
            #self.title = 'Spectrum for {} eV'.format(energy,)
            try: self.filename += str(energy) + "eV"
            except: pass
            super().plot()
            if self.break_loop: break



class Spectrum(Spectra):
    statistics_column = 2
    plot_size = [10,8]
    xlabel = 'E-E$_0$ (eV)'
    y1label = 'Photons/s'
    file = 'focus_band'
    index = 1
                
class Temperature(Spectra):
    xlabel = 'y [cm]'
    y1label = 'Kelvin'
    statistics_column = 3
    file = 'temp_image'
    index = 2
    
class Deformation(Spectra):
    xlabel = 'y [cm]'
    y1label = 'cm'
    statistics_column = 3
    file = 'deform_image'
    index = 2

class DerDeformation(Deformation):
    statistics_column = 5 # 4 is x, 5 is y


class BeamOffset(PlotClass):
    break_loop = False
    plot_size  = [10,6]
    xlabel     = "angle ($\mu$rad)"
    file       = 'focus_savg'
    filename   = "shift_crystal_angle__"

       
    

    def get_spectrum(self, scan_number, case, energy, optical_element, legend):
            a = pd.read_csv("data/Scan{}/res/{}/{}_{}.tsv".format(scan_number, case, self.file, optical_element),
                            delim_whitespace=True, header=None, index_col=0, comment='#')
            y = a.loc[a.index == energy]
            y2 = pd.DataFrame(index=[legend], columns=[self.y_name])
            y2[self.y_name] = y[self.statistics_column].iloc[0]

            return y2
  

    def plot(self):
        for energy in self.energies:
            i = 0
            for legend, case in self.cases.items():
                y2 = self.get_spectrum(self.scan_number, case, energy, self.optical_element, legend)
                if i == 0: self.y1data = y2
                else: self.y1data = pd.concat([self.y1data, y2])
                i += 1

            self.y1data = self.y1data.sort_index(ascending = True)
            self.y1data -= self.y1data.loc[0, self.y1data.columns[0]]
            print(self.__class__.__name__)
            if self.__class__.__name__ in ["xcen", "zcen"]: self.y1data *= 10000
            if self.__class__.__name__ in ["xpcen", "zpcen"]: self.y1data *= 1000000
            #self.y1data['x'] = self.y1data.x.rolling(1).mean()
            #self.y1data['x'] = self.y1data.x.interpolate(method = "linear")
            try: self.filename += str(energy) + "eV"
            except: pass
            super().plot()
            if self.break_loop: break

                
class xcen(BeamOffset):
    title = "Beam offset at sample position in x"
    y_name = 'x'
    statistics_column = 7
    y1label = 'beam x shift ($\mu$m)'
    filename= BeamOffset.filename + "x_offset"
                
                
class zcen(BeamOffset):
    title = "Beam offset at sample position in z"
    y_name = 'z'
    statistics_column = 8
    y1label = 'beam z shift ($\mu$m)'
    filename = BeamOffset.filename +  "z_offset"

    
class xpcen(BeamOffset):
    title = "Beam offset at sample position in xp"
    y_name = 'xp'
    statistics_column = 17
    y1label = 'beam xp shift ($\mu$rad)'
    filename = BeamOffset.filename + "xp_offset"
    
class zpcen(BeamOffset):
    title = "Beam offset at sample position in zp"
    y_name = 'zp'
    statistics_column = 18
    y1label = 'beam zp shift ($\mu$rad)'
    filename = BeamOffset.filename + "zp_offset"
               
                






class USG():
    save_figure = False
    break_loop  = False
    def get_spectrum(self, filename, column_name=None, skip=3,):
        statistics =  pd.read_csv("USG/data/{}".format(filename), 
                                   delim_whitespace=True, skiprows=skip, header=None, index_col=0)
        statistics.columns=["No Strain","Strain"]
        statistics.index = statistics.index/10e-6
        return statistics
    
    def plot(self):
        plt.rcParams['figure.figsize'] = [4.75,3.25]
        for filename in os.listdir("./USG/data"):
            y1data = self.get_spectrum(filename)
            y1data.plot(style=[":","-",])
            plt.xlabel("$\mu$rad", fontsize = 18)
            plt.ylabel("Reflectivity",fontsize = 20)
            max = y1data.index.max()
            min = y1data.index.min()
            plt.xlim(min, max)
            plt.ylim(0,1)
            plt.tight_layout()
            print(''.join(["_"]*50)+'\n')
            print(filename)
            if self.save_figure:
                plt.savefig("./USG/{}.png".format(filename), format='png', dpi=1000)
                print("Figure Saved")
            if self.break_loop: break
            plt.show()
