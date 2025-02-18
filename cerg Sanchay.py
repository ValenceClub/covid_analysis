# -*- coding: utf-8 -*-
"""
Created on Fri Jun 18 20:08:35 2021

@author: Chandraniva
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import csv

infectives_obs = []
recovered_obs = []
total_inf_obs =[]

with open('case_time_series.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter = ',')
    for row in plots:
        infectives_obs.append(int(row[2]))
        recovered_obs.append(int(row[5]))
        total_inf_obs.append(int(row[3]))
        
def get_binned_data(x,bin_size=7):
    x=np.array(x)
    l = len(x)
    x_binned = []
    for i in range(int(len(x)/bin_size)):
        x_binned.append(sum(x[(i*bin_size):(i*bin_size+bin_size)]/bin_size))
    
    if len(x[int(l/bin_size)*bin_size:l]) != 0:
        x_binned.append(sum(x[int(l/bin_size)*bin_size:l])/len(x[int(l/bin_size)*bin_size:l]))
        
    return x_binned

def plot_data(x,lab='No label provided'):
    plt.plot(np.linspace(0,len(x)-1,len(x)), x, label=lab)
    
    
infectives_binned = get_binned_data(infectives_obs[90:378],1)
plot_data(infectives_binned,'Observed infectives')  
rec_binned = get_binned_data(recovered_obs[90:378],1)
plot_data(rec_binned,'Recovered')
total_inf_binned = get_binned_data(total_inf_obs[90:378],1)
plot_data(total_inf_binned,'Observed cumulative infectives') 

def sigmoid(t,A,gamma,b):
    I = A/(b+np.exp(-gamma*t))
    return I

ts = np.linspace(0,len(total_inf_binned)-1,len(total_inf_binned))
A1, gamma1, b1 = curve_fit(sigmoid,ts,total_inf_binned)[0] 
print("1st wave: A and gamma are",A1, gamma1)

curve = sigmoid(ts,A1,gamma1,b1)
plot_data(curve,'Best fit: Cumulative infectives')

plt.legend(loc='best')
plt.xlabel('time (days)')
plt.grid()
plt.show()

" *********************************   SECOND WAVE   ****************************************** "

def sigmoid_with_strolling(t,A,gamma,b,I_stroll):
    I = A/(b+np.exp(-gamma*t)) + I_stroll*t/A/gamma
    return I


total_inf_binned_second_wave = get_binned_data((np.array(total_inf_obs[378:])-
                                                np.array(total_inf_obs[377])),1)
plot_data(total_inf_binned_second_wave,'2nd wave: cumulative infectives') 

ts = np.linspace(0,len(total_inf_binned_second_wave)-1,len(total_inf_binned_second_wave))
A2, gamma2, b2,  I_stroll1 = curve_fit(sigmoid_with_strolling,ts,total_inf_binned_second_wave,
                                       p0 = [38897.07690404634, 0.5524355218215301,\
                                             0.002013665870266782, 0.01])[0] 
print("\n2nd wave: A, gamma, b and I_stroll are", A2, gamma2, b2, I_stroll1)

curve = sigmoid_with_strolling(ts,A2,gamma2,b2, I_stroll1)
plot_data(curve,'Best fit: Cumulative infectives')

plt.legend(loc='best')
plt.xlabel('time (days)')
plt.grid()
plt.show()

" *******************************   BETA FUNCTION   **************************************** "

total_inf_binned = get_binned_data(total_inf_obs[90:],1)
infectives_binned = get_binned_data(infectives_obs[90:],1)

plt.plot(total_inf_binned/A2, infectives_binned/A2, label='-Beta(curly_I)')

def beta_cerg(curlyI, delta0, p_0, Xi1, delta1, p1):
    beta = curlyI*  (abs((1-curlyI)**2 + delta0)**p_0)  * (abs((1-Xi1*curlyI)**2 + delta1)**p1)
    return beta

curly_Is = np.linspace(0,len(total_inf_binned)-1,len(total_inf_binned))

delta0, p_0, Xi1, delta1, p1 = curve_fit(beta_cerg,total_inf_binned/A2,\
                                        infectives_binned/A2, \
                                        p0=[-9000.4402424998057, -1.429326799040603, 0.0018099898169848315, 0.1456914981484282, -2.18440545248528]
                                        , method='lm')[0]

    
curve =  beta_cerg(total_inf_binned/A2, delta0, p_0, Xi1, delta1, p1)
plt.plot(total_inf_binned/A2, curve, label = 'Best fit: -Beta(curly_I)')   

print("\nParameters: delta0, p_0, Xi1, delta1, p1 are:",delta0, p_0, Xi1, delta1, p1)


plt.xlabel("curly_I: Total infectives")
plt.ylabel("$d(curly_I)/d(tau)$")
plt.legend()
plt.grid()
plt.show()

#p0 = [1e-1,0.55,0.001,1e-2,0.55]