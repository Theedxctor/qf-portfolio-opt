import gymnasium as gym
import numpy as np
import pandas as pd
from gymnasium import spaces


class PortfolioEnv(gym.Env):
    """
    A Reinforcement Learning Environment for Portfolio Optimization.
    Accepts a pre-cleaned DataFrame and simulates daily trading.
    """

    def __init__(self, df: pd.DataFrame):
        super(PortfolioEnv, self).__init__()

        # 1. Data Transformation
        # Pivot the long-format DB data into a Wide-Format Matrix
        # Rows: Dates, Columns: Assets, Values: Returns
        self.pivot_df = df.pivot(index="date", columns="asset", values="clean_return")
        self.data = self.pivot_df.values.astype(np.float32)

        self.n_assets = self.data.shape[1]
        self.window_size = 30  # AI looks at the previous 30 days of returns

        # 2. Action Space: Continuous weights for each asset [0, 1]
        # The agent outputs 144 numbers; we will normalize them to sum to 1.0
        self.action_space = spaces.Box(low=0, high=1, shape=(self.n_assets,), dtype=np.float32)

        # 3. Observation Space: A 2D matrix of shape (30, 144)
        self.observation_space = spaces.Box(low=-5, high=5, shape=(self.window_size, self.n_assets), dtype=np.float32)

        self.current_step = self.window_size

    def reset(self, seed=None, options=None):
        """Resets the environment to the starting date."""
        super().reset(seed=seed)
        self.current_step = self.window_size
        return self._get_observation(), {}

    def _get_observation(self):
        """Returns the last 30 days of returns as the current state."""
        return self.data[self.current_step - self.window_size : self.current_step]

    def step(self, action):
        """
        Executes one day of trading.
        1. Normalizes actions into portfolio weights.
        2. Calculates the portfolio return for the day.
        3. Returns the next state, reward, and status.
        """
        # 1. Normalize actions so weights sum to 100% (1.0)
        # We add a tiny epsilon (1e-10) to avoid division by zero
        weights = action / (np.sum(action) + 1e-10)

        # 2. Get today's returns for all 144 assets
        day_returns = self.data[self.current_step]

        # 3. Reward = Portfolio Return (Dot product of weights and returns)
        # In a more complex model, this would be the Sharpe Ratio
        portfolio_return = np.dot(weights, day_returns)
        reward = float(portfolio_return)

        # 4. Advance time
        self.current_step += 1
        done = self.current_step >= len(self.data) - 1

        return self._get_observation(), reward, done, False, {}


if __name__ == "__main__":
    # Internal Test Block to verify the environment works locally
    from sqlalchemy import create_engine

    engine = create_engine("postgresql://devdocker:devpassword@localhost:5432/qffun")
    try:
        sample_df = pd.read_sql("SELECT * FROM stock_returns_clean LIMIT 5000", engine)
        env = PortfolioEnv(sample_df)
        obs, _ = env.reset()

        print(f" Environment initialized with {env.n_assets} assets.")
        print(f" Observation shape (Window, Assets): {obs.shape}")

        # Take a dummy step with random weights
        random_action = env.action_space.sample()
        _, reward, done, _, _ = env.step(random_action)
        print(f" Test step reward: {reward:.6f}")
    except Exception as e:
        print(f" Test failed: {e}")
