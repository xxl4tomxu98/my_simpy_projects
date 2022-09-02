import pandas as pd
import numpy as np
import simpy
from scipy.stats import uniform
from scipy.stats import expon
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns

# Initialization module
MACHINE_FAILURE_MEAN = 10
## Times in repairing
list_of_minutes = [15,30,40,50]
# discrete probabilities for times in repairing
prob1, prob2, prob3, prob4 = 0.1, 0.3, 0.4, 0.2
prob1 = round(prob1, 4)
prob2 = round(prob1 + prob2,4)
prob3 = round(prob2 + prob3,4)
prob4 = round(prob3 + prob4,4)
list_of_probs = [prob1, prob2, prob3, prob4]
df1 = pd.DataFrame(list_of_minutes, columns = ['minutes'])
df2 = pd.DataFrame(list_of_probs, columns = ['range'])
df_service = pd.concat([df1, df2], axis = 1)
SIM_TIME = 100
max_length, number_rows = 0, 0
avg_length, avg_delay = [],[]
avg_out_system, avg_in_service = [],[]
my_path = './'


def machine_failure(env, number_repair):
    # counter of failures
    failure_number = 0
    while True:
        ## exponential distribution for failures
        next_failure = expon.rvs(scale = MACHINE_FAILURE_MEAN, 
                                 size = 1)
        # Wait for the failure
        yield env.timeout(next_failure)
        time_of_failure = env.now
        failures.append(time_of_failure)
        failure_number += 1
        print('failure %3d occurs at %.2f' % 
             (failure_number, env.now))
        env.process(repairing(env, number_repair, 
                    failure_number, time_of_failure))

#...................................................................
def repairing(env, number_repair, failure_number, time_of_failure):
    with repair_persons.request() as req:
        print('%3d enters the queue at %.2f' % 
              (failure_number, env.now))         
        queue_in = env.now
        length = len(repair_persons.queue)
        tme_in_queue.append(queue_in)
        len_in_queue.append(length)
        yield req
        print('%3d leaves the queue at %.2f' % 
              (failure_number, env.now)) 
        queue_out = env.now
        length = len(repair_persons.queue)
        tme_in_queue.append(queue_out)
        len_in_queue.append(length)
        # random variate with uniform distribution
        r_v = uniform.rvs(size=1)
        print(r_v)
        # setting the repair time
        for i,row in df_service.iterrows():
            probab = df_service.loc[i, 'range']
            if r_v < probab:
                time_service = df_service.loc[i, 'minutes']
                break
        yield env.timeout(time_service)
        print('%3d stays at service %.2f' %
              (failure_number,time_service))
        time_repaired = env.now
        repaired.append(time_repaired)
        time_out_system = time_repaired - time_of_failure
        out_system.append(time_out_system)
        time_in_queue = queue_out - queue_in
        in_queue.append(time_in_queue)
        time_in_service = time_service
        in_service.append(time_in_service)

#...................................................................
def avg_line(df_length):
    # finds the time weighted average of the queue length
    # use the next row to figure out how long the queue was at that length
    df_length['delta_time'] = df_length['time'].shift(-1) - df_length['time']
    # drop the last row because it would have an infinite time span
    df_length = df_length[0:-1]
    avg =np.average(df_length['len'],weights=df_length['delta_time'])
    return avg

#...................................................................
def calc_averages():
    df3 = pd.DataFrame(tme_in_queue, columns = ['time'])
    df4 = pd.DataFrame(len_in_queue, columns = ['len'])
    df_length = pd.concat([df3, df4], axis = 1)
    # calculate the y lim for the number of machines in queue chart 
    max_length  = df4['len'].max(axis = 0)
    # calculate the number of frames in the animation
    number_rows = len(df4)
    avg_length.insert(altern, avg_line(df_length))     
    avg_delay.insert(altern,  np.mean(in_queue))
    avg_out_system.insert(altern, np.mean(out_system))
    avg_in_service.insert(altern, np.mean(in_service))
    print('Alternative number: %1d' %(altern+1))
    print('The average delay in queue is %.2f' % 
           (avg_delay[altern]))
    print('The average number of machines in queue is %.2f' % 
           (avg_length[altern]))
    print('The average time machines out of system is %.2f' % 
           (avg_out_system[altern]))
    print('The average time machines were being repaired is %.2f'
           %(avg_in_service[altern]))
    #.............................................................
    Writer = animation.FFMpegWriter(fps=2, metadata=dict(artist='Me'), bitrate=1800)
    fig = plt.figure(figsize=(10,6))
    ax = fig.gca()
    plt.xlim(0, 100)
    plt.ylim(0, max_length + 1)
    ax.yaxis.get_major_locator().set_params(integer=True)
    plt.title(' Number of Machines in Queue for Alternative %i'  
                %NUMBER_REPAIR_PERSONS,fontsize=20)
    def animate(i):
        data = df_length.iloc[:int(i+1)] #select data range
        p = sns.scatterplot(x = data["time"], y = data["len"],
                            marker = '*', s = 100, color="r")
        p.set(xlabel='Time', ylabel='Number of Machines') 
        p.tick_params(labelsize=17)
        plt.setp(p.lines,linewidth=4)
    ani = matplotlib.animation.FuncAnimation(fig, animate, frames=number_rows,
                                             interval=50, repeat=True)
    altern_chart = 'machines_in_queue_alt %i.mp4' %NUMBER_REPAIR_PERSONS
    ani.save(my_path + altern_chart, writer = Writer)  
    plt.show()


RANDOM_SEEDS = [1234, 5678, 9012, 3456, 7890]
np.random.seed(seed= RANDOM_SEEDS[1])

for altern in range(5):
    failures, repaired = [],[]
    in_queue, in_service = [],[]
    out_system = []
    tme_in_queue, len_in_queue = [],[]
    env = simpy.Environment() 
    NUMBER_REPAIR_PERSONS = altern + 1
    repair_persons = simpy.Resource(env, capacity = NUMBER_REPAIR_PERSONS)
    env.process(machine_failure(env, repair_persons))
    env.run(until = SIM_TIME)
    calc_averages()


##..................................................................
def print_averages():
    round_avg_delay  = [round(num, 2) for num in avg_delay]
    round_avg_length = [round(num, 2) for num in avg_length]
    round_avg_out_system = [round(num, 2) for num in avg_out_system]  
    round_avg_in_service = [round(num, 2) for num in avg_in_service]
    listoflists = []
    listoflists.append(round_avg_delay)
    listoflists.append(round_avg_length)
    listoflists.append(round_avg_out_system)
    listoflists.append(round_avg_in_service)
    fig, ax = plt.subplots(1,1)
    column_labels = [" Alt. 1", " Alt. 2", " Alt. 3", 
                     " Alt. 4", " Alt. 5"]
    row_labels = ["Avg. delay in queue", 
                  "Avg. number of machines in queue",
                  "Avg. time machines out of system", 
                  "Avg. time in repair"]
    df=pd.DataFrame(listoflists, columns=column_labels)  
 
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText = df.values, 
             colLabels=df.columns, rowLabels=row_labels,
             rowColours =["skyblue"]*4, 
             colColours =["cyan"]*5, loc="center")
    ax.set_title("Measures of Performance", fontsize=18, 
                 y= 0.8 , pad = 4)
    plt.savefig(my_path +'perf_measures.png',
                bbox_inches='tight', dpi=150)
    plt.show()

