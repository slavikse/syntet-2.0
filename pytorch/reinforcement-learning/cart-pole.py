import os
os.environ['KERAS_BACKEND'] = 'torch'
import torch
import keras
import gymnasium as gym
import numpy as np


class CartPole:
  layers_hidden = 6
  units_hidden = 1000
  units_output = 2
  learning_rate = 1e-5
  batch_size = 10
  epochs = 3
  callbacks = [
    # keras.callbacks.EarlyStopping(
    #   monitor="loss",
    #   patience=3,
    #   verbose=0,
    # )
  ]

  reward_basic = 0.5
  reward_penalty = 0
  reward_base = 0
  reward_step = 0.025
  reward_max = 1
  reward = reward_base

  episodes_hidden = 1000
  episodes_visible = 20000
  # train_hidden | train_visible
  render_mode = 'train_visible'

  env = None
  model = None
  # 0 = silent, 1 = progress bar, 2 = one line per epoch
  verbose = 0
  # file_path = 'models/cart-pole.keras'

  previous_observation = []
  observation = []
  inputs = []
  labels = []


  def __init__(self):
    # self.model = keras.saving.load_model(self.file_path)
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
    render_mode = ''

    if self.render_mode == 'train_hidden':
      render_mode = 'rgb_array'

    elif self.render_mode == 'train_visible':
      render_mode = 'human'

    else:
      raise Exception('The mod is not selected!')

    self.env = gym.make('CartPole-v1', render_mode=render_mode)


  def reset_observations(self):
    self.inputs = []
    self.labels = []
    self.reward = self.reward_base

    self.previous_observation, _ = self.env.reset()
    action = self.env.action_space.sample()
    self.observation, _, _, _, _ = self.env.step(action)
    self.finalize_episode(action, self.reward_base)


  def train_model(self):
    episodes = self.current_episodes()

    for _ in range(episodes):
      action = self.predict()
      self.previous_observation = np.array(self.observation, copy=True)
      self.observation, _, terminated, truncated, _ = self.env.step(action)

      if terminated or truncated:
        self.finalize_penalty(action)
      else:
        self.reward_increment()
        self.finalize_episode(action, self.reward)

    self.finalize_current_mode()


  def current_episodes(self):
    if self.render_mode == 'train_hidden':
      return self.episodes_hidden

    if self.render_mode == 'train_visible':
      return self.episodes_visible

    raise Exception('The mod is not correct!')


  def predict(self):
    observations = self.current_observations()
    x = keras.ops.array(np.array([observations]), dtype=torch.float64)
    predictions = self.model.predict(x=x)
    # print('                                      step:', predictions)
    return predictions.argmax()


  def current_observations(self):
    return [self.observation]
    # return np.append(self.previous_observation, self.observation)


  def reward_increment(self):
    self.reward += self.reward_step

    if self.reward > self.reward_max:
      self.reward = self.reward_max


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
    rewards = [self.reward_basic, self.reward_basic]
    rewards[action] = reward
    return rewards


  def fit_model(self):
    x = keras.ops.array(np.array(self.inputs), dtype=torch.float64)
    y = keras.ops.array(np.array(self.labels), dtype=torch.float16)

    history = self.model.fit(
      x=x,
      y=y,
      batch_size=self.batch_size,
      epochs=self.epochs,
      verbose=self.verbose,
      callbacks=self.callbacks,
    )

    # print(history.history['loss'])
    # self.model.summary()


  def finalize_current_mode(self):
    # self.model.save(self.file_path)
    self.render_mode = self.next_mode()
    self.env.close()
    self.replay()


  def next_mode(self):
    if self.render_mode == 'train_hidden':
      return 'train_visible'

    if self.render_mode == 'train_visible':
      return 'train_hidden'

    raise Exception('The mod is not correct!')


CartPole()
