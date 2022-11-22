import numpy as np
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

def mesh_grid(res_x, res_y, x_offset, y_offset):
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

    scatter = fig.data[0]
    colors = ['#a3a7e4'] * 100
    scatter.marker.color = colors
    scatter.marker.size = [10] * 100
    fig.layout.hovermode = 'closest'

    # create our callback function
    def update_point(trace, points, selector):
        c = list(scatter.marker.color)
        s = list(scatter.marker.size)
        for i in points.point_inds:
            c[i] = '#bae2be'
            s[i] = 20
            with fig.batch_update():
                scatter.marker.color = c
                scatter.marker.size = s

    scatter.on_click(update_point)
    fig.show()

#mesh_grid(3, 3, 0, 0)

w_cnc = 0.79
h_cnc = 0.90
x_offset = 0
y_offset = 0
res_x = 3
res_y = 3
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


fig1 = go.Figure(go.Scatter(x= x_cc, y= y_cc, mode = "markers"))
fig2 = go.Figure(go.Scatter(x=[x_offset, w_cnc, w_cnc, x_offset, x_offset], y=[y_offset, y_offset, h_cnc, h_cnc, y_offset], fill="tonext"))
# fig3 = go.Figure(
#     go.Scatter(x=[0, w_cnc, w_cnc, 0, 0], y=[0, 0, h_cnc, h_cnc, 0],
#                fill="tonext"))
fig = go.Figure(data= fig1.data + fig2.data )
fig.update_xaxes(range=[0.0, 1])
fig.update_traces(marker={'size': 15})
fig.update_yaxes(range=[0, 1])
fig.update_layout(template="plotly_dark")

scatter = fig1.data[0]
colors = ['#a3a7e4'] * 100
scatter.marker.color = colors
scatter.marker.size = [10] * 100
fig1.layout.hovermode = 'closest'

# create our callback function
def update_point(trace, points, selector):
    c = list(scatter.marker.color)
    s = list(scatter.marker.size)
    for i in points.point_inds:
        c[i] = '#bae2be'
        s[i] = 20
        with fig1.batch_update():
            scatter.marker.color = c
            scatter.marker.size = s

scatter.on_click(update_point)
fig.show()

