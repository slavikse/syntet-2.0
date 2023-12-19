import gymnasium as gym
env = gym.make("LunarLander-v2", render_mode="human")
observation = env.reset()

# gamma = 0.99  # Discount factor for past rewards
# max_steps_per_episode = 10000

for _ in range(1000):
  # 0..3
  action = env.action_space.sample()
  observation, reward, terminated, truncated, info = env.step(action)

  if terminated or truncated:
    observation, info = env.reset()

env.close()
