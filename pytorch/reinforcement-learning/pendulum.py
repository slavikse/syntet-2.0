from nn.gym_v1 import NeuralNetwork


class Pendulum(NeuralNetwork):
  def __init__(self, **kwargs):
    super(Pendulum, self).__init__(**kwargs)


# TODO Not completed!

Pendulum(
  env_name='Pendulum-v1',
  units_output=1,

  layers_hidden=5,
  units_hidden=300,
  learning_rate=1e-4,

  reward_normal=-1,
  reward_penalty=-1,

  researchers=0.2,
  # epsilon_decay=0.98,
  # early_convergence=True,
  exploitation=False,
)
