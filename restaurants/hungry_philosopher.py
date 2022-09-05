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
        start_waiting = self.env.now()
        self.diag("requeted chopstick")
        rq1 = self.chopsticks[0].request()
        yield rq1
        self.diag("obtained chopstick")
        # block generator DT between 2 chopsticks
        yield self.env.timeout(self.DT)
        self.diag("requeted another chopstick")
        rq2 = self.chopsticks[1].request()
        yield rq2
        self.diag("obtained another chopstick")
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
        
    # diagosis
    def diag(self, message):
        if self.DIAG:
            print("P{} {} @{}", self.id, message, self.env.now())  

philosophers = [Philosoper(env, (chopsticks[i], chopsticks[(i+1)%N]), i) for i in range(N)]
env.run()