import os
os.environ["KERAS_BACKEND"] = "torch"
import keras
import gymnasium as gym
import numpy as np

hidden = 3
units = 8**2
output = 4
epochs = 2
learning_rate = 0.01
batch_size = 15**2
episodes = 1000


def build_model(output):
  model = keras.Sequential()

  for _ in range(hidden):
    model.add(keras.layers.Dense(
      units=units,
      activation=keras.activations.relu,
    ))

  model.add(keras.layers.Dense(
    units=output,
    activation=keras.activations.softmax,
  ))

  model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
    loss=keras.losses.Huber(),
    metrics=[
      keras.metrics.MeanSquaredError(),
    ],
  )

  return model


def create_env():
  # render_mode: human | rgb_array
  env = gym.make('CartPole-v1', render_mode="human")
  observation, info = env.reset()

  # print(env.action_space)
  # print(env.observation_space)

  return env


def training():
  for _ in range(episodes):
    action = env.action_space.sample()
    observation, reward, terminated, truncated, _ = env.step(action)

    # print(observation, reward)

    if terminated or truncated:
      observation, _ = env.reset()


env = create_env()
model = build_model(env.action_space)
training()


# Play Game
# from gymnasium.utils.play import play
# play(
#   gym.make("CarRacing-v2", render_mode="rgb_array"),
#   keys_to_action={
#     "w": np.array([0, 0.7, 0]),
#     "a": np.array([-1, 0, 0]),
#     "s": np.array([0, 0, 1]),
#     "d": np.array([1, 0, 0]),
#     "wa": np.array([-1, 0.7, 0]),
#     "dw": np.array([1, 0.7, 0]),
#     "ds": np.array([1, 0, 1]),
#     "as": np.array([-1, 0, 1]),
#   }, noop=np.array([0,0,0])
# )
