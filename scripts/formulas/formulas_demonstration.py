import math
import matplotlib.pyplot as plt

gravity_force = 9.8 # Gravity force on Earth
density = 1.293 # Volumic mass of air on Earth
step = 0.05 # Time between points in seconds

def compute_line_rocket(x0, y0, velocity, angle, wind_speed, wind_angle, friction = None, step = step, gravity_force = gravity_force):
    """
    Generates a dictionary of rocket line data, with or without friction
    Columns: Time since launch (seconds), x position, y position
    
    Parameters: Initial x position (float), Initial y position (float), initial velocity (float), launch angle (float), wind speed (float), wind angle (float), OPTIONAL: friction resistance coefficient (float)
    """
    line = []
    xl = []
    yl = []

    wind_x = wind_speed * math.cos(wind_angle)
    wind_y = wind_speed * math.sin(wind_angle)
    velocity_x = velocity * math.cos(angle) + wind_x
    velocity_y = velocity * math.sin(angle) + wind_y
    
    velocity = math.sqrt(velocity_x * velocity_x + velocity_y * velocity_y)
    angle = math.atan(velocity_y / velocity_x)
    t = 0.0
    y = 1
    if friction == None:      # Compute without friction
        while True:
            x = x0 + velocity * math.cos(angle) * t
            y = y0 + velocity * math.sin(angle) * t - 0.5 * gravity_force * t**2
            if y < 0:
                break
            line.append({"time": t, "x": x, "y": y})
            xl.append(x)
            yl.append(y)
            t += step
    else:                           # Compute with friction
        while True:
            x = x0 + (velocity * math.cos(angle) / friction) * (1 - math.e ** (-1 * friction * t))
            y = y0 + ((velocity * math.sin(angle) / friction) + (gravity_force / friction**2)) * (1 - math.e ** (-1 * friction * t)) - (gravity_force*t) / friction
            if y < 0:
                break
            line.append({"time": t, "x": x, "y": y})
            xl.append(x)
            yl.append(y)
            t += step

    return line, xl, yl

def compute_line_grenade(x0, y0, velocity, angle, friction = None, step = step, gravity_force = gravity_force):
    """
    Generates a list of dictionaries of grenade line data with or without friction
    Columns: Time since launch (seconds), x position, y position
    
    Parameters: Initial x position (float), y position (float), initial velocity (float), launch angle (float), friction resistance coefficient (float)
    """
    line = []
    xl = []
    yl = []

    t = 0.0
    y = 1
    if friction == None:
        while True:
            x = x0 + velocity * math.cos(angle) * t
            y = y0 + velocity * math.sin(angle) * t - 0.5 * 9.8 * t**2
            if y < 0:
                break
            line.append({"time": t, "x": x, "y": y})
            xl.append(x)
            yl.append(y)
            t += step
    else:
        while True:
            x = x0 + (velocity * math.cos(angle) / friction) * (1 - math.e ** (-1 * friction * t))
            y = y0 + ((velocity * math.sin(angle) / friction) + (9.8 / friction**2)) * (1 - math.e ** (-1 * friction * t)) - (9.8*t) / friction
            if y < 0:
                break
            line.append({"time": t, "x": x, "y": y})
            xl.append(x)
            yl.append(y)
            t += step

    return line, xl, yl

def compute_archimedes_velocity(speed, radius):
    """
    Computes the terminal velocity of an object in a fluid
    Parameters: Fluid density (float), object volume (float), gravity force (float)
    """
    return speed - ((math.pi * radius**2) / 2) * density * gravity_force

# line, x, y = compute_line_grenade(0,0,5,45,0.7)
# print(line)
# print(x, y)
# plt.plot(x,y)
# plt.xlabel("x")
# plt.ylabel("y")
# plt.title("Points")
# plt.show()

print(compute_archimedes_velocity(30,2))