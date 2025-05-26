# vehicle_manager.py
import pygame
import random
import time
from config import (SPEEDS, START_X, START_Y, VEHICLES, VEHICLE_TYPES, DIRECTION_NUMBERS,
                    DEFAULT_STOP, STOP_LINES, STOPPING_GAP, MOVING_GAP, SIMULATION_GROUP, VEHICLE_IMAGE_BASE_PATH)


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = SPEEDS[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = START_X[direction][lane]
        self.y = START_Y[direction][lane]
        self.crossed = 0
        # Add vehicle to the appropriate lane list (for dynamic counting)
        VEHICLES[direction][lane].append(self)
        self.index = len(VEHICLES[direction][lane]) - 1

        # Build image path and load vehicle image
        path = VEHICLE_IMAGE_BASE_PATH + direction + "/" + vehicleClass + ".png"
        try:
            self.image = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Error loading image at {path}: {e}")
            self.image = pygame.Surface((50, 30))
            self.image.fill((255, 0, 0))

        # Set the stop coordinate based on the previous vehicle in the lane if present
        if len(VEHICLES[direction][lane]) > 1 and VEHICLES[direction][lane][self.index - 1].crossed == 0:
            prev_vehicle = VEHICLES[direction][lane][self.index - 1]
            if direction == 'right':
                self.stop = prev_vehicle.stop - prev_vehicle.image.get_rect().width - STOPPING_GAP
            elif direction == 'left':
                self.stop = prev_vehicle.stop + prev_vehicle.image.get_rect().width + STOPPING_GAP
            elif direction == 'down':
                self.stop = prev_vehicle.stop - prev_vehicle.image.get_rect().height - STOPPING_GAP
            elif direction == 'up':
                self.stop = prev_vehicle.stop + prev_vehicle.image.get_rect().height + STOPPING_GAP
        else:
            self.stop = DEFAULT_STOP[direction]

        # Adjust starting coordinate for the next vehicle in the lane
        if direction == 'right':
            temp = self.image.get_rect().width + STOPPING_GAP
            START_X[direction][lane] -= temp
        elif direction == 'left':
            temp = self.image.get_rect().width + STOPPING_GAP
            START_X[direction][lane] += temp
        elif direction == 'down':
            temp = self.image.get_rect().height + STOPPING_GAP
            START_Y[direction][lane] -= temp
        elif direction == 'up':
            temp = self.image.get_rect().height + STOPPING_GAP
            START_Y[direction][lane] += temp

        SIMULATION_GROUP.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        # Import signals to check current signal status
        import signals
        if self.direction == 'right':
            if self.crossed == 0 and self.x + self.image.get_rect().width > STOP_LINES[self.direction]:
                self.crossed = 1
            if ((self.x + self.image.get_rect().width <= self.stop or self.crossed == 1 or (
                    signals.currentGreen == 0 and signals.currentYellow == 0))
                    and (self.index == 0 or self.x + self.image.get_rect().width < (
                            VEHICLES[self.direction][self.lane][self.index - 1].x - MOVING_GAP))):
                self.x += self.speed
        elif self.direction == 'down':
            if self.crossed == 0 and self.y + self.image.get_rect().height > STOP_LINES[self.direction]:
                self.crossed = 1
            if ((self.y + self.image.get_rect().height <= self.stop or self.crossed == 1 or (
                    signals.currentGreen == 1 and signals.currentYellow == 0))
                    and (self.index == 0 or self.y + self.image.get_rect().height < (
                            VEHICLES[self.direction][self.lane][self.index - 1].y - MOVING_GAP))):
                self.y += self.speed
        elif self.direction == 'left':
            if self.crossed == 0 and self.x < STOP_LINES[self.direction]:
                self.crossed = 1
            if ((self.x >= self.stop or self.crossed == 1 or (signals.currentGreen == 2 and signals.currentYellow == 0))
                    and (self.index == 0 or self.x > (
                            VEHICLES[self.direction][self.lane][self.index - 1].x + VEHICLES[self.direction][self.lane][
                        self.index - 1].image.get_rect().width + MOVING_GAP))):
                self.x -= self.speed
        elif self.direction == 'up':
            if self.crossed == 0 and self.y < STOP_LINES[self.direction]:
                self.crossed = 1
            if ((self.y >= self.stop or self.crossed == 1 or (signals.currentGreen == 3 and signals.currentYellow == 0))
                    and (self.index == 0 or self.y > (
                            VEHICLES[self.direction][self.lane][self.index - 1].y + VEHICLES[self.direction][self.lane][
                        self.index - 1].image.get_rect().height + MOVING_GAP))):
                self.y -= self.speed


def generate_vehicles():
    while True:
        vehicle_type = random.choices( population = [0, 1, 2, 3, 4],
                                       weights = [0.4, 0.05, 0.03, 0.5, 0.07],  # 1% chance of ambulance
                                       k = 1)[0]
        lane_number = random.randint(1, 2)  # Using lane indices 1 or 2
        temp = random.randint(0, 99)
        direction_number = 0
        dist = [25, 50, 75, 100]
        if temp < dist[0]:
            direction_number = 0
        elif temp < dist[1]:
            direction_number = 1
        elif temp < dist[2]:
            direction_number = 2
        elif temp < dist[3]:
            direction_number = 3
        Vehicle(lane_number, VEHICLE_TYPES[vehicle_type], direction_number, DIRECTION_NUMBERS[direction_number])
        time.sleep(1)