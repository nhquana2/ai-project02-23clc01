from environment import *

if __name__ == "__main__":
    env = Environment(size=8, num_wumpus=10, pit_prob=0.05)
    env.display()
    print(env.execute_action(Action.TURN_LEFT))
    env.display()
    print(env.execute_action(Action.SHOOT))
    env.display()
