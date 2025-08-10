import json
from hybrid_agent import HybridAgent
from random_agent import RandomAgent
from inference import KnowledgeBase
from typing import List, Set, Tuple, FrozenSet
from environment import Environment, Action
import time


def create_env(config):
    return Environment(size=config['Size'], num_wumpus=config['NumWumpus'], pit_prob=config['PitProb'], moving_wumpus_mode=config['Moving'])

def run_test(env, agent):
    successes = 0
    total_score = 0
    total_time = 0
    total_step = 0
    
    env.reset()
    agent = agent(env)
    

    start_time = time.time()
    
    agent.run()
    
    end_time = time.time()
    
    if env.agent_state.has_gold and env.agent_state.alive:
        successes += 1

    
    total_score += env.agent_state.score
    total_time += (end_time - start_time)
    total_step += env.agent_action_count

    return successes, total_score, total_time, total_step


if __name__ == "__main__":
    with open('map/map.json', 'r') as f:
        config = json.load(f)

    envs = []
    for env_config in config:
        envs.append(create_env(env_config))

    hybrid_record = {"success_rate": 0, "avg_score": 0, "decision_eff": 0}
    random_record = {"success_rate": 0, "avg_score": 0, "decision_eff": 0}
    
    num_environments = len(envs)
    
    
    for i, env in enumerate(envs):

        success, score, total_time, total_step = run_test(env, HybridAgent)

        hybrid_record["success_rate"] += success
        hybrid_record["avg_score"] += score
        hybrid_record["decision_eff"] += total_step



        success, score, total_time, total_step = run_test(env, RandomAgent)

        random_record["success_rate"] += success
        random_record["avg_score"] += score
        random_record["decision_eff"] += total_step


  
    for key in hybrid_record:
        hybrid_record[key] /= num_environments
        random_record[key] /= num_environments
    
    results = {
        "hybrid_agent": hybrid_record,
        "random_agent": random_record,
        "test_environments": len(envs),
    }
    
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=4)

    print("Test results saved to 'test_results.json'")
