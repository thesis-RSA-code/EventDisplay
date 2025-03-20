


# In cm

DETECTOR_GEOM = {
  'SK': {'height': 3620.0, 'cylinder_radius': 3368.15/2, 'PMT_radius': 25.4}, 
  'HK': {'height': 6575.1, 'cylinder_radius': 6480/2, 'PMT_radius': 25.4}, 
  'HK_realistic': {'height': 6701.41, 'cylinder_radius': 3242.96, 'PMT_radius': 25.4},
  'WCTE': {'height': 338.0, 'cylinder_radius': 369.6/2, 'PMT_radius': 4.0},
  'DEMO': {'height': 558.92 * 2 , 'cylinder_radius': 558.92, 'PMT_radius': 25.4}
}


def track_style(pid):
    match pid:
        case 11:
            color, ls, alpha, lw = 'blue', '-', 1, 2
        case -11:
            color, ls, alpha, lw = 'red', '-', 1, 2
        case 13:
            color, ls, alpha, lw = 'green', '-', 1, 2
        case -13:
            color, ls, alpha, lw = 'purple', '-', 1, 2
        case 22:
            color, ls, alpha, lw = 'orange', '--', 0.3, 0.5
        case 0:
            color, ls, alpha, lw = 'gold', '-', 0.05, 0.2
        case _:
            # Default case – you can adjust the default values as needed.
            color, ls, alpha, lw = 'black', '-', 1, 1
    return color, ls, alpha, lw



