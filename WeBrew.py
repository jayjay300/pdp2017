#!/usr/bin/python
import os
import glob
import time
import blescan
import sys
import requests
import bluetooth._bluetooth as bluez
import pygame
import numpy as np
import tkinter as tk
import RPi.GPIO as GPIO
from PIL import ImageTk,Image
from firebase import firebase
from datetime import datetime
import matplotlib
import matplotlib.image as mpimg
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches



os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir ='/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

firebase = firebase.FirebaseApplication('https://webrew-d32dd.firebaseio.com', None)

coldcrush= False 


#Assign uuid's of various colour tilt hydrometers. BLE devices like the tilt work primarily using advertisements. 
#The first section of any advertisement is the universally unique identifier. Tilt uses a particular identifier based on the colour of the device
red    	= 'a495bb10c5b14b44b5121370f02d74de'
green  	= 'a495bb20c5b14b44b5121370f02d74de'
black  	= 'a495bb30c5b14b44b5121370f02d74de'
purple 	= 'a495bb40c5b14b44b5121370f02d74de'
orange 	= 'a495bb50c5b14b44b5121370f02d74de'
blue   	= 'a495bb60c5b14b44b5121370f02d74de'
yellow 	= 'a495bb70c5b14b44b5121370f02d74de'
pink   	= 'a495bb80c5b14b44b5121370f02d74de'


dev_id = 0






GPIO.setmode(GPIO.BOARD)
chan_heat = [13,18,29,36,37]
chan_cool = [11,15,16,22,31]
GPIO.setup(chan_heat, GPIO.OUT)
GPIO.setup(chan_cool, GPIO.OUT)



#ax = plt.gca()
#ax2 = ax.twinx() #set scale


def heat():
	GPIO.output(chan_heat, GPIO.HIGH)
	GPIO.output(chan_cool, GPIO.LOW)

def cool():
	GPIO.output(chan_heat, GPIO.LOW)
	GPIO.output(chan_cool, GPIO.HIGH)
	
def shutoff():
        GPIO.output(chan_heat, GPIO.LOW)
        GPIO.output(chan_cool, GPIO.LOW)



def read_Sg():
        try:
                sock = bluez.hci_open_dev(dev_id)

        except:
                print ("error accessing bluetooth device...")
                sys.exit(1)

        blescan.hci_le_set_scan_parameters(sock)
        blescan.hci_enable_le_scan(sock)

	#gotData = 0
	#while (gotData == 0):

        returnedList = blescan.parse_events(sock, 10)

        for beacon in returnedList: #returnedList is a list datatype of string datatypes seperated by commas (,)
                output = beacon.split(',') #split the list into individual strings in an array
                if output[1] == green: #Change this to the colour of you tilt
			
                        #gotData = 1
                        tiltSG = int(output[3],16)/1000
                        print ("testing")
                        print (tiltSG)
                        print ("-----")



        blescan.hci_disable_le_scan(sock)
        return tiltSG
		

	
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_time():
    currenttime= datetime.now().replace(microsecond=0)
    return currenttime


def read_timegui():
    ctime = read_time()
    a = "%d:%02d" % (ctime.hour,ctime.minute)
    return a
    
        

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        currenttime = read_time()
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        stringtemp = str(temp_c)
        # Set condition to not send if data is the same
        #result = firebase.post('/users/1002', {'time':str(currenttime),'temp':temp_c, 'hydro': 1.6})
        return temp_c

def updatetherm():
    with open("/home/pi/Desktop/Interface/temp.txt") as f:
        datat = f.read()
    datat = datat.split('\n')
    dt = [row.split(' ')[0] for row in datat]
    xt = [row.split(' ')[1] for row in datat]
    yt = [row.split(' ')[2] for row in datat] 
    xt = [str(i) for i in xt]
    yt = [float(i) for i in yt]
    #x = list(map(int, x))
    #y = list(map(int, y))
    #d = plt.plot(xt,yt)
    #d[0].set_ydata(s)
    #ax2.plot(xt,yt,'#f35924')
    #fig.canvas.draw()

def updatesg():
    with open("/home/pi/Desktop/Interface/sg.txt") as f:
        datas = f.read()
    datas = datas.split('\n')
    ds = [row.split(' ')[0] for row in datas]
    xs = [row.split(' ')[1] for row in datas]
    ys = [row.split(' ')[2] for row in datas] 
    #xs = [f(i) for i in x]
    ys = [float(i) for i in ys]
    #x = list(map(int, x))
    #y = list(map(int, y))
    #d = plt.plot(xs,ys)
    #d[0].set_ydata(s)
    #ax.plot(xs,ys,'black')
    #fig.canvas.draw()

def exitbutton():
        GPIO.cleanup()
        root.destroy()
        
def temperaturecontrol():
        temperature= read_temp()
        desired_temperature = 21
        if coldcrush == False:
                if temperature < desired_temperature:
                        heat()
                elif temperature > desired_temperature:
                        cool()
                elif temperature == desired_temperature:
                        shutoff()

