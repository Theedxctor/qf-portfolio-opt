# scripts/portfolio_env.py
import gymnasium as gym
import numpy as np
import pandas as pd
from gymnasium import spaces
from sqlalchemy import create_engine


class PortfolioEnv(gym.Env):
    def __init__(self):
        super(PortfolioEnv, self).__init__()

        # 1. Load your cleaned data from Postgres
        engine = create_engine("postgresql://devdocker:devpassword@localhost:5432/qffun")
        df = pd.read_sql("SELECT * FROM stock_returns_clean", engine)

        # Pivot so columns are assets
        self.data = df.pivot(index="date", columns="asset", values="clean_return").values
        self.n_assets = self.data.shape[1]
        self.window_size = 30  # AI looks at the last 30 days

        # 2. Define Action Space: Continuous weights between 0 and 1
        self.action_space = spaces.Box(low=0, high=1, shape=(self.n_assets,), dtype=np.float32)

        # 3. Define Observation Space: (window_size, n_assets)
        self.observation_space = spaces.Box(low=-5, high=5, shape=(self.window_size, self.n_assets), dtype=np.float32)

        self.current_step = self.window_size

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = self.window_size
        return self._get_observation(), {}

    def _get_observation(self):
        # Return the last 30 days of data
        return self.data[self.current_step - self.window_size : self.current_step]

    def step(self, action):
        # 1. Normalize weights so they sum to 1.0
        weights = action / (np.sum(action) + 1e-10)

        # 2. Calculate today's returns
        returns = self.data[self.current_step]
        portfolio_return = np.dot(weights, returns)

        # 3. Calculate Reward (Sharpe-style: Return / Std Dev)
        # For simplicity in this step, we use portfolio return as the immediate reward
        reward = portfolio_return

        # 4. Advance time
        self.current_step += 1
        done = self.current_step >= len(self.data) - 1

        return self._get_observation(), reward, done, False, {}

        # Save this at the bottom of portfolio_env.py or run it in a notebook


if __name__ == "__main__":
    # Initialize the world
    env = PortfolioEnv()

    # Start the simulation
    obs, _ = env.reset()
    print(f" Success! Initial Observation Shape: {obs.shape}")
    # Should be (30, 155) -> 30 days of history for 155 stocks

    # Take one random step
    random_action = env.action_space.sample()
    next_obs, reward, done, _, _ = env.step(random_action)

    print(f" Reward for random move: {reward:.6f}")
    print(" The environment is ready for training!")
