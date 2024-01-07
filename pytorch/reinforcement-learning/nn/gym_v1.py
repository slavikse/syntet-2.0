import os
os.environ['KERAS_BACKEND'] = 'torch'
import torch
import keras
import gymnasium as gym
import numpy as np
import random


class NeuralNetwork:
  prev_state = []
  state = []
  inputs = []
  labels = []

  env = None
  model = None
  # 0 = silent, 1 = progress bar, 2 = one line per epoch
  verbose = 0
  # rgb_array | human
  render_mode = 'human'


  def __init__(self,
    env_name,
    units_output,

    layers_hidden=6,
    units_hidden=1000,
    learning_rate=1e-5,

    reward_basic=0,
    reward_penalty=0,
    reward_episode_start=1,

    batch_size=8,
    epochs=3,

    researcher=0.2,
    early_convergence=False,
    use_prev_state=False,
    exploitation=False,

    epsilon_start=0.99,
    epsilon_end=0.001,
    epsilon_decay=0.95,

    episodes_hidden=1200,
    episodes_visible=400,
  ):
    self.env_name = env_name
    self.units_output = units_output

    self.layers_hidden = layers_hidden
    self.units_hidden = units_hidden
    self.learning_rate = learning_rate

    self.reward_basic = reward_basic
    self.reward_penalty = reward_penalty
    self.reward_episode_start = reward_episode_start

    self.batch_size = batch_size
    self.epochs = epochs

    self.researcher = researcher
    self.early_convergence = early_convergence
    self.use_prev_state = use_prev_state
    self.exploitation = exploitation

    # Aspires (decreasing) from epsilon_start to epsilon_end.
    self.epsilon = epsilon_start
    self.epsilon_start = epsilon_start
    self.epsilon_end = epsilon_end
    self.epsilon_decay = epsilon_decay

    self.episodes_hidden = episodes_hidden
    self.episodes_visible = episodes_visible

    self.model_path = 'models/' + self.env_name + '.keras'

    self.start()


  def start(self):
    if self.exploitation:
      self.load_model()
    else:
      self.build_model()

    self.replay()


  def load_model(self):
    self.model = keras.models.load_model(self.model_path)


  def save_model(self):
    self.model.save(self.model_path)
    print('The model is saved...')


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
    if self.exploitation:
      self.exploite_env()
    else:
      self.switch_mode()
      self.train_env()

    self.state_reset()
    self.model_launch()


  def exploite_env(self):
    if not self.env:
      self.render_mode = 'human'
      self.env = gym.make(self.env_name, render_mode=self.render_mode)


  def switch_mode(self):
    if self.render_mode == 'human':
      self.render_mode = 'rgb_array'

    elif self.render_mode == 'rgb_array':
      self.render_mode = 'human'

    else:
      raise Exception('The mod is not selected!')


  def train_env(self):
    if self.env:
      self.save_model()
      self.env.close()

    self.env = gym.make(self.env_name, render_mode=self.render_mode)


  def state_reset(self):
    self.inputs = []
    self.labels = []
    self.epsilon = self.epsilon_start

    if self.early_convergence:
      self.reward_episode = self.reward_episode_start
    else:
      self.reward_episode = 0

    if self.use_prev_state:
      self.prev_state, _ = self.env.reset()
      action = self.random_step()
      self.state, _, _, _, _ = self.env.step(action)
    else:
      self.state, _ = self.env.reset()


  def model_launch(self):
    episodes = self.next_episodes()

    for _ in range(episodes):
      self.calc_epsilon()
      action = self.next_action()
      self.save_prev_state()
      self.state, _, terminated, truncated, _ = self.env.step(action)
      is_end = terminated or truncated

      if is_end and self.exploitation:
        break
      else:
        self.finalize(is_end, action)

    self.replay()


  def next_episodes(self):
    if self.render_mode == 'rgb_array':
      return self.episodes_hidden

    if self.render_mode == 'human':
      return self.episodes_visible

    raise Exception('The mod is not correct!')


  def calc_epsilon(self):
    self.epsilon = max(self.epsilon_end, self.epsilon_decay * self.epsilon)


  def next_action(self):
    if self.render_mode == 'rgb_array'\
    and random.random() < self.researcher:
      return self.random_step()

    return self.predict()


  def random_step(self):
    return self.env.action_space.sample()


  def predict(self):
    state = self.current_state()
    x = keras.ops.array(np.array([state]), dtype=torch.float64)
    predictions = self.model.predict(x=x)
    return predictions.argmax()


  def current_state(self):
    if self.use_prev_state:
      return np.append(self.prev_state, self.state)

    return self.state


  def save_prev_state(self):
    if self.use_prev_state:
      self.prev_state = np.array(self.state, copy=True)


  def finalize(self, is_end, action):
    if is_end:
      self.collect(action, self.reward_penalty)
      self.fit_model()
      self.state_reset()
    else:
      self.collect(action, self.reward_basic)


  def collect(self, action, reward):
    state = self.current_state()
    self.inputs.append(state)

    rewards = self.get_rewards(action, reward)
    self.labels.append(rewards)


  def get_rewards(self, action, reward):
    rewards = []

    for _ in range(self.units_output):
      rewards.append(self.reward_basic)

    if self.early_convergence:
      discount = self.epsilon * reward
      self.reward_episode -= discount
    else:
      discount = (1 - self.epsilon) * reward
      self.reward_episode += discount

    rewards[action] = self.reward_episode
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
