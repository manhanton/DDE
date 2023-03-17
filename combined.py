import pandas as pd
import numpy as np
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

# Get the unique lot_id values in the data
lot_ids = df['lot_id'].unique()

# Create the app
app = dash.Dash(__name__)


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
    dcc.Graph(id='pareto-chart'),
    dcc.Dropdown(
        id='lot-dropdown',
        options=[{'label': str(lot_id), 'value': lot_id} for lot_id in lot_ids],
        value=lot_ids[0],
        searchable=True,
        search_value='',
        placeholder='Select a lot_id...',
        clearable=False
    ),
    dcc.Dropdown(
        id='wafer-dropdown',
        value=None
    ),
    # Define the plot for displaying the grid data
    dcc.Graph(
        id='grid-plot'
    ),
    # Define the text for displaying the total number of 'F' values in the pass_fail_flag column
    html.Div(id='f-text')
])

# ------------------------------------------------------------------------------------------------------------


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


@app.callback(
    dash.dependencies.Output('wafer-dropdown', 'options'),
    [dash.dependencies.Input('lot-dropdown', 'value')]
)
def update_wafer_dropdown(lot_id):
    # Filter the wafer_ids that contain 'F' in the pass_fail_flag column
    wafer_ids = df[(df['lot_id'] == lot_id) & (df['pass_fail_flag'] == 'F')]['wafer_id'].unique()
    # Return the options for the wafer-dropdown
    return [{'label': str(wafer_id), 'value': wafer_id} for wafer_id in wafer_ids]


@app.callback(
    [dash.dependencies.Output('wafer-dropdown', 'value'), dash.dependencies.Output('grid-plot', 'figure'), dash.dependencies.Output('f-text', 'children')],
    [dash.dependencies.Input('lot-dropdown', 'value'), dash.dependencies.Input('wafer-dropdown', 'value')]
)
def update_output_div(lot_id, wafer_id):
    if wafer_id is None:
        # Set the wafer_id value to the first value in the options if no value is selected
        wafer_id = df[(df['lot_id'] == lot_id) & (df['pass_fail_flag'] == 'F')]['wafer_id'].unique()[0]
    # Select the rows with the specified lot_id and wafer_id
    df_selected = df[(df['lot_id'] == lot_id) & (df['wafer_id'] == wafer_id)]
    
    # Check if there are any NaN values in the die_x and die_y columns, and replace them with 0 if necessary
    if df_selected['die_x'].isna().any():
        df_selected.loc[df_selected['die_x'].isna(), 'die_x'] = 0
    if df_selected['die_y'].isna().any():
        df_selected.loc[df_selected['die_y'].isna(), 'die_y'] = 0
    
    # Get the maximum values of die_x and die_y
    x_max = round(df_selected['die_x'].max())
    y_max = round(df_selected['die_y'].max())
    # Create a numpy array of zeros to represent the grid
    grid = np.zeros((y_max+1, x_max+1), dtype=int)
    # Fill in the grid with the values from pass_fail_flag
    for i, row in df_selected.iterrows():
        x = int(round(row['die_x']))
        y = int(round(row['die_y']))
        if row['pass_fail_flag'] == 'P':
            grid[y, x] = 0
        else:
            grid[y, x] = 1


    # Create a heatmap trace to display the grid data
    heatmap = go.Heatmap(z=grid[::-1], colorscale=[[0, 'green'], [1, 'red']])
    # Create the layout for the plot
#     layout = go.Layout(
#         xaxis=dict(range=[0, x_max], autorange=False),
#         yaxis=dict(range=[0, y_max], autorange=False, scaleanchor="x", scaleratio=1),
#         margin=dict(l=50, r=50, b=50, t=50),
#         height=500
#     )
    
    layout = go.Layout(
    xaxis=dict(range=[0, x_max], autorange=False, dtick=1), # Add dtick=1
    yaxis=dict(range=[0, y_max], autorange=False, scaleanchor="x", scaleratio=1, dtick=1), # Add dtick=1
    margin=dict(l=50, r=50, b=50, t=50),
    height=500
    )

    
    
    # Create the figure for the plot
    fig = go.Figure(data=[heatmap], layout=layout)
    # Count the total number of 'F' values in the pass_fail_flag column
    f_count = df_selected['pass_fail_flag'].value_counts().get('F', 0)
    # Create the text for displaying the 'F' count
    f_text = f'Total F: {f_count}' if f_count > 0 else 'F equal to 0'
    # Return the updated values for the wafer-dropdown, grid-plot, and f-text
    return wafer_id, fig, f_text

    
if __name__ == '__main__':
    app.run_server(debug=True)
