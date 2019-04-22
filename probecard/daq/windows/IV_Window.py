from .DetailWindow import DetailWindow

class IV_Window(DetailWindow):
    def addPoint(self,point):
        self.fig.clear()
        volt=point[0]
        meas=point[1]
        try:
            self.cache['volts']
        except KeyError:
            self.cache['volts']=set()
        self.cache['volts'].add(volt)

        ## Add recent measurement to cach
        for key,item in meas.items():
            if 'pass' in key: continue
            try:
                self.cache[key].append(item)
            except KeyError:
                self.cache[key]=[]
                self.cache[key].append(item)

        ## Then Plot
        for key,item in self.cache.items():
            if key == 'volts' : continue
            voltages=sorted(list(self.cache['volts'])[:len(self.cache[key])])[::-1]
            try:
                self.fig.plot(voltages,self.cache[key],label=key)
            except ValueError:
                print("could not plot.len(volt)!=len(y)",voltages,self.cache[key])
        self.fig.legend() #enables the legend
        self.fig.invert_xaxis()
        self.fig.set_xlabel("Voltage (V)")
        self.fig.set_ylabel("Current (A)")
        self.fig.set_title("Multichannel Current vs Voltage")
        self.canvas.draw()
