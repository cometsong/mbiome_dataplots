#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import plotly.offline as ply
import plotly.graph_objs as go
from plotly import tools


data_file = '../HLB444_match_HLB444.blasted.100.tsv'
df = pd.read_table(data_file)

pident = df.pident
pct_seqlens = [calc pct of tuples from zip of two columns]

trace1 = go.Scatter(
    x=[1, 2, 3, 4, 5],
    y=[6, 8, 7, 8, 6],
    mode='lines+markers',
    name="'spline'",
    # text=[""],
    # hoverinfo='text+name',
    line=dict(shape='spline')
)

data = [trace1]

layout = dict(
    legend=dict(
        y=0.5,
        traceorder='reversed',
        font=dict( size=16 )
    )
)

fig = go.Figure(data=data, layout=layout)



plotly_config={'showLink': False,
               'linkText': '', # get one.
               'output_type': 'div',
               'displaylogo': False,
               }

ply.plot(fig,
         auto_open='False',
         image='svg',
         image_height='800',
         image_width='800',
         image_filename='line-pident.svg',
         filename='line-pident',
         config=plotly_config,
         )
