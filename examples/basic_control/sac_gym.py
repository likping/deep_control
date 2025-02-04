import argparse
import sys
sys.path.append("/Users/macbook/Documents/VscodeProjects/deep_control")
import deep_control as dc


def train_gym_sac(args):
    # same training and testing seed
    train_env = dc.envs.load_gym(args.env_id, args.seed)
    test_env = dc.envs.load_gym(args.env_id, args.seed)

    state_space = train_env.observation_space
    action_space = train_env.action_space

    # create agent
    agent = dc.sac.SACAgent(
        state_space.shape[0], action_space.shape[0], args.log_std_low, args.log_std_high,
    )

    # create replay buffer
    if args.prioritized_replay:
        buffer_type = dc.replay.PrioritizedReplayBuffer
    else:
        buffer_type = dc.replay.ReplayBuffer
    buffer = buffer_type(
        args.buffer_size,
        state_shape=state_space.shape,
        state_dtype=float,
        action_shape=action_space.shape,
    )

    # run sac
    dc.sac.sac(
        agent=agent, train_env=train_env, test_env=test_env, buffer=buffer, **vars(args)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    dc.envs.add_gym_args(parser)
    dc.sac.add_args(parser)
    args = parser.parse_args()
    args.max_episode_steps = 1000
    train_gym_sac(args)
