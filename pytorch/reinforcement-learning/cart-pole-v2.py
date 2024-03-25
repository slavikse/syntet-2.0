from nn.gym_v1 import NeuralNetwork


class CarlPole(NeuralNetwork):
  def __init__(self, **kwargs):
    super(CarlPole, self).__init__(**kwargs)


# TODO Not Completed

CarlPole(
  env_name='CartPole-v1',
  episode_length=100, # 500
  units_output=2,

  layers_hidden=6,
  units_hidden=1000,
  learning_rate=1e-5,

  reward_initial=0.5,
  reward_normal=1,
  reward_penalty=0,

  researchers=0.1,

  # episodes_visible=20000,
  # exploitation=True,
)
