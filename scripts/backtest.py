import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from stable_baselines3 import PPO

from scripts.portfolio_env import PortfolioEnv


def run_backtest():
    engine = create_engine("postgresql://devdocker:devpassword@localhost:5432/qffun")
    df = pd.read_sql("SELECT * FROM stock_returns_clean ORDER BY date", engine)

    # 1. Use the same split as the training script
    unique_dates = df["date"].unique()
    split_idx = int(len(unique_dates) * 0.8)
    test_df = df[df["date"].isin(unique_dates[split_idx:])]

    # 2. Setup Environment and Load Model
    env = PortfolioEnv(test_df)
    model = PPO.load("models/ppo_portfolio_final")

    obs, _ = env.reset()
    ai_returns = []
    benchmark_returns = []

    print("📈 Running backtest on unseen data...")

    done = False
    while not done:
        # AI decides the weights
        action, _ = model.predict(obs, deterministic=True)

        # Get actual performance from the environment
        obs, reward, done, _, _ = env.step(action)
        ai_returns.append(reward)

        # Benchmark: Equal Weight (1/144 for every stock)
        # We calculate the average return of all stocks for that day
        day_idx = env.current_step - 1
        day_data = env.data[day_idx]
        benchmark_returns.append(np.mean(day_data))

    # 3. Calculate Cumulative Returns
    ai_cum = np.exp(np.cumsum(ai_returns)) - 1
    bench_cum = np.exp(np.cumsum(benchmark_returns)) - 1

    # 4. Plot the Results
    plt.figure(figsize=(12, 6))
    plt.plot(ai_cum, label="AI Portfolio (PPO)", color="blue")
    plt.plot(bench_cum, label="Equal Weighted (Benchmark)", color="gray", linestyle="--")
    plt.title("Final Year Project: AI vs. Market Benchmark")
    plt.xlabel("Days (Test Period)")
    plt.ylabel("Cumulative Return")
    plt.legend()
    plt.grid(True)

    plt.savefig("backtest_results.png")
    print("✅ Backtest complete! Graph saved as 'backtest_results.png'.")


if __name__ == "__main__":
    run_backtest()
