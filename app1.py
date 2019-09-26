# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import dash_table
from dash.dependencies import Input, Output
import datetime
import os
import mysql.connector as sql



external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                requests_pathname_prefix='/app1/')

datenow= datetime.datetime.now()


#--- database loading data---#
def get_data(data_select,columns_select):
    # create connect
    mydb = sql.connect(host='10.120.14.100', database='hospitaldb', user='hp', password='')
    db_cursor = mydb.cursor(buffered=True)

    #get record
    db_cursor.execute(data_select)
    resoult = db_cursor.fetchall()

    # get columns_name
    db_cursor.execute(columns_select)
    columns_name = [column[0] for column in db_cursor.fetchall()]

    # turn to dataframe
    ctdata = pd.DataFrame(resoult,columns=columns_name)

    # close connect
    mydb.close()

    # --- ETL for chart---------------------------------------------------------#

    # ---上午&下午 -> AM&PM -> timetype ---#
    ctdata['BDATE'] = ctdata['BDATE'].str.replace('上午', 'AM').str.replace('下午', 'PM')
    ctdata['BDATE'] = pd.to_datetime(ctdata['BDATE'], format="%Y/%m/%d %p %I:%M:%S")
    ctdata['EDATE'] = ctdata['EDATE'].str.replace('上午', 'AM').str.replace('下午', 'PM')
    ctdata['EDATE'] = pd.to_datetime(ctdata['EDATE'], format="%Y/%m/%d %p %I:%M:%S")
    # ---上午&下午 -> AM&PM -> timetype ---#
    # ---create Spend time ---#
    ctdata['second'] = ctdata['EDATE'] - ctdata['BDATE']
    ctdata['second'] = ctdata['second'].dt.total_seconds()  # time to second
    # ---create Spend time ---#

    # ---create Check YEAR & MONTH & DAY ---#
    ctdata['CDATE'] = ctdata['CDATE'].str.replace('上午', 'AM').str.replace('下午', 'PM')
    ctdata['CDATE'] = pd.to_datetime(ctdata['CDATE'], format="%Y/%m/%d %p %I:%M:%S")
    ctdata['YEAR'] = pd.DatetimeIndex(ctdata['CDATE']).year
    ctdata['MONTH'] = pd.DatetimeIndex(ctdata['CDATE']).month
    ctdata['DAY'] = pd.DatetimeIndex(ctdata['CDATE']).day
    # ---create Check YEAR & MONTH & DAY ---#

    ctdata = ctdata[ctdata['AGE'] <= 100]  # remove over 100 years old
    ctdata = ctdata[(ctdata['second'] >= 300) & (ctdata['second'] <= 6000)]  # take 300~ 6000 second record
    # ctdata = ctdata.dropna() # remove NULL values

    # --- ETL for chart---------------------------------------------------------#
    df = ctdata[['YEAR', 'MONTH', 'DAY', 'ITEM', 'MODEL_NAME', 'AMOUNT', 'IO', 'SEX', 'AGE', 'second']]
    df = pd.DataFrame(df)

    return df

#--- database loading data---#


#--- loading data---#

df = get_data('SELECT * FROM  CT;', "SHOW columns FROM CT")
available_ITEM = df['ITEM'].unique()
available_MONTH = df['MONTH'].unique()
vailable_YEAR = df['YEAR'].unique()



#--- query data ---#


DAYMODEL_NAME = df.groupby(['YEAR','MONTH','DAY','MODEL_NAME'],as_index=False ).agg({'second':['mean', 'count','sum'],'AMOUNT':['mean', 'count','sum'],'AGE':['mean', 'count','sum']})
MONTHMODEL_NAME = df.groupby(['YEAR','MONTH','MODEL_NAME'],as_index=False ).agg({'second':['mean', 'count','sum'],'AMOUNT':['mean', 'count','sum'],'AGE':['mean', 'count','sum']})

DAYAGE = df.groupby(['YEAR','MONTH','DAY','SEX'],as_index=False ).agg({'second':['mean', 'count','sum'],'AMOUNT':['mean', 'count','sum'],'AGE':['mean', 'count','sum']})
MONTHAGE = df.groupby(['YEAR','MONTH','SEX'],as_index=False ).agg({'second':['mean', 'count','sum'],'AMOUNT':['mean', 'count','sum'],'AGE':['mean', 'count','sum']})

DAYIO = df.groupby(['YEAR','MONTH','DAY','IO'],as_index=False ).agg({'second':['mean', 'count','sum'],'AMOUNT':['mean', 'count','sum'],'AGE':['mean', 'count','sum']})
MONTHIO = df.groupby(['YEAR','MONTH','IO'],as_index=False ).agg({'second':['mean', 'count','sum'],'AMOUNT':['mean', 'count','sum'],'AGE':['mean', 'count','sum']})

