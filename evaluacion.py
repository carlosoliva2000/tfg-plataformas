from ray.rllib import evaluate
from ray.tune import register_env

from plataformas import Juego


def main():
    register_env("TFG-RL", Juego)

    parser = evaluate.create_parser()
    args = parser.parse_args("--run DQN "
                             "--env TFG-RL "
                             "--render "
                             # "--video-dir .\\videos "
                             # "--steps 1000 "
                             "--episodes 10 "
                             # "--out evaluacion "
                             # "--save-info "
                             # ¡Esta ruta debe apuntar al checkpoint que se quiera evaluar!
                             ".\\resultados\\DQN\\"
                             "DQN_Juego_af76a_00000_0_2022-08-01_13-04-17\\checkpoint_004300\\checkpoint-4300"
                             .split())

    evaluate.run(args, parser)


if __name__ == '__main__':
    main()
