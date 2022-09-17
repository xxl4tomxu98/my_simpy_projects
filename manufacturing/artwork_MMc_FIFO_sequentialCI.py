import pandas as pd
import numpy  as np
from numpy.random import RandomState
import simpy
from scipy import stats
import matplotlib.pyplot as plt

# initialization module
# Unit of time = hours
JOBS_ARRIVAL_RATE  = 1/10
WORK_STATION1_MEAN = 7
WORK_STATION2_MEAN = 5
NUMBER_WORK_STATION1 = 1
NUMBER_WORK_STATION2 = 1
column_labels = ["Delay WK1","Delay WK2","Util. WK1",
                 "Util. WK2", "Avg Length WK1"]
df = pd.DataFrame(columns=column_labels)


def generate_jobs(env, arrival_stream, arrival_rate, 
                  inital_delay = 0,
                  stoptime = simpy.core.Infinity, 
                  prng = RandomState(0)):
    number_of_job = 0
    yield env.timeout(inital_delay)     #Yield the initial delay
    while (env.now <stoptime):
        inter_arrival_time = prng.exponential(1.0 / arrival_rate)
        los_station1 = prng.exponential(WORK_STATION1_MEAN)
        los_station2 = prng.exponential(WORK_STATION2_MEAN)
        number_of_job += 1
        jobpr = process_jobs(env, 
           'Job number: {}'.format(number_of_job), number_of_job,
            los_st1 = los_station1, los_st2 = los_station2)
        env.process(jobpr)
        yield env.timeout(inter_arrival_time)

#.................................................................
def process_jobs(env, number_of_job, job_number, los_st1, los_st2):
    # First Workstation
    # print("{} is scheduled for workstation 1 at hour {:.4f}".format(number_of_job, env.now))
    workstation1_schedule_list.append(job_number)
    time_workstation1_schedule_list.append(env.now)
    jobwk1_request = work_station1.request()
    workstation1_length_list.append(len(work_station1.queue))
    workstation1_timeth_list.append(env.now)
    yield jobwk1_request
    #print("{} enters to workstation 1 at hour  {:.4f}".format(job_number, env.now))
    workstation1_operation_list.append(job_number)
    time_workstation1_operation_list.append(env.now)
    workstation1_length_list.append(len(work_station1.queue))
    workstation1_timeth_list.append(env.now)
    #if (env.now > jobwk1_request_time):
        #print("{} has to wait {:.4f} hours".format(job_number, env.now - jobwk1_request_time))
    yield env.timeout(los_st1)
    work_station1.release(jobwk1_request)
    workstation1_release_list.append(job_number)
    time_workstation1_release_list.append(env.now)
    # Second Workstation
    # print("{} is scheduled for workstation 2 at hour {:.4f}".format(job_number, env.now))
    workstation2_schedule_list.append(job_number)
    time_workstation2_schedule_list.append(env.now)
    jobwk2_request = work_station2.request()
    yield jobwk2_request
    #print("{} enters to workstation 2 at hour {:.4f}".format(job_number, env.now))
    workstation2_operation_list.append(job_number)
    time_workstation2_operation_list.append(env.now)
    #if (env.now > jobwk2_request_time):
        #print("{} has to wait {:.4f} hours".format(job_number, env.now-jobwk2_request_time))
    yield env.timeout(los_st2)
    work_station2.release(jobwk2_request)
    workstation2_release_list.append(job_number)
    time_workstation2_release_list.append(env.now)


