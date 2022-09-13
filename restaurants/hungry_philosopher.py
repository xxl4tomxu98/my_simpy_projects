import simpy
import random


class Philosoper():
    # mean time for thinking
    T0 = 10
    # mean time for eating
    T1 = 15
    # time to pick up the other chopstick
    DT = 3
    # Single meal size
    PORTION = 20

    def __init__(self, env, chopsticks, my_id, bowl=None, DIAG=False):        
        self.env = env
        self.chopsticks = sorted(chopsticks, key=id)
        self.id = my_id
        self.DIAG = DIAG
        self.bowl = bowl
        self.waiting = 0
        # register the process with the environment
        env.process(self.run_the_party())

    # request resources
    def get_hungry(self):
        start_waiting = self.env.now
        self.diag("requested chopstick")
        rq1 = self.chopsticks[0].request()
        yield rq1
        self.diag("obtained chopstick")
        # block generator DT between 2 chopsticks
        yield self.env.timeout(self.DT)
        self.diag("requested another chopstick")
        rq2 = self.chopsticks[1].request()
        yield rq2
        self.diag("obtained another chopstick")
        if self.bowl is not None:
            yield self.bowl.get(self.PORTION)
            self.diag("reserved food")
        self.waiting += self.env.now - start_waiting
        return rq1, rq2

    # do everything
    def run_the_party(self):
        while True:
            # Thinking time is exponential distribution
            thinking_delay = random.expovariate(1/self.T0)
            # block generator for the thinking delay time
            yield self.env.timeout(thinking_delay)
            # suspend main process getting hungry yield all events 
            get_hungry_p = self.env.process(self.get_hungry())
            rq1, rq2 = yield get_hungry_p
            # Eating time is also exponential 
            eating_delay = random.expovariate(1/self.T1)
            # block generator for eating delay time
            yield self.env.timeout(eating_delay)
            # use the request handlers returned from subprocess
            # get_hungry() to release the resources
            self.chopsticks[0].release(rq1)
            self.chopsticks[1].release(rq2)
            self.diag("release the chopsticks")
        
    # diagnosis
    def diag(self, message):
        if self.DIAG:
            print(f'P{self.id}, {message}, @{self.env.now}')  


class Chef():
    # mean time for cooking for replenishing
    T2 = 150

    def __init__(self, env, bowl):
        self.env = env
        self.bowl = bowl
        env.process(self.replenish())

    def replenish(self):
        while True:
            yield self.env.timeout(self.T2)
            if self.bowl.level < self.bowl.capacity:
                yield self.bowl.put(self.bowl.capacity - self.bowl.level)


def simulate(n, t):
    '''
    Simulate the system of n philosopher for up to t time units
    and return the average waiting time
    '''
    env = simpy.Environment()
    rice_bowl = simpy.Container(env, init=1000, capacity=1000)
    chef = Chef(env, rice_bowl)
    chopsticks = [simpy.Resource(env, capacity=1) for i in range(n)]
    philosophers = [Philosoper(env, (chopsticks[i], chopsticks[(i+1)%n]), i, rice_bowl)
                    for i in range(n)]
    env.run(until=t)
    return sum(ph.waiting for ph in philosophers)/n


import matplotlib.pyplot as plt 
import matplotlib
matplotlib.style.use("ggplot")
# Simulate
N = 20
X = range(2, N)
Y = [simulate(n, 50000) for n in X]
# Plot
plt.plot(X, Y, "-o")
plt.ylabel("Waiting time")
plt.xlabel("Number of philosopers")
plt.show()
