import base64
import json
import re
import time

import dash_bootstrap_components as dbc
import dash_daq as daq
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scipy.interpolate as sc
from dash import Dash, dcc, html, ctx
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

## Variables
portname = '/dev/tty.usbmodem2101'

movespeed = " F9000"
probespeed = " F600"
sol_ON = "M08\n"
sol_OFF = "M09\n"
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}


## Initiate program
# Searching for connected Arduino serial port

# s = serial.Serial(portname, 115200)
# print("Connected correctly.\nStarting up DocumeNDT firmware...")


def stream():
    f = open('dynamic_text_files/grbl.gcode', 'r')
    log = open('dynamic_text_files/logfile.txt', 'a')
    # Wake up grbl
    temp = "\r\n\r\n"
    s.write(temp.encode())
    time.sleep(0.01)  # Wait for grbl to initialize
    s.flushInput()  # Flush startup text in serial input

    # Stream g-code to grbl
    for line in f:
        l = line.strip()  # Strip all EOL characters for consistency
        print('Sending: ' + l)
        tempo = l + '\n'
        s.write(tempo.encode())  # Send g-code block to grbl
        grbl_out = s.readline()  # Wait for grbl response with carriage return
        print(' : ' + str(grbl_out.strip()))
        log.write('Sending: ' + l + '\n')
        log.write(str(grbl_out.strip()) + '\n')

    # # Wait here until grbl is finished to close serial port and file.
    # input("  Press <ENTER> to exit and disable the control firmware.")

    # Close file and serial port
    f.close()
    log.close()
    # s.close()
    return "streamed"


