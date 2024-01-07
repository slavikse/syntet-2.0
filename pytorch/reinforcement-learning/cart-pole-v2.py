from nn.gym_v1 import NeuralNetwork


class CarlPole(NeuralNetwork):
  def __init__(self, **kwargs):
    super(CarlPole, self).__init__(**kwargs)


CarlPole(
  env_name='CartPole-v1',
  units_output=2,

  layers_hidden=4,
  units_hidden=200,
  learning_rate=1e-3,

  reward_basic=0.5,
  reward_penalty=-1,

  exploitation=True,
)
