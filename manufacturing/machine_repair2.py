# SimPy example: Variation of machine_repair1.py. There is only one repairperson, 
# so the two machines cannot be repaired simultaneously if they are down at the same time.
# Suppose for instance the thread simulating machine 1 reaches the first yield slightly 
# before the thread for machine 0 does. Then the thread for machine 1 will immediately go 
# to the second yield, while the thread for machine 0 will be suspended at the first yield.
# When the thread for machine 1 finally executes the third yield, then SimPy’s internal code
# will notice that the thread for machine 0 had been queued, waiting for the repairperson,
# and would now reactivate that thread.
# In addition to finding the long-run proportion of up time as in machine_repair1.py, let’s 
# also find the long-run proportion of the time that a given machine does not have immediate 
# access to the repairperson when the machine breaks down. Output values should be about 0.6 and 0.67.

import simpy
from random import Random, expovariate, uniform


class G: # globals    
    Rnd = Random(12345)


class MachineClass(object):
    TotalUpTime = 0.0 # total up time for all machines
    NRep = 0 # number of times the machines have broken down
    NImmedRep = 0 # number of breakdowns the machine started repair service right away
    UpRate = 1/1.0 # breakdown rate
    RepairRate = 1/0.5 # repair rate
    # following two variables are not actually used, but are useful for debugging purposes
    NextID = 0 # next available ID number for MachineClass objects
    NUp = 0 # number of machines currently up

    def __init__(self, env, RepairPerson):
        env.process.__init__(self)
        self.env = env
        self.RepairPerson = RepairPerson
        self.StartUpTime = 0.0 # time the current up period stated
        self.ID = MachineClass.NextID # ID for this MachineClass object
        MachineClass.NextID += 1
        MachineClass.NUp += 1 # machines start in the up mode

    def model_run(self):
        while True:
            self.StartUpTime = self.env.now
            yield self.env.timeout(G.Rnd.expovariate(MachineClass.UpRate))
            MachineClass.TotalUpTime += self.env.now - self.StartUpTime
            # update number of breakdowns
            MachineClass.NRep += 1
            # check whether we get repair service immediately
            if self.RepairPerson.capacity == 1:
                MachineClass.NImmedRep += 1
            # need to request, and possibly queue for, the repairperson
            yield self.RepairPerson.request()
            # We’ve obtained access to the repairperson; now hold for repair time
            yield self.env.timeout(G.Rnd.expovariate(MachineClass.RepairRate))
            # repair done, release the repairperson
            yield self.RepairPerson.release(self.RepairPerson.request())


def main():
    env = simpy.Environment() 
    # create the repairperson
    RepairPerson = simpy.Resource(env, capacity=1)
    # set up the two machine processes
    for I in range(2):
        machine = MachineClass(env, RepairPerson)
        env.process(machine.model_run())   
    MaxSimtime = 10000.0
    env.run(until=MaxSimtime)
    print('proportion of up time:', MachineClass.TotalUpTime/(2*MaxSimtime))
    print('proportion of times repair was immediate:', float(MachineClass.NImmedRep)/MachineClass.NRep)


if __name__ == '__main__':
    main() 