DAYITEM = df.groupby(['YEAR','MONTH','DAY','ITEM'],as_index=False ).agg({'second':['mean', 'count','sum'],'AMOUNT':['mean', 'count','sum'],'AGE':['mean', 'count','sum']})
MONTHITEM = df.groupby(['YEAR','MONTH','ITEM'],as_index=False ).agg({'second':['mean', 'count','sum'],'AMOUNT':['mean', 'count','sum'],'AGE':['mean', 'count','sum']})

# Utime_mean= df.groupby(['YEAR','MONTH','MODEL_NAME'],as_index=False )['second'].mean()
AGES_count = df.groupby(["YEAR","MONTH","AGE",'SEX'])['AGE'].count().reset_index(name="count")


#--- query data ---#



def generate_table(dataframe, max_rows=10):
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

app.layout = html.Div(children=[

    # --- header ---#
    html.Div([
        html.H1(children='CT斷層掃描'),
        # html.Div(children='''''')
    ]),
    # --- header ---#

 #--- year slider --#

    html.Div([
        html.Div(children='''請選擇年份與月份'''),
        dcc.RadioItems(
            id='year-select',
            options=[
                {'label': '2017', 'value': 2017},
                {'label': '2018', 'value': 2018},
                {'label': '2019', 'value': 2019}
            ],
            value=datenow.year,
            labelStyle={'display': 'inline-block'}),
        dcc.Dropdown(
            id='month_select',
            options=[{'label': 'January', 'value': 1},
                     {'label': 'Febuary', 'value': 2},
                     {'label': 'March', 'value': 3},
                     {'label': 'April', 'value': 4},
                     {'label': 'May', 'value': 5},
                     {'label': 'June', 'value': 6},
                     {'label': 'July', 'value': 7},
                     {'label': 'August', 'value': 8},
                     {'label': 'September', 'value': 9},
                     {'label': 'October', 'value': 10},
                     {'label': 'November', 'value': 11},
                     {'label': 'December', 'value': 12},
            ], value=6, style={'width': '30%', 'display': 'inline-block'}
        )
    ],className='row'),

    #--- year slider --#


    # --- columns header ---#
    html.Div([
        html.H4(children='檢查項目統計表'),
        # html.Div(children='''''')
    ]),
    # --- columns header ---#

    # --- dropdown ---#
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='two-x_selected-value',
                options=[{'label': i, 'value': i} for i in DAYITEM['ITEM'].unique()],
                value=79993
            ),
        ], style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='two-y_selected-value',
                options=[{'label': i, 'value': i} for i in DAYITEM['ITEM'].unique()],
                value=79994
            ),
        ], style={'width': '30%', 'float': 'left', 'display': 'inline-block'}),
    ], className="eleven columns"),
    # --- dropdown ---#


 # --- two chart --- #
    html.Div([
        #--- bar chart ---#
        html.Div([
            html.Div([dcc.Graph(id='bar-graphic',)]),
            ], className="six columns"),
        #--- bar chart ---#
        #--- line chart ---#
        html.Div([
            html.Div([dcc.Graph(id='line-graphic',)]),
        ], className="six columns"),
        #--- line chart ---#
    ], className="row"),
 # --- two chart  --- #

 # ---two pie chart --- #
    html.Div([
        # --- pie chart ---#
        html.Div([
            html.Div([dcc.Graph(id='pie-graphic')]),
        ], className="six columns"),
        # --- pie chart ---#
        # --- pie2 chart ---#
        html.Div([
            html.Div([dcc.Graph(id='pie2-graphic', )]),
        ], className="six columns"),
        # --- pie2 chart ---#
    ], className="row"),
 # ---two pie chart --- #

    # --- columns header ---#
    html.Div([
        html.H3(children='使用年齡統計表'),
        # html.Div(children='''''')
    ]),
    # --- columns header ---#

 # --- bar chart --- #
    html.Div([
            dcc.Graph(id='bar-chart-graph')
    ], className="eleven columns"),
 # --- bar chart --- #

 # --- general table --- #
    html.Div([
            html.H4(children='醫療檢查資料表'),

            dash_table.DataTable(
                css=[{
                    'selector': '.dash-cell div.dash-cell-value',
                    'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                }],

                id='table',
                columns=[{"name": i, "id": i} for i in df.columns],
                data=df.to_dict('records'),
                fixed_rows={'headers': True, 'data': 0 },
                style_cell={'width': '70px'},
                sort_action='native',
                filter_action="native"
            ),

    ], className="eleven columns"),
 # --- general table --- #
])