def calc_measures():
    # Construct dataframes prior to calculations
    df_wk1_schdl['Job Number']   = workstation1_schedule_list
    df_wk1_schdl['Job Time Sc1'] = time_workstation1_schedule_list
    df_wk2_schdl['Job Number']   = workstation2_schedule_list
    df_wk2_schdl['Job Time Sc2'] = time_workstation2_schedule_list
    df_wk1_opert['Job Number']   = workstation1_operation_list
    df_wk1_opert['Job Time Op1'] = time_workstation1_operation_list 
    df_wk2_opert['Job Number']   = workstation2_operation_list
    df_wk2_opert['Job Time Op2'] = time_workstation2_operation_list
    df_wk1_reles['Job Number']   = workstation1_release_list
    df_wk1_reles['Job Time Rl1'] = time_workstation1_release_list
    df_wk2_reles['Job Number']   = workstation2_release_list
    df_wk2_reles['Job Time Rl2'] = time_workstation2_release_list
    df_merge = pd.merge(df_wk1_schdl, df_wk1_opert, on='Job Number', how='left')
    df_merge = pd.merge(df_merge,     df_wk1_reles, on='Job Number', how='left')
    df_merge = pd.merge(df_merge,     df_wk2_schdl, on='Job Number', how='left')
    df_merge = pd.merge(df_merge,     df_wk2_opert, on='Job Number', how='left')
    df_merge = pd.merge(df_merge,     df_wk2_reles, on='Job Number', how='left')
    #.......................................
    # Computing measures of performance
    # Average Delay in Queues
    df_merge['Delay Wk1'] = df_merge['Job Time Op1'] - df_merge['Job Time Sc1']
    df_merge['Delay Wk2'] = df_merge['Job Time Op2'] - df_merge['Job Time Sc2']
    mean_delay_wk1 = df_merge['Delay Wk1'].mean()
    mean_delay_wk2 = df_merge['Delay Wk2'].mean()
    print('  ')
    print('Measures of Performance for Run: %1d' %(run+1) )
    print(' ')
    print('The average delay in queue for workstation 1 is %.2f hours'  % (mean_delay_wk1))
    print('The average delay in queue for workstation 2 is %.2f hours'  % (mean_delay_wk2))
    #............................................
    # Utilization of the Servers
    for i in range(0, len(df_merge)-1):
         workstation1_utilization_list.append(df_merge['Job Time Op1'][i+1] - df_merge['Job Time Rl1'][i])
         workstation2_utilization_list.append(df_merge['Job Time Op2'][i+1] - df_merge['Job Time Rl2'][i])
    wk1_sum_idle = np.nansum(workstation1_utilization_list)     
    wk2_sum_idle = np.nansum(workstation2_utilization_list)
    utilization_wk1 = round((1 - wk1_sum_idle / stop_arrivals) * 100, 2)
    utilization_wk2 = round((1 - wk2_sum_idle / stop_arrivals) * 100, 2)
    print(' ')
    print('The utilization of the workstation 1 is %.2f%%'  % (utilization_wk1))
    print('The utilization of the workstation 2 is %.2f%%'  % (utilization_wk2))
    #...............................................
    # Time weighted average of the queue length
    df_l1 = pd.DataFrame(workstation1_length_list, 
                         columns = ['len'])
    df_t1 = pd.DataFrame(workstation1_timeth_list,
                         columns = ['time'])
    df_qlength1 = pd.concat([df_l1, df_t1], axis = 1)
    # use the next row to figure out how long the queue was at that length
    df_qlength1['delta_time'] = df_qlength1['time'].shift(-1) - df_qlength1['time']
    # drop the last row because it would have an infinite time span
    df_qlength1 = df_qlength1[0:-1]
    len_avg_wk1 = np.average(df_qlength1['len'],
                             weights = df_qlength1['delta_time'])
    print(' ')
    print('The time weighted length of the workstation 1 is %.2f'  % (len_avg_wk1))
    #.....................................................
    # list and dataframe for final output
    listoflists = []
    listoflists.append(round(mean_delay_wk1,2))
    listoflists.append(round(mean_delay_wk2,2))
    listoflists.append(utilization_wk1)
    listoflists.append(utilization_wk2)
    listoflists.append(round(len_avg_wk1,2))
    df.loc[len(df)] = listoflists


def calc_ICs():
    ## confidence intervals
    ## define 3 global variables
    global df_output, hwic, l_end
    mean = round(df.mean(),2)
    sigma= round(df.std(ddof=1),2)
    dof  = len(df) -1
    t_crit = np.abs(stats.t.ppf((1-confidence)/2,dof))
    inf, sup = (mean-sigma*t_crit/np.sqrt(len(df)),    
                mean+sigma*t_crit/np.sqrt(len(df)))
    inf = round(inf,2)
    sup = round(sup,2)
    hwic= (sup-inf)/2
    if hwic[0] <= abs_err_delay_wk1:
        l_end = True
    print('')
    print(round(hwic[0],2),abs_err_delay_wk1, l_end )  
    df_output = pd.concat([mean, sigma, inf, sup], axis=1)
    print(df_output)


