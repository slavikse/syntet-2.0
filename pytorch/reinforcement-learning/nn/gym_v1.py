import os
os.environ['KERAS_BACKEND'] = 'torch'
import torch
import keras
import gymnasium as gym
import numpy as np
import random

# TODO Not Completed

class NeuralNetwork:
  inputs = []
  labels = []

  state = []
  reward_episode = 0
  epsilon = 0

  # TODO на данный момент модель будет стремится к увеличению количества шагов.
  #   есть задачи, где чем меньше шагов было предпринято моделью - тем лучше.
  step_count = 0
  step_count_maximum = 0

  # rgb_array | human
  render_mode = 'rgb_array'

  env = None
  model = None


  def __init__(self,
    env_name,
    episode_length,
    units_output,

    layers_hidden=3,
    units_hidden=100,
    learning_rate=1e-3,

    batch_size=8,
    epochs=3,

    reward_initial=0.5,
    reward_normal=1,
    reward_penalty=0,

    researchers=0.2,
    # TODO del? эпсилон заменен на скрытую стадию обучения со случайным шагом в 30% случаев всегда.
    epsilon_initial=1.0,
    epsilon_minimum=0.01,
    epsilon_decay=0.95,
    ###

    episodes_hidden=300,
    episodes_visible=200,

    exploitation=False,
  ):
    self.env_name = env_name
    self.episode_length = episode_length
    self.units_output = units_output

    self.layers_hidden = layers_hidden
    self.units_hidden = units_hidden
    self.learning_rate = learning_rate

    self.batch_size = batch_size
    self.epochs = epochs

    self.reward_initial = reward_initial
    self.reward_normal = reward_normal
    self.reward_penalty = reward_penalty

    self.researchers = researchers
    self.epsilon_initial = epsilon_initial
    self.epsilon_minimum = epsilon_minimum
    self.epsilon_decay = epsilon_decay

    self.episodes_hidden = episodes_hidden
    self.episodes_visible = episodes_visible

    self.exploitation = exploitation
    self.is_research = not exploitation

    self.model_path = 'models/' + self.env_name + '.keras'

    self.prepare_model()


  def prepare_model(self):
    if self.exploitation:
      self.load_model()
    else:
      self.build_model()

    self.configure_training()


  def load_model(self):
    if os.path.isfile(self.model_path):
      self.model = keras.models.load_model(self.model_path)
    else:
      print('File was not found:', self.model_path)


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


  def configure_training(self):
    if self.exploitation:
      self.exploite_env()
    else:
      self.train_env()
      self.state_reset()

    self.env_reset()
    self.start_training()


  def exploite_env(self):
    if not self.env:
      self.render_mode = 'human'
      self.create_env()


  def train_env(self):
    if self.env:
      self.save_model()
      self.env.close()

    self.create_env()


  def save_model(self):
    self.model.save(self.model_path)
    print('The model is saved...', self.step_count_maximum)


  def create_env(self):
    self.env = gym.make(self.env_name, render_mode=self.render_mode)


  def state_reset(self):
    self.inputs = []
    self.labels = []


  def env_reset(self):
    self.state, _ = self.env.reset()
    self.reward_episode = 0
    self.epsilon = self.epsilon_initial
    self.step_count = 0


  def start_training(self):
    episodes = self.next_episodes()

    for _ in range(episodes):
      action = self.next_action()
      self.state, _, terminated, truncated, _ = self.env.step(action)
      is_action_bad = terminated or truncated

      if self.exploitation:
        if is_action_bad:
          self.env_reset()
        continue

      self.take_step(is_action_bad, action)

    self.prepare_for_training()


  def next_episodes(self):
    if self.render_mode == 'rgb_array':
      return self.episodes_hidden

    if self.render_mode == 'human':
      return self.episodes_visible

    raise Exception('The mod is not correct!')


  def next_action(self):
    if self.is_research and self.researchers > random.random():
    # if self.is_research and self.epsilon > random.random():
      return self.env.action_space.sample()
    return self.predict_action()


  def predict_action(self):
    x = keras.ops.array(np.array([self.get_state()]), dtype=torch.float64)
    actions = self.model.predict(x=x)
    return actions.argmax()


  def get_state(self):
    step_normal = self.step_count / self.episode_length
    # TODO модификация для сокращения количества шагов?
    # step_normal = 1 - self.step_count / self.episode_length
    return [self.state]
    # return np.append(self.state, step_normal)


  def take_step(self, is_action_bad, action):
    if is_action_bad:
      self.action_penatly(action)
      self.env_reset()
    else:
      is_action_good = self.has_action_good()
      self.update_epsilon()

      if is_action_good:
        self.action_normal(action)
      else:
        # TODO шаги имеют свою оценку, но именно они привели агента к проигрышу...
        #   переназначить награды?
        self.action_penatly(action)


  def action_penatly(self, action):
    rewards = self.rewards_initialize()
    rewards[action] = self.reward_penalty
    self.collect_step(rewards)


  def has_action_good(self):
    self.step_count += 1

    if self.step_count > self.step_count_maximum:
      self.step_count_maximum = self.step_count
      print('model began to predict better...', self.step_count_maximum)
      return True

    return False


  def action_normal(self, action):
    self.reward_episode += self.reward_normal
    rewards = self.rewards_initialize()
    rewards[action] = self.reward_episode / self.episode_length

    # TODO модификация для сокращения количества шагов?
    # rewards[action] = 1 - self.reward_episode / self.episode_length
    self.collect_step(rewards)


  def rewards_initialize(self):
    rewards = []
    for _ in range(self.units_output):
      rewards.append(self.reward_initial)
    return rewards


  def update_epsilon(self):
    self.epsilon = max(self.epsilon_minimum, self.epsilon * self.epsilon_decay)


  def collect_step(self, rewards):
    self.inputs.append(self.get_state())
    self.labels.append(rewards)


  def prepare_for_training(self):
    if not self.exploitation:
      self.fit_model()
      self.switch_mode()
      self.state_reset()

    self.configure_training()


  def fit_model(self):
    x = keras.ops.array(np.array(self.inputs), dtype=torch.float64)
    y = keras.ops.array(np.array(self.labels), dtype=torch.float64)

    self.model.fit(
      x=x,
      y=y,
      batch_size=self.batch_size,
      epochs=self.epochs,
      # 0 = silent, 1 = progress bar, 2 = one line per epoch
      verbose=0,
    )


  # three stages: hidden with and without epsilon. displayed without epsilon.
  def switch_mode(self):
    if self.is_research:
      if self.render_mode == 'rgb_array':
        self.is_research = False
    else:
      if self.render_mode == 'rgb_array':
        self.render_mode = 'human'
      elif self.render_mode == 'human':
        self.is_research = True
        self.render_mode = 'rgb_array'
