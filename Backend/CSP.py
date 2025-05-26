# CSP.py

import math
from Simulation.config import (
    NO_OF_SIGNALS,
    DEFAULT_GREEN, DEFAULT_RED, DEFAULT_YELLOW,
    VEHICLES, DIRECTION_NUMBERS
)

class TrafficCSP:
    def __init__(self):
        self.min_green_time = 5   # Minimum green time (s)
        self.max_green_time = 30  # Maximum green time (s)
        # Total budget = sum of defaults (e.g. 4 × 10 = 40s)
        self.total_time_budget = sum(DEFAULT_GREEN.values())
        # How strongly to prioritize any ambulance‐waiting direction
        self.ambulance_weight_multiplier = 5

    def calculate_green_times(self, vehicle_counts):
        """
        Calculate optimized green times, boosting lanes with ambulances.
        Args:
            vehicle_counts: [# vehicles waiting at right, down, left, up]
        Returns:
            dict of {signal_index: green_seconds}
        """
        # If no vehicles anywhere, just return defaults
        if sum(vehicle_counts) == 0:
            return DEFAULT_GREEN.copy()

        # 1) Base weights from sqrt of queue length
        weights = [math.sqrt(c + 1) for c in vehicle_counts]

        # 2) Detect ambulances waiting in each direction and boost weight
        for i in range(NO_OF_SIGNALS):
            dir_name = DIRECTION_NUMBERS[i]
            amb_count = 0
            # count un‐crossed ambulances in each lane
            for lane_key, lane_list in VEHICLES[dir_name].items():
                for v in lane_list:
                    if getattr(v, 'vehicleClass', '') == 'ambulance' and v.crossed == 0:
                        amb_count += 1
            if amb_count > 0:
                weights[i] *= self.ambulance_weight_multiplier

        # 3) Allocate proportional to weights
        total_weight = sum(weights)
        green_times = {}
        for i in range(NO_OF_SIGNALS):
            if total_weight > 0:
                alloc = (weights[i] / total_weight) * self.total_time_budget
            else:
                alloc = self.total_time_budget / NO_OF_SIGNALS
            # clamp to [min, max]
            green_times[i] = max(self.min_green_time,
                                 min(self.max_green_time, int(alloc)))

        # 4) Fix any rounding drift
        drift = self.total_time_budget - sum(green_times.values())
        if drift != 0:
            # give all leftover to the lane with the most vehicles
            max_dir = vehicle_counts.index(max(vehicle_counts))
            green_times[max_dir] += drift

        return green_times
