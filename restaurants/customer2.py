import random
from collections import deque
import simpy

SERVICE_DELAY = 10
service_line = deque()
# set the state of the clerk at service counter
counter_idle = False
env = simpy.Environment()


class CustomerFailedException(Exception):
    pass


def service_counter():
    global counter_idle
    while True:
        if service_line:
            ticket = service_line.popleft()
            yield env.timeout(SERVICE_DELAY)
            if random.randinit(0,9) == 9:
                ticket.fail(CustomerFailedException())
            else:
                counter_idle = True
                print("The clerk fall asleep @{0:.1f}".format(env.now))
                try:
                    yield env.event()
                except simpy.Interrupt:
                    counter_idle = False
                    print("The clerk woke up @{0:.1f}".format(env.now))
    
service_counter_p = env.process(service_counter())


def customer():
    print("Customer arrived @{0:.1f}".forrmat(env.now))
    ticket = env.event()
    service_line.append(ticket)
    if counter_idle:
        service_counter_p.interrupt()
    try:
        yield ticket
        print("Customer left @{0:.1f}".format(env.now))
    except CustomerFailedException:
        print("Customer failed and left @{0:.1f}".format(env.now))


def customer_generator():
    for _ in range(10):
        env.process(customer())
        yield env.timeout(random.expovariate(1/SERVICE_DELAY))


customer_generator_p = env.process(customer_generator())
env.run()