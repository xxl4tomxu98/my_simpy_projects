# SimPy example: Variation of Mach1.py, Mach2.py. Two machines, but
# sometimes break down. Up time is exponentially distributed with mean
# 1.0, and repair time is exponentially distributed with mean 0.5. In
# this example,there is only one repairperson, and she is not summoned
# until both machines are down. We find the proportion of up time. It
# should come out to about 0.45.

import simpy
from random import Random, expovariate


class G: # globals
    Rnd = Random(12345)


class MachineClass(object):
    MachineList = [] # list of all objects of this class
    UpRate = 1/1.0
    RepairRate = 1/0.5
    TotalUpTime = 0.0 # total up time for all machines
    NextID = 0 # next available ID number for MachineClass objects
    NUp = 0 # number of machines currently up

    def __init__(self, env, RepairPerson):
        env.process.__init__(self)
        self.env = env
        self.RepairPerson = RepairPerson
        self.StartUpTime = None # time the current up period started
        self.ID = MachineClass.NextID # ID for this MachineClass object
        MachineClass.NextID += 1
        MachineClass.MachineList.append(self)
        MachineClass.NUp += 1 # start in up mode
    
    def model_run(self):
        while True:
            self.StartUpTime = self.env.now
            yield self.env.timeout(G.Rnd.expovariate(MachineClass.UpRate))
            MachineClass.TotalUpTime += self.env.now - self.StartUpTime
            # update number of up machines
            MachineClass.NUp -= 1
            # if only one machine down, then wait for the other to go down
            if MachineClass.NUp == 1:
                yield passivate,self
            # here is the case in which we are the second machine down;
            # either (a) the other machine was waiting for this machine to
            # go down, or (b) the other machine is in the process of being
            # repaired
            elif G.RepairPerson.capacity == 1:
                reactivate(MachineClass.MachineList[1-self.ID])
                # now go to repair
                yield self.RepairPerson.request()
                yield self.env.timeout(G.Rnd.expovariate(MachineClass.RepairRate))
                MachineClass.NUp += 1
                yield self.RepairPerson.release(self.RepairPerson.request())


def main():
    env = simpy.Environment()  # required
    # create the repairperson
    RepairPerson = simpy.Resource(env, capacity=1)
    # set up the two machine threads
    for I in range(2):
        # create a MachineClass object
        machine = MachineClass(env, RepairPerson)
        # register thread machine, executing machine’s model_run() method,
        env.process(machine.model_run())  # required
    # run until simulated time 10000
    MaxSimtime = 10000.0
    env.run(until=MaxSimtime)  # required
    print("the percentage of up time was: ", (MachineClass.TotalUpTime)/(2*MaxSimtime))


if __name__ == "__main__":
    main()