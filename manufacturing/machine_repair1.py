# Introductory SimPy example: Two machines, which sometimes break down.
# Up time is exponentially distributed with mean 1.0, and repair time is
# exponentially distributed with mean 0.5. There are two repairpersons,
# so the two machines can be repaired simultaneously if they are down
# at the same time.

# Output is long-run proportion of up time. Should get value of about
# 0.66.

import simpy # required
import random


class G: # global variables
    Rnd = random.Random(12345)


class MachineClass(object):
    UpRate = 1/1.0 # reciprocal of mean up time
    RepairRate = 1/0.5 # reciprocal of mean repair time
    TotalUpTime = 0.0 # total up time for all machines
    NextID = 0 # next available ID number for MachineClass objects
    
    def __init__(self, env): # required constructor
        env.process.__init__(self) # must call parent constructor
        # instance variables
        self.StartUpTime = 0.0 # time the current up period started
        self.ID = MachineClass.NextID # ID for this MachineClass object
        MachineClass.NextID += 1

    def model_run(self, env): # required constructor
        while True:
            # record current time, now(), so can see how long machine is up
            self.StartUpTime = env.now()
            # hold for exponentially distributed up time
            UpTime = G.Rnd.expovariate(MachineClass.UpRate)
            yield env.hold, self, UpTime # simulate UpTime
            # update up time total
            MachineClass.TotalUpTime += env.now() - self.StartUpTime
            RepairTime = G.Rnd.expovariate(MachineClass.RepairRate)
            # hold for exponentially distributed repair time
            yield env.hold, self, RepairTime


def main():
    env = simpy.Environment()  # required
    # set up the two machine threads
    for I in range(2):
        # create a MachineClass object
        machine = MachineClass(env)
        # register thread machine, executing machine’s model_run() method,
        env.process(machine.model_run(env))  # required
    # run until simulated time 10000
    MaxSimtime = 10000.0
    env.run(until=MaxSimtime)  # required
    print("the percentage of up time was: ", (MachineClass.TotalUpTime)/(2*MaxSimtime))


if __name__ == "__main__":
    main()