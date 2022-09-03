# Emergency Room Simulation Model
# Non Terminating Simulation
# Batch Means Technique
# Import Modules
import pandas as pd
import numpy  as np
from numpy.random import RandomState
import simpy
from scipy import stats
from scipy.stats import uniform
from scipy.stats import truncnorm

# initialization module
# Unit of time = hours
PATIENT_ARRIVAL_RATE  = 1.2
NUMBER_ADMISSIONS_DESKS = 2
ADMISSION_MEAN = 0.3
ADMISSION_STD  = 0.15
HOSPITAL_MEAN = 25
HOSPITAL_STD  = 1.5
AMBULATORY_MEAN = 6
AMBULATORY_STD  = 1
NO_CARE_INF = 0.5
NO_CARE_SUP = 1.0
NUMBER_DOCS_HOSPITAL= 1
NUMBER_DOCS_AMBULAT = 5
NUMBER_DOCS_NO_CARE = 1
# discrete probabilities for three care levels
prob1, prob2, prob3 = 0.3, 0.6, 0.1
prob1 = round(prob1, 2)
prob2 = round(prob1 + prob2, 2)
prob3 = round(prob2 + prob3, 2)
list_of_probs = [prob1, prob2, prob3]
patient_arrival, arrival = [], []
patient_admission, patient_hospital_care = [], []
patient_ambulatory_care, patient_no_care = [], []
time_in_admission, delay_in_admission = [], []
time_in_hospital_care, delay_in_hospital_care = [], []
time_in_ambulatory_care, delay_in_ambulatory_care = [], []
time_in_no_care, delay_in_no_care = [], []
SIM_TIME = 8760


def generate_patient(env, patient_arrival_rate,inital_delay = 0,                 
                     stoptime = simpy.core.Infinity,
                     prng = RandomState(0)):
    number_of_patients = 0
    yield env.timeout(inital_delay)     # Initial delay 
    while (env.now <stoptime):  
        inter_arrival_time=prng.exponential(1.0/patient_arrival_rate)
        left, right = 0, np.inf 
        loc1, scale1 = ADMISSION_MEAN, ADMISSION_STD
        loc2, scale2 = HOSPITAL_MEAN,  HOSPITAL_STD
        loc3, scale3 = AMBULATORY_MEAN,AMBULATORY_STD
        a1 = (left - loc1)/scale1
        b1 = (right - loc1)/scale1
        a2 = (left - loc2)/scale2
        b2 = (right - loc2)/scale2
        a3 = (left - loc3)/scale3
        b3 = (right - loc3)/scale3   
        los_admis = truncnorm.rvs(a1,b1,loc1, scale1 ,size=1)
        los_hosp  = truncnorm.rvs(a2,b2,loc2, scale2 ,size=1)
        los_ambu  = truncnorm.rvs(a3,b3,loc3, scale3 ,size=1)
        los_exit  = uniform.rvs(loc=NO_CARE_INF, scale=NO_CARE_SUP+1, size=1)
        number_of_patients += 1
        pat_str = patient_stream(env, 'Patient number: {}'.format(number_of_patients),
                                 los_admis, los_hosp,los_ambu, los_exit)
        env.process(pat_str)
        yield env.timeout(inter_arrival_time)


