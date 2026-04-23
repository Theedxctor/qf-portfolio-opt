# scripts/train_agent.py
import os

from stable_baselines3 import PPO

from scripts.portfolio_env import PortfolioEnv


def train():
    # 1. Initialize the Environment
    env = PortfolioEnv()

    # 2. Setup the Model
    # 'MlpPolicy' means a standard Multi-Layer Perceptron (Neural Network)
    # verbose=1 shows us the progress in the terminal
    model = PPO("MlpPolicy", env, verbose=1, device="cpu")

    print("🚀 Starting training... This might take a few minutes.")

    # 3. Train for 50,000 steps (cycles through your data multiple times)
    model.learn(total_timesteps=1000)

    # 4. Save the trained model
    os.makedirs("models", exist_ok=True)
    model.save("models/ppo_portfolio_manager")

    print("✅ Training complete! Model saved to models/ppo_portfolio_manager.zip")


if __name__ == "__main__":
    train()
