import os
os.environ['KERAS_BACKEND'] = 'torch'
import torch
import keras
import gymnasium as gym
import numpy as np
import random

# TODO Not completed!

class MountainCar:
  layers_hidden = 6
  units_hidden = 1000
  learning_rate = 1e-5

  reward_basic = -1
  reward_penalty = -1

  epsilon_start = 1.0
  epsilon = epsilon_start
  epsilon_end = 0.001
  epsilon_decay = 0.98

  batch_size = 8
  epochs = 3
  episodes_hidden = 800
  episodes_visible = 300

  # rgb_array | human
  render_mode = 'human'
  env_name = 'Pendulum-v1'
  units_output = 1

  env = None
  model = None
  # 0 = silent, 1 = progress bar, 2 = one line per epoch
  verbose = 0
  previous_observation = []
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

    self.env = gym.make(self.env_name, render_mode=self.render_mode)


  def reset_observations(self):
    self.inputs = []
    self.labels = []
    self.epsilon = self.epsilon_start

    self.previous_observation, _ = self.env.reset()
    action = self.random_step()
    self.observation, _, _, _, _ = self.env.step(action)


  def random_step(self):
    return self.env.action_space.sample()


  def train_model(self):
    episodes = self.current_episodes()

    for _ in range(episodes):
      self.calc_epsilon()
      action = self.current_action()
      self.previous_observation = np.array(self.observation, copy=True)

      print('action', action)

      self.observation, reward, terminated, truncated, _ = self.env.step(action)

      # if terminated or truncated:
      #   self.finalize_penalty(action)
      # else:
      #   self.finalize_episode(action, reward)

    self.replay()


  def current_episodes(self):
    if self.render_mode == 'rgb_array':
      return self.episodes_hidden
    if self.render_mode == 'human':
      return self.episodes_visible
    raise Exception('The mod is not correct!')


  def calc_epsilon(self):
    self.epsilon = max(self.epsilon_end, self.epsilon_decay * self.epsilon)


  def current_action(self):
    if random.random() > self.epsilon:
      return self.predict()
    return self.random_step()


  def predict(self):
    observations = self.current_observations()
    x = keras.ops.array(np.array(observations), dtype=torch.float64)
    predictions = self.model.predict(x=x)
    return predictions.argmax()


  def current_observations(self):
    return [self.observation]
    # return np.append(self.previous_observation, self.observation)


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
    rewards = [reward]
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


MountainCar()