def updategui():
    updatesg()
    updatetherm()
    #temperaturecontrol() TURN ON ONCE TEMP CONTROL TESTING IS NECESSARY
    ftemp = open('/home/pi/Desktop/Interface/temp.txt', 'a')
    fsg = open('/home/pi/Desktop/Interface/sg.txt', 'a')

    tempread = str(read_temp())
    sgread = str(read_Sg()) #  TURN ON ONCE HYDROMETER IS FUNCTIONAL
    #sgread = "1.6"
    timeread = str(read_time())
    temperature.set("Current Temperature "+tempread+"°C")
    writetemp = '\n'+timeread + " " + tempread
    ftemp.write(writetemp)
    sg.set("Current Specific Gravity: "+sgread)
    writesg = '\n'+timeread + " " + sgread
    fsg.write(writesg)
    time.set("Current Time: "+timeread)
    root.update()
    root.after(60000,updategui)
    print(read_temp())
    print(read_Sg())
    datetime=timeread.split()
    date=datetime[0]
    print(date)
    timer=datetime[1]
    print(timer)
    tk.Label(root,text=str(read_temp())+"°C",font=("NotoSans-Bold",45),fg='#ff8d00',background='white').grid(row=10, column=1)
    tk.Label(root,text=str(read_Sg()),font=("NotoSans-Bold",45),fg='#ff8d00',background='white').grid(row=10, column=4)
    tk.Label(titleframe,text=str(read_timegui()+"          "),font=("NotoSans-Bold",14),fg='white',background='#ff8d00',compound="center").grid(row=0, column=6)
    #result = firebase.post('/users/1003', {'date':date,'time':timer,'temp':tempread,'desiredtemp':20, 'hydro': sgread})

root = tk.Tk()

#fig = plt.figure(1) GRAPH GUI CODE
#plt.ion()

temperature = tk.StringVar()
sg = tk.StringVar()
time = tk.StringVar()

temperature.set("null")
sg.set("null")


updatetherm()
updatesg()

#plt.plot(xt,yt) COMMENTED CODE BELOW IS GRAPH CODE-FUNCTIONAL BUT ABANDONED
#plt.plot(xs,ys)

#canvas = FigureCanvasTkAgg(fig, master=root)
#plot_widget = canvas.get_tk_widget()
#im = mpimg.imread('webrew.gif')
#ax2.imshow(im,  extent=[0, 400, 0, 300])
#ax2.set_ylabel("Temperature",fontsize=8,color='#f35924')
#ax.set_ylabel("Specific Gravity",fontsize=8,color='black')
#ax.get_xaxis().set_ticks([])
#templeg = mpatches.Patch(color='#f35924', label='Temperature')
#sgleg = mpatches.Patch(color='black', label='Specific Gravity')
#plt.legend(handles=[templeg,sgleg],bbox_to_anchor=(0., 1.02, 1., .102), loc=3,ncol=2, mode="expand", borderaxespad=0.)






def update():
    updatesg()
    updatetherm()
   # plt.plot(xt,yt)
   # plt.plot(xs,ys)
   # d[0].set_ydata(s)
   # fig.canvas.draw()
#img = plt.imread("webrew.gif")
#plot_widget.grid(row=1, column=0)     ABANDONED GRAPHING CODE- FUNCTIONAL 
#imgpath = "icon_lcd.gif"
#img = root.PhotoImage(file=imgpath)
#photos = tk.Label(root, image = img).grid(row=0,column=0)
#photos.image = img
root.resizable(width = False, height = False)
titleframe = tk.Frame(root, bg = "#ff8d00")
titleframe.grid(row=0,column=0, columnspan=80,sticky='ew')
image = tk.PhotoImage(file="/home/pi/Desktop/Interface/icon_lcd.gif")
photo = tk.Label(titleframe,image=image,borderwidth=0)
photo.grid(row=0,column=0)
#titlelabel = tk.Label(root, bg="#ff8d00")
#titlelabel.grid(row=0, column =0, sticky='ew',columnspan=2)
root.grid_rowconfigure(1, minsize=100)
root.grid_rowconfigure(11, minsize=100)
root.grid_columnconfigure(0, minsize=100)
root.grid_columnconfigure(3, minsize=50)
#root.grid_columnconfigure(11, minsize=)
tk.Label(root,text="Temperature",font=("NotoSans-Bold",24),fg="#606859",background="white").grid(row=7, column=1)
tk.Label(root,text="Specific Gravity",font=("NotoSans-Bold",24),fg="#606859",background="white").grid(row=7,column=4)
tk.Label(root,text=str(read_temp())+"°C",font=("NotoSans-Bold",45),fg='#ff8d00',background='white').grid(row=10, column=1)
tk.Label(root,text=str(read_Sg()),font=("NotoSans-Bold",45),fg='#ff8d00',background='white').grid(row=10, column=4)
#tk.Label(root,text="recipe 25.1°C",font=("NotoSans-Bold",20),fg='#ff8d00',background='white').grid(row=11,column=1)
#tk.Label(root,text="recipe 1.58",font=("NotoSans-Bold",20),fg='#ff8d00',background='white').grid(row=11,column=4)
#tk.Label(root,text="Fermentation: 3 days left",font=("NotoSans-Bold",22)).grid(row=12,column=7,columnspan=3)
tk.Label(titleframe,text=str(read_timegui()+"          "),font=("NotoSans-Bold",14),fg='white',background='#ff8d00',compound="center").grid(row=0, column=6)
#im=Image.open("icon_lcd.gif")
#canvas = tk.Canvas(root, width = 800, height = 200)            ABANDONED GRAPHING CODE
#canvas.grid(row=0, column=0)

tk.Button(root,text="Exit",command=exitbutton).grid(row=9, column=0)
root.configure(background='white')
root.title("WeBrew")
root.geometry('800x480')
#plt.imshow(img) ABANDONED GRAPHING CODE
root.after(0,updategui)
root.mainloop()


