from ray import tune
from plataformas import Juego

tune.run(run_or_experiment="DQN",
         checkpoint_freq=100,
         checkpoint_at_end=True,
         local_dir=r'./resultados',
         config={
             "env": Juego,
             "render_env": True,
             "num_workers": 1
         })
