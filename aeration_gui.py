# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
import minimalmodbus
import sys
import glob
import serial
import numpy as np
from functools import partial
import math

class DO_gui():
    def __init__(self, master):
        master.title('DO and Aeration')        
        master.geometry('900x500')
        self.port_pump = tk.StringVar(master)
        self.port_sensor = tk.StringVar(master)
        self.port_list = self.serial_ports()
        self.current_DO = tk.DoubleVar(master)
        self.current_temperature = tk.DoubleVar(master)
        self.saturate_DO = tk.DoubleVar(master)
        self.DO_table = [14.62,14.22,13.83,13.46,13.11,12.77,12.45,12.14,11.84,11.56,
                         11.29,11.03,10.78,10.54,10.31,10.08,9.87,9.66,9.47,9.28,
                         9.09,8.92,8.74,8.58,8.42,8.26,8.11,7.97,7.83,7.69,7.56]
        
        self.create_widet(master)
        self.random(master)
        
        
        
    def create_widet(self, master):
        # row 0 for ports
        self.label1 = tk.Label(master, text='Pump port:')
        self.label2 = tk.Label(master, text='Sensor port:')
        self.dropdown1 = ttk.Combobox(master, values=self.port_list, 
                                      state='readonly')
        self.dropdown2 = ttk.Combobox(master, values=self.port_list, 
                                      state='readonly')
        self.button1 = tk.Button(master, text='Apply', command=self.apply_port,
                                 width=8)
        self.button2 = tk.Button(master, text='Initialize', command=self.equipment_initialize,
                                 width=10)
        self.label1.grid(row=0, column=0, 
                         padx=10, pady=10)
        self.dropdown1.grid(row=0, column=1, 
                            padx=10, pady=10)
        self.label2.grid(row=0, column=2, 
                         padx=10, pady=10)
        self.dropdown2.grid(row=0, column=3, 
                            padx=10, pady=10)
        self.button1.grid(row=0, column=4, 
                          padx=10, pady=10)
        self.button2.grid(row=0, column=5,
                          padx=10, pady=10)
        
        # DO display in row 1-2
        self.label3 = tk.Label(master, text='Current DO:')
        self.label4 = tk.Label(master, textvariable=self.current_DO, font=("Arial", 35))
        self.label5 = tk.Label(master, text='mg/L')
        self.label6 = tk.Label(master, text='Current temperature:')
        self.label7 = tk.Label(master, textvariable=self.current_temperature)
        self.label8 = tk.Label(master, text=u'\N{DEGREE SIGN}'+'C')
        self.label9 = tk.Label(master, text='Approximate saturate DO:')
        self.label10 = tk.Label(master, textvariable=self.saturate_DO)
        self.label11 = tk.Label(master, text='mg/L')
        self.label3.grid(row=1, column=0)
        self.label4.grid(row=1, column=1, 
                         columnspan=2)
        self.label5.grid(row=1, column=2, 
                         sticky='w')
        self.label6.grid(row=1, column=3)
        self.label7.grid(row=1, column=4)
        self.label8.grid(row=1, column=5,
                         sticky='w')
        self.label9.grid(row=2, column=0)
        self.label10.grid(row=2, column=1,
                          columnspan=2)
        self.label11.grid(row=2, column=2, 
                         sticky='w')
        
        # buttons in row 3
        self.button3 = tk.Button(master, text='START', command=partial(self.measure, master),
                                 width=10, font=("Arial", 15), fg='green')
        self.button4 = tk.Button(master, text='STOP', command=partial(self.stop_measure, master),
                                 width=10, font=("Arial", 15), fg='red')
        self.button3.grid(row=3, column=3)
        self.button4.grid(row=3, column=4)
    
    def measure(self, master):
        global timer
        self.sensor.write_register(1, 31, functioncode=6) # may not be useful
        self.current_temperature.set(self.sensor.read_float(83))
        
        i = math.floor(self.current_temperature.get())
        if i>30:
            i = 30
        
        self.saturate_DO.set(self.DO_table[])
        self.current_DO.set(self.sensor.read_float(87))
        if self.current_DO.get()>=5:
            self.label4.config(fg='green')
            self.stop_VFD()
        elif self.current_DO.get()>=2.5:
            self.label4.config(fg='orange')
        elif self.current_DO.get()<2.5:
            self.label4.config(fg='red')
        elif self.current_DO.get()<1.5:
            self.label4.config(fg='red')
            self.start_VFD()
        timer = master.after(1000, self.measure, master)
        
        
    def random(self, master):        
        self.current_temperature.set(round(np.random.uniform(0,30), 2))        
        self.saturate_DO.set(self.DO_table[math.floor(self.current_temperature.get())])
        self.current_DO.set(round(np.random.uniform(0,self.saturate_DO.get()), 2))
        if self.current_DO.get()/self.saturate_DO.get()>=0.8:
            self.label4.config(fg='green')
        elif self.current_DO.get()/self.saturate_DO.get()>=0.4:
            self.label4.config(fg='orange')
        else:
            self.label4.config(fg='red')
        timer = master.after(1000, self.random, master)
    
    def stop_measure(self, master):
        master.after_cancel(timer)
    
    def equipment_initialize(self):
        # start VFD
        self.VFD = minimalmodbus.Instrument(self.dropdown_1.get(), 1) # slave ID 1
        self.VFD.serial.baudrate = 9600
        self.VFD.serial.timeout = 0.25
        self.VFD.write_register(0, 1, functioncode=6) 
        # set frequency to 0 after startup
        self.VFD.write_register(1, 0, 
                                  number_of_decimals=1, functioncode=6) 
        # start sensor
        self.sensor = minimalmodbus.Instrument(self.dropdown_2.get(), 10) # slave ID 10
        self.sensor.serial.baudrate = 9600
        self.sensor.write_register(1, 31, functioncode=6) 
        self.current_temperature.set(self.sensor.read_float(83))
        self.current_DO.set(self.sensor.read_float(87))
        if self.current_DO.get()>=5:
            self.label4.config(fg='green')
        elif self.current_DO.get()>=2.5:
            self.label4.config(fg='orange')
        elif self.current_DO.get()<2.5:
            self.label4.config(fg='red')
        
    def start_VFD(self):
        self.VFD.write_register(0, 1, functioncode=6) 
        # set frequency to 0 after startup
        self.VFD.write_register(1, 60, 
                                  number_of_decimals=1, functioncode=6)  
        
    def stop_VFD(self):
        self.VFD.write_register(0, 0, functioncode=6) 
        
    def apply_port(self):
        # set the port number
        try:
            self.port_pump.set(self.dropdown_1.get())
            self.port_sensor.set(self.dropdown_2.get())
        except IndexError:
            pass
        
    def serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')  
        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result
        
if __name__ == '__main__':        
        
    root = tk.Tk()         
    gui = DO_gui(root)     

    root.mainloop()
