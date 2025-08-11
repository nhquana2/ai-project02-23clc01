import json
import csv
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
    
    if env.agent_state.has_gold and env.agent_state.win:
        successes += 1

    
    total_score += env.agent_state.score
    total_time += (end_time - start_time)
    total_step += env.agent_action_count

    return successes, total_score, total_time, total_step


if __name__ == "__main__":
    with open('map/map.json', 'r') as f:
        config = json.load(f)

    num_env = 12
    envs_per_config = num_env // len(config)
    
    envs = []
    env_configs = []

    for env_config in config:
        for _ in range(envs_per_config):
            envs.append(create_env(env_config))
            env_configs.append(env_config)
    
    remaining = num_env - len(envs)
    for i in range(remaining):
        envs.append(create_env(config[0]))
        env_configs.append(config[0])

    print(f"Created {len(envs)} environments distributed across {len(config)} configurations")

    csv_filename = 'results/test_results_random.csv'
    csv_headers = [
        'Map_ID', 'Size', 'NumWumpus', 'PitProb', 'Moving',
        'Hybrid_Success', 'Hybrid_Score', 'Hybrid_Decision_Eff',
        'Random_Success', 'Random_Score', 'Random_Decision_Eff'
    ]
    
    all_hybrid_successes = []
    all_hybrid_scores = []
    all_hybrid_steps = []
    all_random_successes = []
    all_random_scores = []
    all_random_steps = []
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csv_headers)
        
        for i, (env, env_config) in enumerate(zip(envs, env_configs)):
            
            hybrid_success, hybrid_score, hybrid_time, hybrid_steps = run_test(env, HybridAgent)
            
            random_success, random_score, random_time, random_steps = run_test(env, RandomAgent)
            
            all_hybrid_successes.append(hybrid_success)
            all_hybrid_scores.append(hybrid_score)
            all_hybrid_steps.append(hybrid_steps)
            all_random_successes.append(random_success)
            all_random_scores.append(random_score)
            all_random_steps.append(random_steps)
            
            row = [
                i+1,  # Map_ID
                env_config['Size'],
                env_config['NumWumpus'], 
                env_config['PitProb'],
                env_config['Moving'],
                hybrid_success,    # Success (0 or 1)
                hybrid_score,      # Score
                hybrid_steps,      # Decision efficiency (step count)
                random_success,
                random_score,
                random_steps
            ]
            writer.writerow(row)
    
    print(f"Individual test results saved to '{csv_filename}'")
    
    total_maps = len(envs)
    hybrid_summary = {
        "success_rate": sum(all_hybrid_successes) / total_maps,
        "avg_score": sum(all_hybrid_scores) / total_maps,
        "avg_decision_eff": sum(all_hybrid_steps) / total_maps
    }
    
    random_summary = {
        "success_rate": sum(all_random_successes) / total_maps,
        "avg_score": sum(all_random_scores) / total_maps,
        "avg_decision_eff": sum(all_random_steps) / total_maps
    }
    
    summary_results = {
        "total_environments": total_maps,
        "hybrid_agent": hybrid_summary,
        "random_agent": random_summary,
        "test_configurations": config
    }
    
    json_filename = 'test_summary.json'
    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(summary_results, jsonfile, indent=4)
   