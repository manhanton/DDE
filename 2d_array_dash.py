import numpy as np
import pandas as pd
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html

# Read the data from the CSV file
df = pd.read_csv('https://raw.githubusercontent.com/manhanton/DDE/main/AOI_ATBK_KMI700E_FEB23.csv')

# Get the unique lot_id values in the data
lot_ids = df['lot_id'].unique()

# Create the dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(children=[
    html.H1(children='Grid Dashboard'),
    html.Div(children='''
        A dashboard to display the grid data.
    '''),
    # Define the dropdown menu for selecting the lot_id value
    dcc.Dropdown(
        id='lot-dropdown',
        options=[{'label': str(lot_id), 'value': lot_id} for lot_id in lot_ids],
        value=lot_ids[0],
        searchable=True,
        search_value='',
        placeholder='Select a lot_id...',
        clearable=False
    ),
    # Define the dropdown menu for selecting the wafer_id value
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

# Define the callback function for updating the wafer-dropdown based on the selected lot_id value
@app.callback(
    dash.dependencies.Output('wafer-dropdown', 'options'),
    [dash.dependencies.Input('lot-dropdown', 'value')]
)
def update_wafer_dropdown(lot_id):
    # Filter the wafer_ids that contain 'F' in the pass_fail_flag column
    wafer_ids = df[(df['lot_id'] == lot_id) & (df['pass_fail_flag'] == 'F')]['wafer_id'].unique()
    # Return the options for the wafer-dropdown
    return [{'label': str(wafer_id), 'value': wafer_id} for wafer_id in wafer_ids]

    
# Define the callback function for updating the plot and text based on the selected lot_id and wafer_id values
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
    layout = go.Layout(
        xaxis=dict(range=[0, x_max], autorange=False),
        yaxis=dict(range=[0, y_max], autorange=False, scaleanchor="x", scaleratio=1),
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
