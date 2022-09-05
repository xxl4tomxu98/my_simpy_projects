import simpy
import random

env = simpy.Environment()
N = 5
chopsticks = [simpy.Resource(env, capacity=1) for i in range(N)]


class Philosoper():
    # mean time for thinking
    T0 = 10
    # mean time for eating
    T1 = 10
    # time to pick up the other chopstick
    DT = 1
    def __init__(self, env, chopsticks, my_id, DIAG=False):        
        self.env = env
        self.chopsticks = chopsticks
        self.id = my_id
        self.DIAG = DIAG
        self.waiting = 0
        # register the process with the environment
        env.process(self.run_the_party())
    # request resources
    def get_hungry(self):
        yield
    # do everything
    def run_the_party(self):
        yield
    # diagose
    def diag(self, message):
        if self.DIAG:
            print("P{} {} @{}", self.id, message, self.env.now())  

philosophers = [Philosoper(env, (chopsticks[i], chopsticks[(i+1)%N]), i) for i in range(N)]   