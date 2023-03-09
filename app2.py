import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Load the data from the CSV file
df = pd.read_csv('part-00000-5eaa3dcb-db9b-49f4-baac-602e5f9baaa8-c000.csv')
df = df[df['pass_fail_flag'] == 'F']

# Convert the test_date_time column to datetime
df['test_date_time'] = pd.to_datetime(df['test_date_time'])

# Convert the description column to string
df['description'] = df['description'].astype(str)

# Create the app
app = dash.Dash(__name__)



#     dcc.Graph(id='stacked-bar'),
#     dcc.Dropdown(id='pareto-dropdown',
#                  options=[{'label': i, 'value': i} for i in df['description'].unique()],
#                  value=df['description'].unique()[0]),
#     dcc.Graph(id='pareto-chart')


# Define the layout of the app
app.layout = html.Div([
    dcc.DatePickerRange(
        id='date-picker',
        min_date_allowed=df['test_date_time'].min(),
        max_date_allowed=df['test_date_time'].max(),
        initial_visible_month=df['test_date_time'].min(),
        start_date=df['test_date_time'].min(),
        end_date=df['test_date_time'].max(),
        display_format='MMM Do, YY'
    ),
    dcc.Graph(id='stacked-bar'),
    dcc.Graph(id='pareto-chart')
])



# Define the callback function for the stacked bar chart
@app.callback(Output('stacked-bar', 'figure'),
              [Input('date-picker', 'start_date'),
               Input('date-picker', 'end_date')])
def update_stacked_bar(start_date, end_date):
    filtered_df = df[(df['test_date_time'] >= start_date) & (df['test_date_time'] <= end_date)]
    grouped_df = filtered_df.groupby(['lot_id', 'description']).size().reset_index(name='count')
    grouped_df = grouped_df.sort_values(by=['lot_id', 'count'], ascending=[True, False])
    
    traces = []
    for desc in grouped_df['description'].unique():
        trace = go.Bar(x=grouped_df[grouped_df['description'] == desc]['lot_id'],
                       y=grouped_df[grouped_df['description'] == desc]['count'],
                       name=desc,
                       width=0.5)
        traces.append(trace)

    fig = go.Figure(data=traces)
    fig.update_layout(barmode='stack', xaxis={'tickangle': 45, 'type': 'category'}, yaxis={'title': 'Count'})
    return fig



@app.callback(
    Output('pareto-chart', 'figure'),
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')])
def update_pareto_chart(start_date, end_date):
    filtered_df = df[(df['test_date_time'] >= start_date) & (df['test_date_time'] <= end_date)]
    desc_counts = filtered_df.groupby('description')['lot_id'].nunique()
    total_count = filtered_df['lot_id'].nunique()
    x = desc_counts.index.tolist()
    y = desc_counts.tolist()
    pct = [val/total_count*100 for val in y]
    trace1 = go.Bar(x=x, y=y, name='Cumulative Count')
    trace2 = go.Scatter(x=x, y=pct, name='Cumulative Percentage')
    layout = go.Layout(
        title='Pareto Chart',
        xaxis={'title': 'Description'},
        yaxis={'title': 'Cumulative Count/Percentage'},
        hovermode='closest'
    )
    return {'data': [trace1, trace2], 'layout': layout}




if __name__ == '__main__':
    app.run_server(debug=True)