def print_output(): 
    # Table showing measures of performance for the last 20 independent runs
    df_last_20 = df.tail(20)
    row_labels = ['Run' + str(i+1) for i in range(run+1-20, run+1)]
    fig, ax = plt.subplots(1,1)
    ax.axis('tight')
    ax.axis('off')
    runs_table = ax.table(cellText=df_last_20.values, colLabels=df.columns,
                          rowLabels=row_labels, rowColours=["skyblue"]*(20),
                          colColours =["cyan"]*5, cellLoc='center', loc="center")
    ax.set_title("Measures of Performance", fontsize=18, y= 1.2 , pad = 4)
    runs_table.auto_set_font_size(False)
    runs_table.set_fontsize(8)
    plt.savefig('./' +'twoWKs_perf_measures_sequentialCI.png',
                bbox_inches='tight', dpi=150)
    plt.show()    
    # Output Data Table
    col_labels = ["Mean", "Std. Dev.", "Lower bound", "Upper Bound"]
    row_labels = ["Delay WK1 (h)","Delay WK2 (h)",
                  "Util. WK1 (%)","Util. WK2 (%)","Avg Length WK1"]
    fig, ax = plt.subplots(1,1)
    ax.axis('tight')
    ax.axis('off')
    output_table = ax.table(cellText = df_output.values,
                            colLabels = col_labels, rowLabels = row_labels,
                            rowColours =["skyblue"]*5,
                            colColours =["cyan"]*4,
                            cellLoc='center', loc="center")
    ax.set_title("Output data for %i independent runs" %(run+1),
                 fontsize=18,y= 0.8, pad = 4)
    output_table.auto_set_font_size(False)
    output_table.set_fontsize(8)
    plt.savefig('./' +'twoWKs_output_perf_measures_sequentialCI.png',
                bbox_inches='tight', dpi=150)
    plt.show()


confidence = 0.90
abs_err_delay_wk1 = 1.00
l_end = False
init_numb_of_runs = 500
numb_of_runs = init_numb_of_runs
seed_value = 2345
prbnumgen  = RandomState(seed_value)
hours_run_sim = 30 * 24
stop_arrivals = 720           # for the verification step

for run in range(numb_of_runs):
    workstation1_schedule_list, workstation2_schedule_list = [],[]
    workstation1_operation_list,workstation2_operation_list= [],[]
    workstation1_release_list,  workstation2_release_list  = [],[]
    time_workstation1_schedule_list, time_workstation2_schedule_list  = [],[]
    time_workstation1_operation_list,time_workstation2_operation_list = [],[]
    time_workstation1_release_list,  time_workstation2_release_list   = [],[]
    workstation1_length_list, workstation1_utilization_list = [],[]
    workstation1_timeth_list, workstation2_utilization_list = [],[]
    mean_delay_wk1,  mean_delay_wk2  = [],[]
    utilization_wk1, utilization_wk2 = [],[]
    len_avg_wk1,     len_avg_wk2     = [],[]
    listoflists = []
    df_wk1_schdl = pd.DataFrame(columns = ['Job Number', 'Job Time Sc1'])
    df_wk2_schdl = pd.DataFrame(columns = ['Job Number', 'Job Time Sc2'])
    df_wk1_opert = pd.DataFrame(columns = ['Job Number', 'Job Time Op1'])
    df_wk2_opert = pd.DataFrame(columns = ['Job Number', 'Job Time Op2'])
    df_wk1_reles = pd.DataFrame(columns = ['Job Number', 'Job Time Rl1'])
    df_wk2_reles = pd.DataFrame(columns = ['Job Number', 'Job Time Rl2'])
    # Set up the simulation environment
    env = simpy.Environment()
    work_station1 = simpy.Resource(env, NUMBER_WORK_STATION1)
    work_station2 = simpy.Resource(env, NUMBER_WORK_STATION2)
    env.process(generate_jobs(env, "Type1", JOBS_ARRIVAL_RATE, 0, 
                stop_arrivals, prbnumgen))
    env.run(until = hours_run_sim)
    calc_measures()
    if run >= 10:
        calc_ICs()
        if l_end == True:
            print_output() 
            break