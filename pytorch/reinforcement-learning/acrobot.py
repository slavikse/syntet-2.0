import os
os.environ['KERAS_BACKEND'] = 'torch'
import torch
import keras
import gymnasium as gym
import numpy as np


class Acrobot:
  layers_hidden = 6
  units_hidden = 1000
  learning_rate = 1e-5
  batch_size = 4
  epochs = 3
  units_output = 3

  reward_basic = -1
  reward_penalty = -1

  episodes_hidden = 1000
  episodes_visible = 200
  # rgb_array | human
  render_mode = 'human'

  env = None
  model = None
  # 0 = silent, 1 = progress bar, 2 = one line per epoch
  verbose = 0

  observation = []
  inputs = []
  labels = []


  def __init__(self):
    self.build_model()
    self.replay()


  def build_model(self):
    self.model = keras.Sequential()

    for _ in range(self.layers_hidden):
      self.model.add(keras.layers.Dense(
        units=self.units_hidden,
        activation=keras.activations.relu,
      ))

    self.model.add(keras.layers.Dense(
      units=self.units_output,
      activation=keras.activations.softmax,
    ))

    self.model.compile(
      optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
      loss=keras.losses.Huber(),
      metrics=[
        keras.metrics.MeanSquaredError(),
      ],
    )


  def replay(self):
    self.create_env()
    self.reset_observations()
    self.train_model()


  def create_env(self):
    if self.render_mode == 'rgb_array':
      self.render_mode = 'human'
    elif self.render_mode == 'human':
      self.render_mode = 'rgb_array'
    else:
      raise Exception('The mod is not selected!')

    if self.env:
      self.env.close()
    self.env = gym.make('Acrobot-v1', render_mode=self.render_mode)


  def reset_observations(self):
    self.inputs = []
    self.labels = []

    self.env.reset()
    action = self.env.action_space.sample()
    self.observation, _, _, _, _ = self.env.step(action)


  def train_model(self):
    episodes = self.current_episodes()

    for _ in range(episodes):
      action = self.predict()
      self.observation, reward, terminated, truncated, _ = self.env.step(action)

      if terminated or truncated:
        self.finalize_penalty(action)
      else:
        self.finalize_episode(action, reward)

    self.replay()


  def current_episodes(self):
    if self.render_mode == 'rgb_array':
      return self.episodes_hidden
    if self.render_mode == 'human':
      return self.episodes_visible
    raise Exception('The mod is not correct!')


  def predict(self):
    observations = self.current_observations()
    x = keras.ops.array(np.array([observations]), dtype=torch.float64)
    predictions = self.model.predict(x=x)
    return predictions.argmax()


  def current_observations(self):
    return [self.observation]


  def finalize_penalty(self, action):
    self.finalize_episode(action, self.reward_penalty)
    self.fit_model()
    self.reset_observations()


  def finalize_episode(self, action, reward):
    observations = self.current_observations()
    self.inputs.append(observations)
    rewards = self.get_rewards(action, reward)
    self.labels.append(rewards)


  def get_rewards(self, action, reward):
    rewards = []
    for _ in range(self.units_output):
      rewards.append(self.reward_basic)
    rewards[action] = reward
    return rewards


  def fit_model(self):
    x = keras.ops.array(np.array(self.inputs), dtype=torch.float64)
    y = keras.ops.array(np.array(self.labels), dtype=torch.float16)

    self.model.fit(
      x=x,
      y=y,
      batch_size=self.batch_size,
      epochs=self.epochs,
      verbose=self.verbose,
    )


Acrobot()
