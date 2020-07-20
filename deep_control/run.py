import argparse

import gym
import pybullet
import pybullet_envs
import torch

from . import agents, utils


def run(agent, env, episodes, max_steps, render=False, verbosity=1):
    episode_return_history = []
    if render:
        env.render()
    for episode in range(episodes):
        episode_return = 0
        state = env.reset()
        done, info = False, {}
        for _ in range(max_steps):
            if done:
                break
            action = agent.forward(state)
            state, reward, done, info = env.step(action)
            if render:
                env.render()
            episode_return += reward
        if verbosity:
            print(f"Episode {episode}:: {episode_return}")
        episode_return_history.append(episode_return)
    return torch.tensor(episode_return_history)


def collect_experience_by_steps(
    agent, env, buffer, num_steps, current_state=None, current_done=None
):
    if not current_state:
        state = env.reset()
    if not current_done:
        done = False
    for step in num_steps:
        if done:
            state = env.reset()
        action = agent.forward(state)
        next_state, reward, done, info = env.step(action)
        buffer.push(state, action, reward, next_state, done)
        state = next_state
    return state, done


def collect_experience_by_rollouts(
    agent, env, buffer, num_rollouts, max_rollout_length
):
    state = env.reset()
    done = False
    for rollout in range(num_rollouts):
        step_num = 0
        while not done:
            action = agent.forward(state)
            next_state, reward, done, info = env.step(action)
            buffer.push(state, action, reward, next_state, done)
            state = next_state
            step_num += 1
            if step_num >= max_rollout_length:
                done = True


def load_env(env_id, algo_type):
    env = gym.make(env_id)
    shape = (env.observation_space.shape[0], env.action_space.shape[0])
    max_action = env.action_space.high[0]
    if algo_type == "ddpg":
        agent = agents.DDPGAgent(*shape, max_action)
    elif algo_type == "sac":
        agent = agents.SACAgent(*shape, max_action)
    elif algo_type == "td3":
        agent = agents.TD3Agent(*shape, max_action)
    return agent, env


def warmup_buffer(buffer, env, warmup_steps, max_episode_steps):
    # use warmp up steps to add random transitions to the buffer
    state = env.reset()
    done = False
    steps_this_ep = 0
    for _ in range(warmup_steps):
        if done:
            state = env.reset()
            steps_this_ep = 0
            done = False
        rand_action = env.action_space.sample()
        next_state, reward, done, info = env.step(rand_action)
        buffer.push(state, rand_action, reward, next_state, done)
        state = next_state
        steps_this_ep += 1
        if steps_this_ep >= max_episode_steps:
            done = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", type=int, default=1)
    parser.add_argument("--env", type=str)
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--save", type=str)
    parser.add_argument("--algo", type=str)
    parser.add_argument("--max_steps", type=int, default=300)
    args = parser.parse_args()

    agent, env = load_env(args.env, args.algo)
    agent.load(args.agent)
    run(agent, env, args.episodes, args.max_steps, args.render, verbosity=1)
