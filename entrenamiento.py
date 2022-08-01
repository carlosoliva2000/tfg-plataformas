from ray import tune
from plataformas import Juego


def main():
    tune.run(run_or_experiment="DQN",
             checkpoint_freq=100,
             checkpoint_at_end=True,
             local_dir=r'./resultados',
             resume="AUTO",
             # resources_per_trial={"cpu": 4, "gpu": 4},
             # num_samples=10,
             config={
                 "env": Juego,
                 "render_env": True,
                 "num_workers": 4,
                 # "evaluation_num_workers": 1,
                 "evaluation_config": {
                     "render_env": True,
                 },
             })


if __name__ == "__main__":
    main()
