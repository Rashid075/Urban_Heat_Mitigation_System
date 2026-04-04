import numpy as np

def generate_grid(lat_min, lat_max, lon_min, lon_max, step=2):
    grid = {}

    lat_range = np.arange(lat_min, lat_max, step)
    lon_range = np.arange(lon_min, lon_max, step)

    for lat in lat_range:
        for lon in lon_range:

            
            lat_jitter = lat + np.random.uniform(-0.3, 0.3)
            lon_jitter = lon + np.random.uniform(-0.3, 0.3)

            name = f"{lat_jitter:.2f}_{lon_jitter:.2f}"
            grid[name] = (lat_jitter, lon_jitter)

    return grid