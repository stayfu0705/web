# -*- coding: utf-8 -*-
import dash
import dash_html_components as html
import dash_table
import datetime
from etl import get_data

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__,
                external_stylesheets=external_stylesheets,
                requests_pathname_prefix='/app3/')

datenow= datetime.datetime.now()



df = get_data('SELECT * FROM  result;', "SHOW columns FROM result")

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

 # --- general table --- #
    html.Div([
            html.H4(children='檢查時間預測表'),

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
                filter_action="native",
                style_table={'height': '250px'}
            ),

    ], className="eleven columns"),
 # --- general table --- #
])

