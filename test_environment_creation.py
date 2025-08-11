import json
import csv
from hybrid_agent import HybridAgent
from random_agent import RandomAgent
from inference import KnowledgeBase
from typing import List, Set, Tuple, FrozenSet
from environment import Environment, Action
import time


def load_map(file_path: str) -> dict:
    with open(file_path, 'r') as f:
        return json.load(f)
    

def run_test(env: Environment, agent_class) -> Tuple[int, int, float, int]:
    successes = 0
    total_score = 0
    total_time = 0
    total_step = 0

    log_act = []
    
    env.reset()
    agent = agent_class(env)

    
    start_time = time.time()

    percepts = env.get_percept()

    while agent.state.alive:
        agent.think(percepts)

        if not agent.action_plan:
            log_act.append("No action planned\n")
            break
        
        action = agent.action_plan.pop(0)
        log_act.append(f"Agent action: {action}\n")

        percepts = env.execute_action(action)

        agent._update_state(action, percepts)

        if action == Action.SHOOT:
            agent.inference_engine.reset_kb_after_shoot((agent.state.x, agent.state.y), agent.state.direction)
        
        if env.moving_wumpus_mode and env.agent_action_count > 0 and env.agent_action_count % 5 == 0:
            agent.inference_engine.reset_kb()

        if action == Action.CLIMB: 
            break
        

    end_time = time.time()
    
    if env.agent_state.has_gold and env.agent_state.win:
        successes += 1

    total_score += env.agent_state.score
    total_time += (end_time - start_time)
    total_step += env.agent_action_count

    return successes, total_score, total_time, total_step, log_act


if __name__ == "__main__":

    num_env = 3

    envs = []

    for i in range(num_env):    
        map_config = load_map(f'testcases/map{i + 1}.json')

        envs.append(Environment(size=map_config["Size"],
                                world_matrix=map_config["WorldMatrix"],
                                moving_wumpus_mode=map_config["MovingWumpusMode"]))
        
    all_hybrid_successes = []
    all_hybrid_scores = []
    all_hybrid_steps = []


    csv_filename = 'results/test_results_hybrid.csv'

    csv_headers = [
        'Map_ID', 'Size', 'NumWumpus', 'Moving',
        'Hybrid_Success', 'Hybrid_Score', 'Hybrid_Decision_Eff'
    ]


    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(csv_headers)

        for i, env in enumerate(envs):
            env.display()
            successes, total_score, total_time, total_step, log_act = run_test(env, HybridAgent)

            all_hybrid_successes.append(successes)
            all_hybrid_scores.append(total_score)
            all_hybrid_steps.append(total_step)

            log_file_path = f"results/log_map{i + 1}.txt"

            with open(log_file_path, "w") as log_file:
                for log in log_act:
                    log_file.write(log)

            row = [
                i + 1,  # Map_ID
                env.size,
                env.num_wumpus,
                env.moving_wumpus_mode,
                successes,
                total_score,
                total_step
            ]

            writer.writerow(row)

    
    sum_file_path = "results/test_summary.json"
    total_maps = len(envs)

    hybrid_summary = {
        "success_rate": round((sum(all_hybrid_successes) / total_maps), 2),
        "avg_score": round(sum(all_hybrid_scores) / total_maps, 2),
        "avg_decision_eff": round(sum(all_hybrid_steps) / total_maps, 2)
    }

    with open(sum_file_path, 'w') as sum_file:
        json.dump(hybrid_summary, sum_file)



    


    

    


    

    