def patient_stream(env, patient_number, los_admis, 
                   los_hosp, los_ambu, los_exit):
    #  Admission
    print("%3s is arriving for admission at %.2f" %(patient_number, env.now))
    patient_arrival.append(patient_number)
    arrival_time = env.now
    arrival.append(arrival_time)
    adm_request_desk = admission_desks.request()
    yield adm_request_desk
    print("%3s admitted to admission at %.2f" %(patient_number, env.now))
    time_in_admission.append(env.now)
    if (env.now > arrival_time):
        delay_in_admission.append(env.now - arrival_time)
        patient_admission.append(patient_number)
        print("%3s has to wait %.2f' for admission" %(patient_number, env.now - arrival_time))
    yield env.timeout(los_admis)
    print('%3s stays at admission %.2f' % (patient_number,los_admis))
    admission_desks.release(adm_request_desk)
    # uniform distribution for level assigments
    r_v = uniform.rvs(size=1)
    if r_v < prob1:
        stream = 1
    elif r_v < prob2:
        stream = 2
    else:
        stream = 3
    if stream == 1:
        # Hospital Care
        print('%3s is arriving for hospital care at %.2f' % (patient_number,env.now))
        arrival_time = env.now
        time_in_hospital_care.append(arrival_time)
        hospital_care_request = hospital_care.request()
        yield hospital_care_request
        print('%3s is admitted to hospital care at %.2f' % (patient_number,env.now))
        if (env.now > arrival_time):
            delay_in_hospital_care.append(env.now - arrival_time)
            patient_hospital_care.append(patient_number)
            print('%3s has to wait for hospital care for %.2f'
                    %(patient_number, env.now - arrival_time)) 
    
        yield env.timeout(los_hosp)
        print('%3s stays at hospital care at %.2f' % (patient_number,los_hosp))
        hospital_care.release(hospital_care_request)
    elif stream == 2:
        #  ambulatory care
        print('%3s is arriving for ambultory care at %.2f' % (patient_number,env.now))
        arrival_time = env.now
        time_in_ambulatory_care.append(arrival_time)
        ambulatory_care_request = ambulatory_care.request()
        yield ambulatory_care_request
        print('%3s is admitted to ambulatory care at %.2f' % (patient_number,env.now))
        if (env.now > arrival_time):
            delay_in_ambulatory_care.append(env.now - arrival_time)
            patient_ambulatory_care.append(patient_number)
            print('%3s has to wait for ambulatory care for %.2f' %
                    (patient_number, env.now - arrival_time))
        yield env.timeout(los_ambu)
        print('%3s stays at ambulatory care at %.2f' % (patient_number,los_ambu))
        ambulatory_care.release(ambulatory_care_request)
    elif stream == 3:
        #  no care
        print('%3s is arriving for no care at %.2f' % (patient_number,env.now))
        arrival_time = env.now
        time_in_no_care.append(arrival_time)
        no_care_request = no_care_level.request()
        yield no_care_request
        print('%3s is admitted to no care at %.2f' % (patient_number,env.now))
        if (env.now > arrival_time):
            delay_in_no_care.append(env.now - arrival_time)
            patient_no_care.append(patient_number)
            print('%3s has to wait for no care for %.2f' % 
                    (patient_number, env.now - arrival_time))
        yield env.timeout(los_exit)
        print('%3s stays at no care at %.2f' % (patient_number,los_exit))
        no_care_level.release(no_care_request)


def calc_batches():
    ## delay in ambulatory care
    global inf, sup, delay_in_ambulatory_care
    number_batchs = 13        # selected by the analyst
    number_recs    = len(delay_in_ambulatory_care)
    recs_per_batch = int(number_recs/number_batchs)
    # to guarantee equal number of records in each batch
    matrix_dim = number_batchs*recs_per_batch
    rows_to_eliminate = number_recs - matrix_dim   
    delay_in_ambulatory_care = delay_in_ambulatory_care[rows_to_eliminate:]
    # eliminating transient effects (warm-up period)
    delay_in_ambulatory_care = delay_in_ambulatory_care[recs_per_batch:]
    matrix = []
    while delay_in_ambulatory_care != []:
        matrix.append(delay_in_ambulatory_care[:recs_per_batch])
        delay_in_ambulatory_care = delay_in_ambulatory_care[recs_per_batch:]   
    number_batchs = number_batchs - 1   # the warm-up batch                                         
    dof  = number_batchs - 1
    confidence = 0.90                   # selected by the analyst
    t_crit = np.abs(stats.t.ppf((1-confidence)/2,dof))
    batch_means = np.mean(matrix, axis = 1)
    batch_std   = np.std(matrix,  axis = 1)
    average_batch_means  = np.mean(batch_means,axis = 0)
    standard_batch_means = np.std(batch_means, axis = 0)
    inf = average_batch_means - \
          standard_batch_means*t_crit/np.sqrt(number_batchs)
    sup = average_batch_means + \
          standard_batch_means*t_crit/np.sqrt(number_batchs)
    inf = round(float(inf),2)
    sup = round(float(sup),2)
    print('')
    print('Simulation of an Emergency Room')
    print('')
    print('%3s patients arrived at the emergency room' % (len(patient_arrival)))
    print('%3s patients derived to ambulatory care' % (number_recs))
    print('%3s batches of %3s records were used for calculations' % (number_batchs, recs_per_batch))
    print ('')
    print('The average delay in ambulatory care belongs to the interval %3s %3s' % (inf, sup))


env = simpy.Environment()
admission_desks = simpy.Resource(env,
                                 capacity = NUMBER_ADMISSIONS_DESKS)
hospital_care   = simpy.Resource(env, 
                                 capacity = NUMBER_DOCS_HOSPITAL)
ambulatory_care = simpy.Resource(env, 
                                 capacity = NUMBER_DOCS_AMBULAT)
no_care_level   = simpy.Resource(env, 
                                 capacity = NUMBER_DOCS_NO_CARE)
prng = RandomState(1234)
stop_arrivals = 2000
env.process(generate_patient(env,PATIENT_ARRIVAL_RATE, 0,
            stop_arrivals, prng ))
env.run(until = SIM_TIME)
calc_batches()