#  -------------------  ------------------- update function -------------------  ------------------- #
# ------------------- update two chart ------------------- #
# --- update bar chart---#
@app.callback(
    Output('bar-graphic', 'figure'),
    [Input('year-select', 'value'),
     Input('month_select','value'),
     Input('two-x_selected-value', 'value'),
     Input('two-y_selected-value', 'value')]
)
def update_graph(year_select,month_select,x_selected,y_selected):
    dff = DAYITEM[(DAYITEM["YEAR"] == year_select) & (DAYITEM["MONTH"] == month_select) & (DAYITEM['ITEM']==x_selected)]
    dff1 = DAYITEM[(DAYITEM["YEAR"] == year_select) & (DAYITEM["MONTH"] == month_select) & (DAYITEM['ITEM']==y_selected)]
    trace1 = go.Scatter(x=dff["DAY"], y=dff["AMOUNT"]['sum'], name=x_selected)
    trace2 = go.Scatter(x=dff1["DAY"], y=dff1["AMOUNT"]['sum'], name=y_selected)

    return {
        'data': [trace1,trace2],
        "layout": go.Layout(title=f"每日費用",

                            xaxis={'title': "日期", 'titlefont': {'color': 'black', 'size': 14},
                                   'tickfont': {'size': 9, 'color': 'black'}},
                            yaxis={'title': "費用", 'titlefont': {'color': 'black', 'size': 14, },
                                   'tickfont': {'color': 'black'}})}
# --- update bar chart---#
# --- update line chart---#
@app.callback(
    Output('line-graphic', 'figure'),
    [Input('year-select', 'value'),
     Input('month_select','value'),
     Input('two-x_selected-value', 'value'),
     Input('two-y_selected-value', 'value')]
)
def update_graph(year_select,month_select,x_selected,y_selected):
    dff = DAYITEM[(DAYITEM["YEAR"] == year_select) & (DAYITEM["MONTH"] == month_select) & (DAYITEM['ITEM']==x_selected)]
    dff1 = DAYITEM[(DAYITEM["YEAR"] == year_select) & (DAYITEM["MONTH"] == month_select) & (DAYITEM['ITEM']==y_selected)]
    trace1 = go.Scatter(x=dff["DAY"], y=dff["second"]['sum'], name=x_selected)
    trace2 = go.Scatter(x=dff1["DAY"], y=dff1["second"]['sum'], name=y_selected)

    return {
        'data': [trace1,trace2],
        "layout": go.Layout(title=f"每日時間",

                            xaxis={'title': "日期", 'titlefont': {'color': 'black', 'size': 14},
                                   'tickfont': {'size': 9, 'color': 'black'}},
                            yaxis={'title': "時間", 'titlefont': {'color': 'black', 'size': 14, },
                                   'tickfont': {'color': 'black'}})}
# --- update line chart---#
# ------------------- update two chart ------------------- #


# ------------------- update two pie chart ------------------- #
@app.callback(
    Output('pie-graphic', 'figure'),
    [Input('year-select', 'value'),
     Input('month_select','value')]
)
def update_graph(month_select,year_select):
    return {
        "data": [go.Pie(labels=MONTHITEM["ITEM"].unique().tolist(), values= MONTHITEM[(MONTHITEM['YEAR'] == month_select) & (MONTHITEM['MONTH'] == year_select)]["second"]['mean'].tolist(),
                        marker={'colors': ['#EF963B', '#C93277', '#349600', '#EF533B', '#57D4F1']}, textinfo='label')],
        "layout": go.Layout(title=f"使用時間: 平均", margin={"l": 100, "r": 100, },
                            legend={"x": 1, "y": 0.7})}

@app.callback(
    Output('pie2-graphic', 'figure'),
    [Input('year-select', 'value'),
     Input('month_select','value')]
)
def update_graph(month_select,year_select):
    return {
        "data": [go.Pie(labels=MONTHITEM["ITEM"].unique().tolist(), values= MONTHITEM[(MONTHITEM['YEAR'] == month_select) & (MONTHITEM['MONTH'] == year_select)]["second"]['sum'].tolist(),
                        marker={'colors': ['#EF963B', '#C93277', '#349600', '#EF533B', '#57D4F1']}, textinfo='label')],
        "layout": go.Layout(title=f"使用時間: 總計", margin={"l": 100, "r": 100, },
                            legend={"x": 1, "y": 0.7})}
# ------------------- update  two pie chart ------------------- #


# --- update bar chart---#
@app.callback(
    Output('bar-chart-graph', 'figure'),
    [Input('year-select', 'value'),
     Input('month_select','value')]
)
def update_graph(year_select,month_select):
    dff = AGES_count[(AGES_count["YEAR"] == year_select) & (AGES_count["MONTH"] == month_select)]
    dfM = dff[dff["SEX"] == 'M']
    dfF = dff[dff["SEX"] == 'F']
    trace1 = go.Bar(x=dfM["AGE"], y=dfM["count"], name="Male")
    trace2 = go.Bar(x=dfF["AGE"], y=dfF["count"], name="Female")

    return {
        'data': [trace1, trace2],
        "layout": go.Layout(title=f"各年齡層男女使用比例",

                            xaxis={'title': "年齡", 'titlefont': {'color': 'black', 'size': 14},
                                   'tickfont': {'size': 9, 'color': 'black'}},
                            yaxis={'title': "人數", 'titlefont': {'color': 'black', 'size': 14, },
                                   'tickfont': {'color': 'black'}})}
# --- update bar chart---#

#  -------------------  ------------------- update function -------------------  ------------------- #

