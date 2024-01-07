from nn.gym_v1 import NeuralNetwork


class Acrobot(NeuralNetwork):
  def __init__(self, **kwargs):
    super(Acrobot, self).__init__(**kwargs)


Acrobot(
  env_name='Acrobot-v1',
  units_output=3,

  layers_hidden=3,
  units_hidden=200,
  learning_rate=1e-3,

  reward_basic=-1,
  reward_penalty=-1,

  exploitation=True,
)
