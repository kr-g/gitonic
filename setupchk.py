from importlib.metadata import entry_points

eps = entry_points()

console_scripts = eps["console_scripts"]
