import numpy as np
import pandas as pd

# Read the data from the CSV file
df = pd.read_csv('https://raw.githubusercontent.com/manhanton/DDE/main/AOI_ATBK_KMI700E_FEB23.csv')

# Define the lot_id and wafer_id values
lot_id = 'N0PC04EGY000'
# wafer_ids = list(df[df['lot_id']==lot_id]['wafer_id'].unique()) 
wafer_ids = df[(df['lot_id'] == lot_id) & (df['pass_fail_flag'] == 'F')]['wafer_id'].unique()


# Loop over the wafer_id values
for wafer_id in wafer_ids:
    print('Wafer ID:', wafer_id)
    # Select the rows with the specified lot_id and wafer_id
    df_selected = df[(df['lot_id'] == lot_id) & (df['wafer_id'] == wafer_id)]
    # Get the maximum values of die_x and die_y
    x_max = df_selected['die_x'].max()
    y_max = df_selected['die_y'].max()
    # Create a numpy array of zeros to represent the grid
    grid = np.zeros((y_max+1, x_max+1))
    # Fill in the grid with the values from pass_fail_flag
    for i, row in df_selected.iterrows():
        x = row['die_x']
        y = row['die_y']
        if row['pass_fail_flag'] == 'P':
            grid[y, x] = 0
        else:
            grid[y, x] = 1
    # Print the grid with the values
    for row in grid[::-1]:
        for val in row:
            if val == 0:
                print('P', end=' ')
            elif val == 1:
                print('F', end=' ')
            else:
                print('_', end=' ')
        print()
    # Count the total number of 'F' values in the pass_fail_flag column
    f_count = df_selected['pass_fail_flag'].value_counts().get('F', 0)
    if f_count == 0:
        print('Total F:',f_count)
    else:
        print('Total F:', f_count)
    print('-------------------------------')
