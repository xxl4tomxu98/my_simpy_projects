import pandas as pd
import numpy  as np
from numpy.random import RandomState
import simpy
from scipy import stats
from scipy.stats import expon
from scipy.stats import uniform
import matplotlib.pyplot as plt

my_path = './'

# initialization module
MACHINE_FAILURE_MEAN  = 10
NUMBER_REPAIR_PERSONS = 3
## times in repairing
list_of_minutes = [15,  30,  40,  50]
# discrete probabilities for times in repairing
prob1, prob2, prob3, prob4 = 0.1, 0.3, 0.4, 0.2
prob1 = round(prob1, 4)
prob2 = round(prob1 + prob2,4)
prob3 = round(prob2 + prob3,4)
prob4 = round(prob3 + prob4,4)
list_of_probs = [prob1, prob2, prob3, prob4]
df1 = pd.DataFrame(list_of_minutes, columns = ['minutes'])
df2 = pd.DataFrame(list_of_probs,   columns = ['range'])
df_service = pd.concat([df1, df2], axis = 1)


def machine_failure(env, number_repair):
    # counter of failures
    failure_number = 0
    while True:
        ## exponential distribution for failures
        next_failure = expon.rvs(scale=MACHINE_FAILURE_MEAN, size=1)
        # Wait for the failure
        yield env.timeout(next_failure)
        time_of_failure = env.now
        failures.append(time_of_failure)
        failure_number += 1
        print('failure %3d occurs at %.2f' % (failure_number, env.now))
        env.process(repairing(env, number_repair, 
                    failure_number, time_of_failure))

#...................................................................
def repairing(env, number_repair, failure_number, time_of_failure):
    with repair_persons.request() as req:
        print('%3d enters the queue at %.2f' % (failure_number, env.now))
        queue_in = env.now
        length   = len(repair_persons.queue)
        tme_in_queue.append(queue_in)
        len_in_queue.append(length)
        yield req
        print('%3d leaves the queue at %.2f' % (failure_number, env.now))        
        queue_out = env.now
        length = len(repair_persons.queue)
        tme_in_queue.append(queue_out)
        len_in_queue.append(length)        
        # uniform distribution for the repairing process
        r_v = uniform.rvs(size=1)
        print(r_v)
        for i,row in df_service.iterrows():
            probab = df_service.loc[i, 'range']
            if r_v < probab:
                time_service = df_service.loc[i, 'minutes']
                break
        yield env.timeout(time_service)
        print('%3d stays at service %.2f' % (failure_number,time_service))  
        time_repaired = env.now
        repaired.append(time_repaired)
        time_out_system = time_repaired - time_of_failure
        out_system.append(time_out_system)  
        time_in_queue = queue_out - queue_in
        in_queue.append(time_in_queue)
        time_in_service = time_service
        in_service.append(time_in_service)


def avg_line(df_length):
    # finds the time weighted average of the queue length
    # use the next row to figure out how long the queue was at that length
    df_length['delta_time'] = df_length['time'].shift(-1) - df_length['time']
    # drop the last row because it would have an infinite time span
    df_length = df_length[0:-1]
    avg = np.average(df_length['len'], weights = df_length['delta_time'])
    return avg

#..................................................................
def calc_measures():
    df3 = pd.DataFrame(tme_in_queue, columns = ['time'])
    df4 = pd.DataFrame(len_in_queue, columns = ['len'])
    global df_length
    df_length = pd.concat([df3, df4], axis = 1)
    avg_length = avg_line(df_length)
    avg_delay  = np.mean(in_queue)
    avg_in_service = np.mean(in_service)
    avg_out_system = np.mean(out_system)
    print('Number of Run: %1d' %(run+1))
    print('The average delay in queue is %.2f' % (avg_delay))
    print('The average number of machines in queue is %.2f' % (avg_length))
    print('The average time machines were being repaired is %.2f' % (avg_in_service))
    print('The average time machines out of system is %.2f' % (avg_out_system))
    # list and dataframe for final output
    listoflists = []
    listoflists.append(round(avg_delay,2))
    listoflists.append(avg_in_service)
    listoflists.append(avg_out_system)
    listoflists.append(avg_length)
    df.loc[len(df)] = listoflists


def calc_ICs():
    # confidence intervals, define 3 global variables
    global df_output, hwic, l_end
    mean = round(df.mean(),2)
    sigma= round(df.std(ddof=1),2)
    dof  = len(df)-1
    for i in range(4):
        t_crit = np.abs(stats.t.ppf((1-confidence[i])/2,dof))
        print(round(t_crit,3))
    inf, sup = (mean - sigma*t_crit/np.sqrt(len(df)), 
                mean + sigma*t_crit/np.sqrt(len(df)))
    inf = round(inf,2)
    sup = round(sup,2)
    df_output = pd.concat([mean, sigma, inf, sup], axis=1)
    print(df_output)
    hwic= (sup - inf)/2
    if (hwic[0]<=abs_err[0]) and (hwic[1]<=abs_err[1]) and (hwic[3]<=abs_err[3]):
        l_end = True
    print('')
    print(round(hwic,2), abs_err, l_end )


def print_output():
    col_labels = ["Mean", "Std. Dev.", "Lower bound", "Upper Bound"]
    row_labels = ["Delay in Queue","In Repair",
                  "Out of System","Machines in Queue"]
    fig, ax = plt.subplots(1,1)
    ax.axis('tight')
    ax.axis('off') 
    output_table = ax.table(cellText=df_output.values, colLabels=col_labels,
                            rowLabels=row_labels, rowColours=["skyblue"]*5,
                            colColours=["cyan"]*4, cellLoc='center', loc="center")
    ax.set_title("Output data for %i independent runs" %(run+1),  
                  fontsize=18, y= 0.8 , pad = 4)
    output_table.auto_set_font_size(False)
    output_table.set_fontsize(8)
    plt.savefig(my_path +'output_perf_measures.png',
                bbox_inches='tight', dpi=150)
    plt.show()


#...................................................................
confidence = [0.96667, 0.96667, 0.9, 0.96667]
abs_err    = [3.00, 2.00, 3.00, 2.00]
l_end = False
max_numb_of_runs = 1000
numb_of_runs = max_numb_of_runs
seed_value = 2345
prbnumgen  = RandomState(seed_value)
SIM_TIME = 30 * 24
stop_arrivals = 720           # for the verification step
global df
column_labels = ["Delay in Queue","In Repair",
                 "Out of System","Machines in Queue"]
df = pd.DataFrame(columns=column_labels)

for run in range(numb_of_runs):
    failures, repaired    = [],[]
    in_queue, in_service  = [],[]
    out_system = []
    tme_in_queue, len_in_queue = [],[]
    #Set up the simulation environment
    env = simpy.Environment()
    repair_persons=simpy.Resource(env, capacity=NUMBER_REPAIR_PERSONS)
    env.process(machine_failure(env, repair_persons))
    env.run(until = SIM_TIME)
    calc_measures()
    if run >= 10:
        calc_ICs()
    if l_end == True:
       print_output()
       break