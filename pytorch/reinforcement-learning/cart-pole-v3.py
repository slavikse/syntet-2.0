import os

os.environ['KERAS_BACKEND'] = 'torch'
import keras
import gymnasium as gym
import numpy as np

# TODO
# одна модель, несколько агентов (2).
# один агент всегда принимает решения предсказанием.
# второй - в 20% случайный образом делает шаг.

# action = self.env.action_space.sample()

class Agent:
  last_steps = -3
  layers_hidden = 3
  units_hidden = 20
  learning_rate = 1e-3
  batch_size = 1
  epochs = 1
  episodes_hidden = 800
  episodes_visible = 200
  reward_positive = 0.95
  reward_negative = 0

  # ---

  env_name = 'CartPole-v1'
  action_space = 2
  # None | 42
  seed = None
  is_switch_render_mode = True

  # ---

  env = None
  # rgb_array | human
  render_mode = 'human'
  model = None
  inputs = []
  labels = []
  observation = []
  observations = []
  rewards = []

  # 0 = silent, 1 = progress bar, 2 = one line per epoch
  verbose = 1


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
      units=self.action_space,
      activation=keras.activations.softmax,
    ))

    self.model.compile(
      optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
      loss=keras.losses.Huber(),
      metrics=[
        # Accuracy, Precision
        keras.metrics.Precision(),
      ],
    )


  def replay(self):
    self.create_env()
    self.reset_state()
    self.reset_buffers()
    self.reset_observation()
    self.train_model()


  def create_env(self):
    if self.is_switch_render_mode:
      if self.render_mode == 'rgb_array':
        self.render_mode = 'human'
      elif self.render_mode == 'human':
        self.render_mode = 'rgb_array'
      else:
        raise Exception('The mod is not selected!')

    if self.env:
      self.env.close()

    self.env = gym.make(self.env_name, render_mode=self.render_mode)


  def reset_state(self):
    self.inputs = []
    self.labels = []


  def reset_buffers(self):
    self.observations = []
    self.rewards = []


  def reset_observation(self):
    self.observation, _ = self.env.reset(seed=self.seed)


  def train_model(self):
    episodes = self.current_episodes()

    for episode in range(episodes):
      action = self.predict()
      self.observation, reward, terminated, truncated, _ = self.env.step(action)

      self.observations.append(self.observation)
      rewards = self.get_rewards(reward)
      self.rewards.append(rewards)

      if terminated:
        self.finalize_penalty()
        self.reset_observation()

      if (episode + 1) % self.last_steps == 0:
        self.finalize_episode()

      if truncated:
        break

    self.replay()


  def current_episodes(self):
    if self.render_mode == 'rgb_array':
      return self.episodes_hidden
    if self.render_mode == 'human':
      return self.episodes_visible
    raise Exception('The mod is not correct!')


  def predict(self):
    # TODO [[ ]] ?
    x = np.array([self.observation])
    predictions = self.model.predict(x=x)
    return predictions.argmax()


  def get_rewards(self, reward):
    rewards = []
    for _ in range(self.action_space):
      rewards.append(reward)
    return rewards


  def finalize_penalty(self):
    for idx in range(len(self.rewards)):
      last = -(idx + 1)

      if last >= self.last_steps:
        rewards = self.get_rewards(self.reward_negative)
        self.rewards[last] = rewards

    self.finalize_episode()
    self.fit_model()
    self.reset_state()


  def finalize_episode(self):
    self.inputs += self.observations
    self.labels += self.rewards

    self.reset_buffers()


  def fit_model(self):
    x = np.array(self.inputs)
    y = np.array(self.labels)

    self.model.fit(
      x=x,
      y=y,
      batch_size=self.batch_size,
      epochs=self.epochs,
      verbose=self.verbose,
    )


Agent()
