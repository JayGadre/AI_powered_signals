# signals.py
import time
import threading
from config import (
    DEFAULT_GREEN, DEFAULT_RED, DEFAULT_YELLOW,
    NO_OF_SIGNALS, DEFAULT_STOP,
    DIRECTION_NUMBERS, VEHICLES
)
from Backend.CSP import TrafficCSP

# module‐level globals
signals = []
currentGreen = 0
currentYellow = 0  # 0 = green phase; 1 = yellow phase
nextGreen = 1
csp_solver = TrafficCSP()

# --- Manual override flag ---
manual_override = None


def set_manual_override(dir_index):
    global manual_override
    manual_override = dir_index


def clear_manual_override():
    global manual_override
    manual_override = None


class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.dynamic_green = green
        self.signalText = ""


def initialize_signals():
    """Reset all signals to default timings."""
    global signals
    signals = []
    for i in range(NO_OF_SIGNALS):
        ts = TrafficSignal(DEFAULT_RED, DEFAULT_YELLOW, DEFAULT_GREEN[i])
        signals.append(ts)
    return signals


def ambulance_waiting_direction():
    """Return the index of any lane with a waiting ambulance, else None."""
    for i in range(NO_OF_SIGNALS):
        dname = DIRECTION_NUMBERS[i]
        for lane in VEHICLES[dname].values():
            for v in lane:
                if getattr(v, 'vehicleClass', '') == 'ambulance' and v.crossed == 0:
                    return i
    return None


def update_values():
    """Decrement the active signal's timer, others count down red."""
    global currentGreen, currentYellow
    for i in range(NO_OF_SIGNALS):
        if i == currentGreen:
            if currentYellow == 0:
                if signals[i].green > 0:
                    signals[i].green -= 1
                else:
                    signals[i].green = 0
            else:
                signals[i].yellow -= 1


def count_waiting_vehicles():
    counts = []
    for d in ['right', 'down', 'left', 'up']:
        c = 0
        for lane_key, lane_list in VEHICLES[d].items():
            if isinstance(lane_key, int):
                c += sum(1 for v in lane_list if v.crossed == 0)
        counts.append(c)
    return counts


def adjust_signal_times():
    waiting = count_waiting_vehicles()
    greens = csp_solver.calculate_green_times(waiting)
    for i in range(NO_OF_SIGNALS):
        signals[i].dynamic_green = greens[i]


def handle_manual_override():
    """Helper function to handle manual override mode"""
    global currentGreen, currentYellow, nextGreen

    mo = manual_override
    currentGreen = mo
    currentYellow = 0

    # Reset all signals
    for i in range(NO_OF_SIGNALS):
        if i != mo:
            signals[i].red = DEFAULT_RED
            signals[i].yellow = DEFAULT_YELLOW

    # Hold here until manual override is cleared
    while manual_override == mo:
        time.sleep(0.1)

    # Once turned off, transition to yellow first
    currentYellow = 1
    signals[mo].yellow = DEFAULT_YELLOW
    direction = DIRECTION_NUMBERS[mo]

    # Set stop lines for vehicles
    for lane in VEHICLES[direction].values():
        for v in lane:
            v.stop = DEFAULT_STOP[direction]

    # Run yellow phase
    while signals[mo].yellow > 0:
        signals[mo].yellow -= 1
        time.sleep(1)

    # Now go to next signal
    signals[mo].yellow = DEFAULT_YELLOW  # Reset yellow for future use
    currentGreen = 0  # Default to first signal
    nextGreen = 1
    currentYellow = 0

    # Reset all signals
    initialize_signals()

    # Set red times for all other signals
    for i in range(NO_OF_SIGNALS):
        if i != currentGreen:
            signals[i].red = signals[currentGreen].dynamic_green + signals[currentGreen].yellow

    return True  # Return True to indicate override was handled


def run_signals():
    global currentGreen, currentYellow, nextGreen, signals

    while True:
        # --- Check manual override at the beginning of each iteration ---
        if manual_override is not None:
            if handle_manual_override():
                continue

        # --- Check for ambulance override ---
        amb = ambulance_waiting_direction()
        if amb is not None:
            currentGreen = amb
            currentYellow = 0
            signals[amb].green = signals[amb].dynamic_green
            for i in range(NO_OF_SIGNALS):
                if i != amb:
                    signals[i].red = DEFAULT_RED
                    signals[i].yellow = DEFAULT_YELLOW

            # Hold until ambulance gone
            while ambulance_waiting_direction() == amb:
                # Check for manual override during ambulance handling
                if manual_override is not None:
                    if handle_manual_override():
                        break
                update_values()
                time.sleep(1)

            # If we broke out due to manual override, continue to next loop
            if manual_override is not None:
                continue

            # Otherwise transition to yellow first
            currentYellow = 1
            signals[amb].yellow = DEFAULT_YELLOW
            direction = DIRECTION_NUMBERS[amb]

            # Set stop lines for vehicles
            for lane in VEHICLES[direction].values():
                for v in lane:
                    v.stop = DEFAULT_STOP[direction]

            # Run yellow phase
            while signals[amb].yellow > 0:
                # Check for manual override during yellow
                if manual_override is not None:
                    if handle_manual_override():
                        break
                signals[amb].yellow -= 1
                time.sleep(1)

            # If manual override was triggered during yellow, continue to next loop
            if manual_override is not None:
                continue

            # Reset to normal operation
            initialize_signals()
            currentGreen = 0
            nextGreen = 1
            currentYellow = 0
            continue

        # --- Normal CSP‐driven cycle ---
        adjust_signal_times()
        signals[currentGreen].green = signals[currentGreen].dynamic_green

        # Green phase
        while signals[currentGreen].green > 0:
            # Check for manual override during green phase
            if manual_override is not None:
                if handle_manual_override():
                    break
            update_values()
            time.sleep(1)

        # If we broke out due to manual override, continue to next loop
        if manual_override is not None:
            continue

        # Yellow phase
        currentYellow = 1
        direction = DIRECTION_NUMBERS[currentGreen]
        for lane in VEHICLES[direction].values():
            for v in lane:
                v.stop = DEFAULT_STOP[direction]

        while signals[currentGreen].yellow > 0:
            # Check for manual override during yellow phase
            if manual_override is not None:
                if handle_manual_override():
                    break
            update_values()
            time.sleep(1)

        # If we broke out due to manual override, continue to next loop
        if manual_override is not None:
            continue

        # Reset this signal's timers
        signals[currentGreen].yellow = DEFAULT_YELLOW
        signals[currentGreen].red = DEFAULT_RED

        # Advance to next signal
        currentGreen = nextGreen
        nextGreen = (currentGreen + 1) % NO_OF_SIGNALS
        for i in range(NO_OF_SIGNALS):
            if i != currentGreen:
                signals[i].red = signals[currentGreen].dynamic_green + signals[currentGreen].yellow
        currentYellow = 0


def start_signal_thread():
    thread = threading.Thread(target=run_signals, daemon=True)
    thread.start()