def df_maker():
    temp_lst = []
    # string to search in file
    word = 'PRB:'
    with open(r'dynamic_text_files/logfile.txt', 'r') as fp:
        # read all lines in a list
        line_numbers = []
        lines = fp.readlines()
        fp.close()
        for line in lines:
            # check if string present on a current line
            if line.find(word) != -1:
                line_numbers.append(lines.index(line))
                # print('Line:', line)
                xyz = [float(s) for s in re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?', line)]
                temp_lst.append(xyz)
                # print(xyz)
    df = pd.DataFrame(temp_lst, columns=['x', 'y', 'h (z)', 'scale'])
    # print(df)
    norm_lst = []
    for index, row in df.iterrows():
        z = df['h (z)'][0] - row['h (z)']
        norm_lst.append(z)
    df['norm_z'] = norm_lst
    df.to_csv('probing_points.csv', sep='\t')
    return df, line_numbers


def last_movement_searcher():
    templst = []
    word = 'G90 X'
    with open(r'dynamic_text_files/logfile.txt', 'r') as fp:
        lines = fp.readlines()
        fp.close()
        for line in lines:
            if line.find(word) != -1:
                xy = [float(s) for s in re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?', line)]
                templst.append(xy)
    if len(templst) == 0:
        templst = [[0.0, 0.0, 0.0]]
    else:
        templst = templst
    print(templst)
    return templst


def surface_plot(df):
    x = np.array(df["x"])
    # print(x)
    y = np.array(df["y"])
    # print(y)
    z = -1 * np.array(df["h (z)"])
    # print(z)

    xi = np.linspace(x.min(), x.max(), 100)
    yi = np.linspace(y.min(), y.max(), 100)

    X, Y = np.meshgrid(xi, yi)

    Z = sc.griddata((x, y), z, (X, Y), method='cubic')

    fig = go.Figure(go.Surface(x=xi, y=yi, z=Z))
    fig.update_traces(contours_z=dict(show=True, usecolormap=True,
                                      highlightcolor="limegreen", project_z=True))
    fig.update_layout(title='Wall Surface [mm]')
    fig.update_layout(template="plotly",
                      scene=dict(
                          zaxis=dict(range=[min(z), max(z)])))
    # width=700,
    # margin=dict(r=20, l=10, b=10, t=10))

    # fig.show()
    return fig


app = Dash(__name__,
           external_stylesheets=[dbc.themes.ZEPHYR, dbc.icons.BOOTSTRAP])


app.layout = html.Div([
    html.Div(children=[
        html.H1('Input Data'),
        html.H6(
            'Please paste the input file as downloaded with filename: cc.csv under the folder \"Coordinates_Input\"'),
        dbc.Row(dbc.Col([
            dbc.Button("Generate Grid-Data", id='btn-nclicks-12345',
                       n_clicks=0,
                       color="dark",
                       outline=True),
            html.Div(id='generate-button'),
            html.Div(id='generate-button-output')], width='auto'), justify='center'
        ),
        html.Br(),
        dcc.Graph(id="plot"),

        html.Div([
            dcc.Markdown("""
                ***Current Position:*** 
            """),
            html.Pre(id='click-data', style=styles['pre']),
        ], className='three columns'),

        html.Br(),
        dcc.Graph(id="3dplot"),
        dcc.Interval(id="refresh-graph-interval", disabled=False, interval=5000),

        dbc.Row([
            dbc.Col([
                dbc.Button([html.I(className="bi bi-download"), "  Download CSV"], id='btn-nclicks-12', color='success',
                           outline=True),
                html.Div(id='download-button'), html.Div(id='download-button-output'),
                dcc.Download(id="download-dataframe-xlsx")], width='auto'
            ),
            dbc.Col([dcc.ConfirmDialog(
                id='confirm-delete',
                message='!! Are you sure you want to delete previously recorded data? It is always save to first download the movements before starting with an empty record  !!',
            ),
                dbc.Button('Delete previous datapoints', id='btn-nclicks-13', color='danger', outline=True),
                html.Div(id='delete-button-output'),
            ]),
            dbc.Col([
                dbc.Button([html.I(className="bi bi-arrow-counterclockwise"), "  UNDO"], id='btn-nclicks-123',
                           color='warning', outline=True),
                html.Div(id='undo-button-output'),
            ])
        ], justify='center')
    ], style={'padding': 50, 'flex': 1}),

    ########################################################################################################################

    ########################################################################################################################

    html.Div(children=[
        html.H1('Solenoid'),
        dbc.Row([dbc.Col([
            daq.Knob(
                id="frequency-knob",
                label="Frequency [Hz]",
                value=3,
                color={"gradient": True, "ranges": {"green": [0, 3], "yellow": [3, 7.5], "red": [7.5, 10]}}
            )]
        ),
            dbc.Col(
                daq.Knob(
                    id='hitting-knob',
                    label="Number of Hits [-]",
                    max=1000,
                    value=25
                )

            )]),
        dbc.Row([
            dbc.Col(html.Div(id='slider-output-frequency'), width="auto"),
            dbc.Col(html.Div(id='hitter-output-frequency'), width="auto")
        ], justify="center"),

        # html.Label('Solenoid frequency [Hz]'),
        # dcc.Slider(1, 10, 0.25, value=3, id='slider-input-frequency',
        #            marks={
        #                1: {'label': '1 Hz', 'style': {'color': '#FFFFFF'}},
        #                2: {'label': '2 Hz', 'style': {'color': '#FFFFFF'}},
        #                3: {'label': '3 Hz', 'style': {'color': '#66E188'}},
        #                4: {'label': '4 Hz', 'style': {'color': '#FFFFFF'}},
        #                5: {'label': '5 Hz', 'style': {'color': '#FFFFFF'}},
        #                6: {'label': '6 Hz', 'style': {'color': '#FFFFFF'}},
        #                7: {'label': '7 Hz', 'style': {'color': '#FFFFFF'}},
        #                8: {'label': '8 Hz', 'style': {'color': '#FFFFFF'}},
        #                9: {'label': '9 Hz ', 'style': {'color': '#FFFFFF'}},
        #                10: {'label': '10Hz', 'style': {'color': '#DA0A0A'}}
        #
        #            }
        #            ),
        # html.Div(id='slider-output-frequency'),
        #
        # html.Br(),
        #
        # html.Label('Amount of hits per location:'),
        # dbc.Input(id='input-number-of-hits', type='number', value= 20),
        # html.Div(id='output-number-of-hits'),

        html.Br(),
        dbc.Row([dbc.Col(
            [dbc.Button('Home Machine', id='btn-nclicks-4', n_clicks=0, color='dark', outline=True),
             html.Div(id='home-button'), html.Div(id='home-button-output')], width='auto'
        ),
            dbc.Col([
                dbc.Button('Position Solenoid', id='btn-nclicks-1', n_clicks=0, color='primary', outline=True),
                html.Div(id='position-solenoid-button')], width="auto"
            ),
            dbc.Col([
                dbc.Button('Start Hitting', id='btn-nclicks-2', n_clicks=0, color="success", outline=True),
                html.Div(id='start-solenoid-button'),
                html.Div(id='start-solenoid-output')], width="auto"),

            dbc.Col([
                dcc.ConfirmDialog(
                    id='confirm-set-origin',
                    message='!! Are you certain all axes are set to the origin point for this test? !!',
                ),
                dbc.Button([html.I(className="bi bi-exclamation-triangle"), "  SET ORIGIN"], id='btn-nclicks-200',
                           n_clicks=0,
                           color="danger", outline=False),
                html.Div(id='set-zero-button'),
                html.Div(id='set-zero-output')], width="auto"),

            # dbc.Col([
            #     dbc.Button('STOP', id='btn-nclicks-3', n_clicks=0, color="danger", outline=True),
            #     html.Div(id='stop-button'),
            #     html.Div(id='stop-button-output')
            # ], width="auto")

        ], justify='center'),
        html.Br(),
        html.H1('Controller'),

        html.Br(),
        dbc.Row([
            dbc.Col(
                html.Div(
                    [
                        html.P("X micro-adjustments [mm]"),
                        dbc.Input(type="number", min=-100, max=100, step=1, id="x-adjustment", value=0),
                    ],

                )
            ),
            dbc.Col(
                html.Div(
                    [
                        html.P("Y micro-adjustments [mm]"),
                        dbc.Input(type="number", min=-100, max=100, step=0.5, id="y-adjustment", value=0),
                    ],

                )
            )]
            , justify='center'
        ),
        html.Br(),
        dbc.Row(dbc.Col([
            dbc.Button([html.I(className="bi bi-arrows-move"), "  Move"], id='btn-nclicks-100', n_clicks=0,
                       color="warning",
                       outline=False),
            html.Div(id='move-button'),
            html.Div(id='move-button-output')], width='auto'), justify='center'
        ),

        html.Br(),
        html.Br(),
        html.Br(),

        dbc.Row([
            dbc.CardImg(src='https://www.hiig.de/wp-content/uploads/2016/04/Wall-e.jpg.jpg')
        ]),

        # html.Br(),
        # html.H1('Autonomous Mode'),
        # dbc.Row([
        #     dbc.Col(dcc.Input())
        #
        # ])

    ], style={'padding': 50, 'flex': 1}),  # right side
], style={'display': 'flex', 'flex-direction': 'row'})


@app.callback(
    Output('slider-output-frequency', 'children'),
    Input('frequency-knob', 'value'))
def update_output(value):
    return '{} Hz'.format(np.round(value, 1))


@app.callback(
    Output('hitter-output-frequency', 'children'),
    Input('hitting-knob', 'value'))
def update_output(value):
    return '{} Hits'.format(int(np.round(value, 0)))


@app.callback(
    Output('start-solenoid-output', 'children'),
    Input('btn-nclicks-2', 'n_clicks'),
    Input('hitting-knob', 'value'),
    Input('frequency-knob', 'value')
)
def start_hitting(btn2, n, freq):  # n = number of hits, freq = frequency
    if "btn-nclicks-2" == ctx.triggered_id:
        msg = "Finished hitting cycle"
        f = open('dynamic_text_files/grbl.gcode', 'a')
        number = np.round(n, 1)
        f.truncate(0)  # delete previous code
        t_wait = (1 / (2 * freq)) + 0.001  # for some reason the stream has this constant delay
        for i in range(int(number)):  # start hitting at t_wait interval for i times
            f.write(sol_ON)
            f.write('G4 P' + str(t_wait) + '\n')
            f.write(sol_OFF)
            f.write('G4 P' + str(t_wait) + '\n')
        f.close()
        stream()
        return html.Div(msg)


@app.callback(Output('confirm-set-origin', 'displayed'),
              Input('btn-nclicks-200', 'n_clicks'), )
def display_confirm(btn200):
    if "btn-nclicks-200" == ctx.triggered_id:
        return True
    return False


@app.callback(
    Output('set-zero-output', 'children'),
    Input('btn-nclicks-200', 'n_clicks'),
)
def set_zero(btn):
    if "btn-nclicks-200" == ctx.triggered_id:
        command = "G92 X0 Y0 Z0\n"
        f = open('dynamic_text_files/grbl.gcode', 'a')
        f.truncate(0)  # delete previous code
        f.write(command)
        f.close()
        stream()
        msg = "current position saved as zero"
        return html.Div(msg)


@app.callback(
    Output('home-button-output', 'children'),
    Input('btn-nclicks-4', 'n_clicks')
)
def home(btn4):  # n = number of hits, freq = frequency
    if "btn-nclicks-4" == ctx.triggered_id:
        msg = "Machine has homed"
        f = open('dynamic_text_files/grbl.gcode', 'a')
        f.truncate(0)  # delete previous code
        f.write('G90 Z1 F5000')
        f.write('G90 X0 Y0 F5000\n')
        f.close()
        stream()
        return html.Div(msg)


@app.callback(Output('confirm-delete', 'displayed'),
              Input('btn-nclicks-13', 'n_clicks'), )
def display_confirm(btn13):
    if "btn-nclicks-13" == ctx.triggered_id:
        return True
    return False


@app.callback(
    Output('delete-button-output', 'children'),
    Input('btn-nclicks-13', 'n_clicks')
)
def home(btn13):  # n = number of hits, freq = frequency
    if "btn-nclicks-13" == ctx.triggered_id:
        msg = "All datapoints were deleted.\nReady for new test."
        log = open('dynamic_text_files/logfile.txt', 'a')
        log.truncate(0)
        log.close()

        return html.Div(msg)


@app.callback(
    Output('undo-button-output', 'children'),
    Input('btn-nclicks-123', 'n_clicks')
)
def home(btn123):  # n = number of hits, freq = frequency
    if "btn-nclicks-123" == ctx.triggered_id:
        msg = "Last probe deleted."
        linenumber = df_maker()[1][-1]
        with open("dynamic_text_files/logfile.txt", "r") as f:
            lines = f.readlines()
            print('deleted line: ', lines[linenumber])
        with open("dynamic_text_files/logfile.txt", "w") as f:
            del lines[linenumber]
            for line in lines:
                f.write(str(line))

        return html.Div(msg)


@app.callback(
    Output("plot", "figure"),
    Input('btn-nclicks-12345', 'n_clicks')
)
def home(btn123):  # n = number of hits, freq = frequency
    if "btn-nclicks-12345" == ctx.triggered_id:
        msg = "Done."
        with open("Coordinates_Input/cc.csv") as f:
            df = pd.read_csv(f)

        w_cnc = 0.50
        h_cnc = 0.98
        # # x_offset = float(x_offset)
        # # y_offset = float(y_offset)
        # w = float(width)
        # h = float(height)
        # dx = w / (res_x + 1)
        # dy = h / (res_y + 1)
        #
        # x_lst = [0]
        # for i in range(res_x):
        #     x_cc = dx * (i + 1)
        #     x_lst.append(x_cc)
        # x_lst.append(w)
        # y_lst = [0]
        # for i in range(res_y):
        #     y_cc = dy * (i + 1)
        #     y_lst.append(y_cc)
        # y_lst.append(h)
        #
        # x_cc = []
        # y_cc = []
        # for x in x_lst:
        #     for y in y_lst:
        #         x_cc.append(x)
        #         y_cc.append(y)
        xcc = [float(i) / 1000 for i in df['x'].tolist()]
        ycc = [float(i) / 1000 for i in df['y'].tolist()]

        fig = go.Figure(go.Scatter(x=np.array(xcc), y=np.array(ycc), mode="markers"))
        fig = go.FigureWidget(fig.data)
        # fig.update_xaxes(range=[-0.1, 0.6])
        fig.update_traces(marker={'size': 10})
        fig.add_scatter(x=xcc, y=ycc)
        # fig.update_yaxes(range=[-0.1, 1.1])
        fig.update_layout(template="plotly")
        fig.update_layout(showlegend=False)
        fig.update_yaxes(automargin='left+top+right+bottom')
        fig.update_layout(clickmode='event+select')

        fig.update_traces(marker_size=20)

        # fig.show()
        return fig
    else:
        return {}


@app.callback(
    Output('click-data', 'children'),
    Input('plot', 'clickData'))
def display_click_data(clickData):
    if str(json.dumps(clickData, indent=2)) == "null":
        mssg = "No point has been selected.\nPlease click on a blue dot in order to move"
    else:
        # extract location data from
        txt = json.dumps(clickData, indent=2)
        xtxt = txt.splitlines()[6]
        ytxt = txt.splitlines()[7]
        x = float(xtxt[11:-1]) * 1000
        y = float(ytxt[11:-1]) * 1000
        print('\nSelected/clicked position [x] [y]:')
        print(x, y)

        # Creating GCODE
        f = open('dynamic_text_files/grbl.gcode', 'a')
        f.truncate(0)  # delete previous code
        f.write(sol_OFF)
        f.write("G90 Z0" + movespeed + "\n")  # home z axis
        # f.write('G91 G01 Z20 F500\n')
        movetemp = "G90 X" + str(x) + "Y" + str(y) + movespeed + "\n"
        f.write(movetemp)
        f.close()
        stream()

        mssg = "Arrived at: x = ", x, "   y = ", y, "   [mm]"
    return mssg


# Position solenoid
@app.callback(
    Output('position-solenoid-button', 'children'),
    Input('btn-nclicks-1', 'n_clicks')
)
def hit(btn1):
    if "btn-nclicks-1" == ctx.triggered_id:
        msg = "Solenoid is in position."
        f = open('dynamic_text_files/grbl.gcode', 'a')
        f.truncate(0)  # delete previous code
        f.write(sol_ON)
        f.write(sol_OFF)
        f.write('G38.5 Z150' + probespeed + '\n')  # probe up to 150 mm deep
        f.write('G91 G01 Z-4 F7000\n')  # move back if needed
        f.close()
        stream()
        return html.Div(msg)


# Refresh 3D
@app.callback(
    Output("3dplot", "figure"),
    [Input("refresh-graph-interval", "n_intervals")]
)
def refresh_graph_interval_callback(n_intervals):
    if n_intervals is not None:
        for i in range(0, 5):
            time.sleep(0.01)
            if int(len(df_maker()[0])) == 0:
                x = np.linspace(0, 1, 10)
                y = x
                z = np.array([0] * len(x))

                fig3d = go.Figure(go.Surface(x=x, y=y, z=z))
            elif int(len(df_maker()[0])) == 1:
                x = np.linspace(0, 1, 10)
                y = x
                z = np.array([0] * len(x))

                fig3d = go.Figure(go.Surface(x=x, y=y, z=z))
            elif int(len(df_maker()[0])) == 2:
                x = np.linspace(0, 1, 10)
                y = x
                z = np.array([0] * len(x))

                fig3d = go.Figure(go.Surface(x=x, y=y, z=z))

            else:
                fig3d = surface_plot(df_maker()[0])
            return fig3d
    raise PreventUpdate()


# Dowload dataframe as excel file
@app.callback(
    Output("download-dataframe-xlsx", "data"),
    Input("btn-nclicks-12", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    df = df_maker()[0]
    return dcc.send_data_frame(df.to_csv, "cc.csv")


@app.callback(
    Output("move-button-output", "children"),
    Input("btn-nclicks-100", "n_clicks"),
    Input("x-adjustment", "value"),
    Input("y-adjustment", "value")
)
def mini_move(btn, x, y):  # TODO: add button input + code rest of function
    if "btn-nclicks-100" == ctx.triggered_id:
        current_x = float(last_movement_searcher()[-1][-3])
        current_y = float(last_movement_searcher()[-1][-2])
        print(current_x, current_y)
        X = current_x + x
        Y = current_y + y
        print(X, Y)
        # Creating GCODE
        f = open('dynamic_text_files/grbl.gcode', 'a')
        f.truncate(0)  # delete previous code
        f.write(sol_OFF)
        f.write("G90 Z0" + movespeed + "\n")  # home z axis
        movetemp = "G90 X" + str(X) + " Y" + str(Y) + movespeed + "\n"
        f.write(movetemp)
        f.close()
        stream()
        # mesg = "Arrived at {}, {} [mm]".format(X, Y)
    # return mesg


if __name__ == '__main__':
    app.run_server(debug=True)
