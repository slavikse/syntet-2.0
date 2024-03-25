from nn.gym_v1 import NeuralNetwork


class LunarLander(NeuralNetwork):
  def __init__(self, **kwargs):
    super(LunarLander, self).__init__(**kwargs)


# TODO Not completed!

LunarLander(
  env_name='LunarLander-v2',
  episode_length=200,
  units_output=4,

  layers_hidden=4,
  units_hidden=200,
  learning_rate=1e-5,

  reward_normal=0.5,
  reward_penalty=0,

  researchers=0.2,
  exploitation=False,
)
