import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scipy.interpolate as sc
import re
df = pd.read_csv("/Users/marnixmeersman/PycharmProjects/DocumeNDT_Controller/old/testdata.csv")

def df_maker():
    temp_lst = []
    # string to search in file
    word = 'PRB:'
    with open(r'/Users/marnixmeersman/PycharmProjects/DocumeNDT_Controller/dynamic_text_files/logfile.txt', 'r') as fp:
        # read all lines in a list
        lines = fp.readlines()
        for line in lines:
            # check if string present on a current line
            if line.find(word) != -1:
                # print('Line Number:', lines.index(line))
                # print('Line:', line)
                xyz = [float(s) for s in re.findall(r'[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?', line)]
                temp_lst.append(xyz)
                # print(xyz)
    df = pd.DataFrame(temp_lst, columns=['x', 'y', 'h (z)','scale'])
    print(df)
    df.to_csv('probing_points.csv', sep='\t')
    return df

df_maker()


def surface_plot(df):
    x = np.array(df["x"])
    # print(x)
    y = np.array(df["y"])
    # print(y)
    z = np.array(df["h (z)"])
    # print(z)


    xi = np.linspace(x.min(), x.max(), 500)
    yi = np.linspace(y.min(), y.max(), 500)

    X,Y = np.meshgrid(xi,yi)

    Z = sc.griddata((x,y),z,(X,Y), method='cubic')


    fig = go.Figure(go.Surface(x=xi,y=yi,z=Z))
    fig.update_traces(contours_z=dict(show=True, usecolormap=True,
                                      highlightcolor="limegreen", project_z=True))
    fig.update_layout(title='Wall Surface [mm]')

    # fig.show()
    return fig