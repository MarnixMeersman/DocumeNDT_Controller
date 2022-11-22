import serial
import plotly.graph_objects as go
from plotly import *
import plotly.express as px
import numpy as np
import pandas as pd

# s = serial.Serial('/dev/tty.usbmodem101', 115200)
print("Starting up DocumeNDT firmware...")

def stream():
    # Open grbl serial port

    # Open g-code file
    f = open('../dynamic_text_files/grbl.gcode', 'r')

    # Wake up grbl
    temp = "\r\n\r\n"
    s.write(temp.encode())
    time.sleep(2)  # Wait for grbl to initialize
    s.flushInput()  # Flush startup text in serial input

    # Stream g-code to grbl
    for line in f:
        l = line.strip()  # Strip all EOL characters for consistency
        print('Sending: ' + l)
        tempo = l + '\n'
        s.write(tempo.encode())  # Send g-code block to grbl
        grbl_out = s.readline()  # Wait for grbl response with carriage return
        print(' : ' + str(grbl_out.strip()))

    # # Wait here until grbl is finished to close serial port and file.
    # input("  Press <ENTER> to exit and disable the control firmware.")

    # Close file and serial port
    f.close()
    # s.close()


def coordinates(res_x, res_y, x_offset, y_offset):
    w_cnc = 0.79
    h_cnc = 0.90
    w = w_cnc - x_offset
    h = h_cnc - y_offset
    dx = w / (res_x+1)
    dy = h / (res_y+1)

    x_lst = []
    for i in range(res_x):
        x_cc = dx * (i + 1) + x_offset
        x_lst.append(x_cc)
    y_lst = []
    for i in range(res_y):
        y_cc = dy * (i + 1) + y_offset
        y_lst.append(y_cc)

    x_cc = []
    y_cc = []
    for x in x_lst:
        for y in y_lst:
            x_cc.append(x)
            y_cc.append(y)


    fig1 = px.scatter(x= x_cc, y= y_cc)
    fig2 = go.Figure(go.Scatter(x=[x_offset, w_cnc, w_cnc, x_offset, x_offset], y=[y_offset, y_offset, h_cnc, h_cnc, y_offset], fill="tonext"))
    # fig3 = go.Figure(
    #     go.Scatter(x=[0, w_cnc, w_cnc, 0, 0], y=[0, 0, h_cnc, h_cnc, 0],
    #                fill="tonext"))
    fig = go.Figure(data= fig1.data + fig2.data )
    fig.update_xaxes(range=[0.0, 1])
    fig.update_traces(marker={'size': 15})
    fig.update_yaxes(range=[0, 1])
    fig.update_layout(template="plotly_dark")
    fig.show()
    return fig, x_cc, y_cc

def surface(x,y,z):
    x= np.array(x)
    y = np.array(y)
    z = np.array(z)
    fig = go.Figure(data=[go.Surface()])
    # fig.update_traces(contours_z=dict(show=True, usecolormap=True,
    #                                   highlightcolor="limegreen", project_z=True))

    fig.update_layout(title='Hitting surface roughness', autosize=True)
    fig.show()
    return fig


