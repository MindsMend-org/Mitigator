# deep_learn.py
from forex_data_loader import DataLoader
from forex_playback_sim import PlaybackSimulator

class DeepLearn:
    def __init__(self):
        self.data_loader = DataLoader("historical_data.csv")
        self.simulator = None

    def load_data(self):
        historical_data = self.data_loader.load_data()
        self.simulator = PlaybackSimulator(historical_data)

    def start_simulation(self):
        if self.simulator:
            try:
                print("Starting simulation...")
                self.simulator.start()
            except KeyboardInterrupt:
                print("Simulation stopped.")
        else:
            print("Data not loaded. Call load_data() first.")

# Usage example
if __name__ == "__main__":
    deep_learn = DeepLearn()
    deep_learn.load_data()
    deep_learn.start_simulation()