# config.py
import pygame

# --- Signal Timing ---
DEFAULT_GREEN = {0: 10, 1: 10, 2: 10, 3: 10}
DEFAULT_RED = 150
DEFAULT_YELLOW = 5
NO_OF_SIGNALS = 4

# --- Vehicle Speeds ---
SPEEDS = {'car': 2.25, 'bus': 2.1, 'truck': 2.0, 'bike': 2.5,'ambulance':3.5}

# --- Starting Coordinates for Vehicles (per direction and lane) ---
START_X = {
    'right': [0, 0, 0],
    'down': [755, 727, 697],
    'left': [1400, 1400, 1400],
    'up': [602, 627, 657]
}
START_Y = {
    'right': [348, 370, 398],
    'down': [0, 0, 0],
    'left': [498, 466, 436],
    'up': [800, 800, 800]
}

# --- Global Vehicles Dictionary ---
# Each direction has three lanes (keys 0,1,2) plus a key 'crossed' (which we won't use for counting)
VEHICLES = {
    'right': {0: [], 1: [], 2: []},
    'down': {0: [], 1: [], 2: []},
    'left': {0: [], 1: [], 2: []},
    'up': {0: [], 1: [], 2: []}
}

# --- Vehicle and Direction Mappings ---
VEHICLE_TYPES = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike',4:'ambulance'}
DIRECTION_NUMBERS = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# --- Signal Display Coordinates ---
SIGNAL_COORDS = [(530, 230), (810, 230), (810, 570), (530, 570)]
SIGNAL_TIMER_COORDS = [(530, 210), (810, 210), (810, 550), (530, 550)]

# --- Stop Lines and Default Stop Coordinates ---
STOP_LINES = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
DEFAULT_STOP = {'right': 580, 'down': 320, 'left': 810, 'up': 545}

# --- Gaps ---
STOPPING_GAP = 15
MOVING_GAP = 15

# --- Image Paths ---
# Adjust these paths according to your folder structure.
VEHICLE_IMAGE_BASE_PATH = "/images/"
BACKGROUND_IMAGE_PATH = "../images/intersection.png"
RED_SIGNAL_IMAGE_PATH = "../images/signals/red.png"
YELLOW_SIGNAL_IMAGE_PATH = "../images/signals/yellow.png"
GREEN_SIGNAL_IMAGE_PATH = "../images/signals/green.png"

# --- Screen Dimensions ---
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 750

# --- Pygame Sprite Group for Simulation ---
pygame.init()
SIMULATION_GROUP = pygame.sprite.Group()
