import matplotlib.pyplot as plt

# Define the dimensions of the rectangle
x_dim = 10
y_dim = 4

# Create a figure and axis object
fig, ax = plt.subplots()

# Set the axis limits and aspect ratio
ax.set_xlim([0, x_dim])
ax.set_ylim([0, y_dim])
ax.set_aspect('equal')

# Loop through each square in the rectangle
for x in range(x_dim):
    for y in range(y_dim):
        # Calculate the coordinates of the square
        x_coord = x + 0.5
        y_coord = y + 0.5
        
        # Add a rectangle patch to the axis object
        rect = plt.Rectangle((x, y), 1, 1, facecolor='white', edgecolor='black')
        ax.add_patch(rect)
        
        # Map values to specific locations in the rectangle
        if x == 3 and y == 3:
            plt.text(x_coord, y_coord, '4', ha='center', va='center')
        if x == 3 and y == 4:
            plt.text(x_coord, y_coord, '5', ha='center', va='center')

# Show the plot
plt.show()
