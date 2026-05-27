'''
class Member: Contains the data structure of a cipher, including properties useful in the genetic algorithm.
class Generation: Contains info about the current generation
'''

from cipher.linear_functions import *
from cipher.sbox_functions import *
import analysis.latency_computation as latency
import analysis.security_computation as security
import cipher.components as components

import utils
import numpy as np
import config
from copy import deepcopy
from concurrent.futures import ProcessPoolExecutor
import json
from yosys.main import Yosys
import os

from seed_config import SEED, set_global_seed
set_global_seed(SEED)

class Member:
    def __init__(self):
        self.num_rounds = 0
        self.security_diff = None
        self.diff_trails = None
        self.security_linear = None
        self.linear_trails = None
        self.latency = None
        self.fitness = None
        self.diversity = None
        self.round_functions = []
        self.pop_index = None
        self.gen_index = None
        self.identifier = None

    def randomize(self,nr=1):
        self.round_functions = []
        for n in range(nr-1):
            r = components.round_function()
            r.randomize()
            self.add_round_function(r)
        r = components.round_function()
        r.randomize()
        r.linear = None
        self.add_round_function(r)
        # self.print_member()

    def steal_one_round(self,generation):
        # member function that steal a round from someone in the generation
        r = components.round_function()
        r.steal_one_round(generation,self) # give the generation and what member (mainly to extract info from it)
        if self.num_rounds % 2 == 0: # add to the front
            self.round_functions.insert(0,r)
            for i,rf in enumerate(self.round_functions):
                rf.round_index = i
            self.num_rounds += 1
        else:
            self.round_functions[-1].linear = r.linear
            r.linear = None
            self.add_round_function(r)
        
    def smart_randomize_one_round(self):
        r = components.round_function()
        try:
            if self.num_rounds % 2 == 0: # add to the front
                diff_trail = self.diff_trails[0].before
                linear_trail = self.linear_trails[0].before
            else:
                diff_trail = self.diff_trails[-1].after
                linear_trail = self.linear_trails[-1].after
        except:
            diff_trail = None
            linear_trail = None

        r.smart_randomize(diff_trail=diff_trail,linear_trail=linear_trail,front=self.num_rounds % 2)

        if self.num_rounds % 2 == 0: # add to the front
            self.round_functions.insert(0,r)
            for i,rf in enumerate(self.round_functions):
                rf.round_index = i
            self.num_rounds += 1
        else: # add to the back
            self.round_functions[-1].linear = r.linear
            r.linear = None
            self.add_round_function(r)



    def add_round_function(self,round_function):
        round_function.round_index = self.num_rounds
        self.round_functions.append(round_function)
        self.num_rounds += 1

    def mutate(self,prob):
        for round_function in self.round_functions:
            if np.random.uniform(0,1) >= prob: continue
            round_function.mutate()
    
    def compute_fitness(self):
        # docker_instance = openlane_containers.openlane_containers.get()
        # self.latency = self.compute_latency(docker_instance)
        self.latency = self.compute_latency()
        # openlane_containers.openlane_containers.put(docker_instance)
        window = min(self.num_rounds,config.SECURITY['MAX_WINDOW'])
        # print(window,self.num_rounds,self.pop_index)
        self.security_diff,self.diff_trails = self.compute_diff_security(window)
        self.security_linear,self.linear_trails = self.compute_linear_security(window)
        self.fitness = config.GENETIC_FUNCTIONS['FITNESS_FORMULA'][window](min(self.security_diff + [2*s for s in self.security_linear]),self.latency,self.num_rounds)
        return
    
    # Generating the cnf formula given the necessary details
    def _generate_diff_cnf(self,vars_before_subst,vars_after_subst,probability_vars,auxiliary_vars,probability,window_length,start_of_window,cnf=None):
        statements = []
        if cnf == None:
            # avoid trivial case
            s = ''
            for var in vars_before_subst[0]:
                s += '%s ' % (var)
            s += '0'
            statements.append(s)
            # round function
            for n_index,n in enumerate(range(start_of_window,start_of_window + window_length)):
                sec_statements = security.differential.get_subst_layer_cnf(\
                    self.round_functions[n].substitution,vars_before_subst[n_index],vars_after_subst[n_index],\
                    probability_vars[n_index],self.pop_index,config.FILE_PATHS['MAIN_FILE'])
                statements.extend(sec_statements)
                if n == (start_of_window + window_length - 1): continue # we ignore the last linear layer
                lin_statements = security.differential.get_linear_layer_cnf(\
                    self.round_functions[n].linear,vars_after_subst[n_index],vars_before_subst[n_index+1])
                statements.extend(lin_statements)
            cnf = deepcopy(statements) # to save some computation time
        else:
            statements = deepcopy(cnf)
        # forming the probabilities
        prob_statements = security.common.sequential_encoding(probability_vars,auxiliary_vars,probability)
        statements.extend(prob_statements)
        return statements,cnf
    
    # Computing a single instance of SAT
    def _compute_diff_cnf_using_sat(self,probability,window_length,start_of_window,cnf=None):
        input_sat_file = './%s_tmp/sat_diff_tmp/sec_%s_input.cnf' % (config.FILE_PATHS['MAIN_FILE'],self.pop_index)
        output_sat_file = './%s_tmp/sat_diff_tmp/sec_%s_output.cnf' % (config.FILE_PATHS['MAIN_FILE'],self.pop_index)
        vars_before_subst,vars_after_subst,auxiliary_vars,probability_vars,variable_count = security.common.generate_cnf_vars(probability,window_length)
        statements,cnf = self._generate_diff_cnf(vars_before_subst,vars_after_subst,probability_vars,auxiliary_vars,probability,window_length,start_of_window,cnf=cnf)
        statements.insert(0,'p cnf %s %s' % (variable_count-1,len(statements)))

        utils.write_to_file(input_sat_file,statements)
        sat_bool = security.common.run_sat_solver(input_sat_file,output_sat_file)
        if sat_bool == 'sat':
            self.diff_trails[start_of_window].reset()
            self.diff_trails[start_of_window].start = start_of_window
            self.diff_trails[start_of_window].read_trails_from_cnf(output_sat_file,vars_before_subst,vars_after_subst,probability_vars)
        return sat_bool,cnf

    # Given a window, computing the best differential characteristic
    def _compute_single_diff_security(self,init_probability,window_length,start_of_window=0):
        probability_bounds = [0,init_probability]
        # compute the upper bound
        cnf = None
        while True:
            sat_bool, cnf = self._compute_diff_cnf_using_sat(probability_bounds[1],window_length,start_of_window,cnf)
            if sat_bool == 'sat': 
                # print('upper bound is %s' % (probability_bounds))
                break # we found the upper bound
            elif sat_bool == 'unsat':
                probability_bounds[0] = probability_bounds[1]
                probability_bounds[1] = min(config.SECURITY['MAX_DIFF_SECURITY'], probability_bounds[1] + 2) # increment of 2 each time
            if probability_bounds[0] == probability_bounds[1] == config.SECURITY['MAX_DIFF_SECURITY']: # exceeded what we limited
                return config.SECURITY['MAX_DIFF_SECURITY']
        # compute the lower bound
        while True:
            if probability_bounds[0] >= probability_bounds[1] - 1: # terminating criteria
                return probability_bounds[1]
            else:
                probability = max(probability_bounds[0]+1,probability_bounds[1]-1)
                sat_bool, cnf = self._compute_diff_cnf_using_sat(probability,window_length,start_of_window,cnf)
                if sat_bool == 'sat': probability_bounds[1] = probability
                else: probability_bounds[0] = probability
                # print('lower bound is %s' % (probability_bounds))

    # Compute a list of best differential characteristics (windows)
    def compute_diff_security(self,window_length,start=0,end=999):
        if window_length >= self.num_rounds:
            self.diff_trails = [components.trail()]
            self.security_diff = [self._compute_single_diff_security(config.SECURITY['INIT_DIFF_SECURITY'][window_length],window_length,0)]
        else: 
            self.security_diff = []
            self.diff_trails = [components.trail() for _ in range(start,min(end,self.num_rounds+1-window_length))]
            for start_of_window in range(start,min(end,self.num_rounds+1-window_length)):
                self.security_diff.append(self._compute_single_diff_security(config.SECURITY['INIT_DIFF_SECURITY'][window_length],window_length,start_of_window))
        return self.security_diff,self.diff_trails
    
    # Generating the cnf formula given the necessary details
    def _generate_linear_cnf(self,vars_before_subst,vars_after_subst,correlation_vars,auxiliary_vars,correlation,start_of_window,window_length,cnf=None):
        statements = []
        if cnf == None:
            # avoid trivial case
            s = ''
            for var in vars_before_subst[0]:
                s += '%s ' % (var)
            s += '0'
            statements.append(s)
            # round function
            for n_index,n in enumerate(range(start_of_window,start_of_window + window_length)):
                sec_statements = security.linear.get_subst_layer_cnf(\
                    self.round_functions[n].substitution,vars_before_subst[n_index],vars_after_subst[n_index],\
                    correlation_vars[n_index],self.pop_index,config.FILE_PATHS['MAIN_FILE'])
                statements.extend(sec_statements)
                if n == (start_of_window + window_length - 1): continue # we ignore the last linear layer
                lin_statements = security.linear.get_linear_layer_cnf(\
                    self.round_functions[n].linear,vars_after_subst[n_index],vars_before_subst[n_index+1])
                statements.extend(lin_statements)
            cnf = deepcopy(statements) # to save some computation time
        else:
            statements = deepcopy(cnf)
        # forming the probabilities
        prob_statements = security.common.sequential_encoding(correlation_vars,auxiliary_vars,correlation)
        statements.extend(prob_statements)
        return statements,cnf

    # Computing a single instance of SAT
    def _compute_linear_cnf_using_sat(self,correlation,start_of_window,window_length,cnf=None):
        input_sat_file = './%s_tmp/sat_linear_tmp/sec_%s_input.cnf' % (config.FILE_PATHS['MAIN_FILE'],self.pop_index)
        output_sat_file = './%s_tmp/sat_linear_tmp/sec_%s_output.cnf' % (config.FILE_PATHS['MAIN_FILE'],self.pop_index)
        vars_before_subst,vars_after_subst,auxiliary_vars,correlation_vars,variable_count = security.common.generate_cnf_vars(correlation,window_length)

        statements,cnf = self._generate_linear_cnf(vars_before_subst,vars_after_subst,correlation_vars,auxiliary_vars,correlation,start_of_window,window_length,cnf=cnf)
        statements.insert(0,'p cnf %s %s' % (variable_count-1,len(statements)))

        utils.write_to_file(input_sat_file,statements)
        sat_bool = security.common.run_sat_solver(input_sat_file,output_sat_file)
        if sat_bool == 'sat':
            self.linear_trails[start_of_window].reset()
            self.linear_trails[start_of_window].start = start_of_window
            self.linear_trails[start_of_window].read_trails_from_cnf(output_sat_file,vars_before_subst,vars_after_subst,correlation_vars)
        return sat_bool,cnf

    # Given a window, computing the best linear trail
    def _compute_single_linear_security(self,init_correlation,window_length,start_of_window=0):
        correlation_bounds = [0,init_correlation]
        # compute the upper bound
        cnf = None
        while True:
            sat_bool, cnf = self._compute_linear_cnf_using_sat(correlation_bounds[1],start_of_window,window_length,cnf)
            if sat_bool == 'sat': break # we found the upper bound
            elif sat_bool == 'unsat':
                correlation_bounds[0] = correlation_bounds[1]
                correlation_bounds[1] = min(config.SECURITY['MAX_LINEAR_SECURITY'], correlation_bounds[1] + 2) # increment of 2 each time
            if correlation_bounds[0] == correlation_bounds[1] == config.SECURITY['MAX_LINEAR_SECURITY']: # exceeded what we limited
                return config.SECURITY['MAX_LINEAR_SECURITY']
        # compute the lower bound
        while True:
            if correlation_bounds[0] >= correlation_bounds[1] - 1: # terminating criteria
                return correlation_bounds[1]
            else:
                correlation = max(correlation_bounds[0]+1,correlation_bounds[1]-1)
                sat_bool, cnf = self._compute_linear_cnf_using_sat(correlation,start_of_window,window_length)
                if sat_bool == 'sat': correlation_bounds[1] = correlation
                else: correlation_bounds[0] = correlation
    
    # Compute a list of best linear trails (windows)
    def compute_linear_security(self,window_length,start=0,end=999):
        if window_length >= self.num_rounds:
            self.linear_trails = [components.trail()]
            self.security_linear = [self._compute_single_linear_security(config.SECURITY['INIT_LINEAR_SECURITY'][window_length],window_length,0)]
        else: 
            self.linear_trails = [components.trail() for _ in range(start,min(end,self.num_rounds+1-window_length))]
            self.security_linear = []
            for start_of_window in range(start,min(end,self.num_rounds+1-window_length)):
                self.security_linear.append(self._compute_single_linear_security(config.SECURITY['INIT_LINEAR_SECURITY'][window_length],window_length,start_of_window))
        return self.security_linear,self.linear_trails

    def _prepare_verilog_statements(self,verilog_file):
        statements = []
        statement = latency.prepare_preamble(self.num_rounds,verilog_file)
        statements.extend(statement)

        # Settling the key schedule and constants
        for n in range(self.num_rounds+1): 
            statement = latency.get_key_schedule_and_const(mkey_index=n % 2, rkey_index=n, constant_index=n); 
            statements.append(statement)

        # XOR the keys
        statements.append('\tassign t[%s] = x ^ kn[%s];' % (0,0));
        for n in range(1,self.num_rounds):
            statement = latency.get_add_key(t_index=3*n-1, rkey_index=n)
            statements.append(statement)
        statements.append('\tassign t[%i] = t[%i] ^ kn[%i];' % (3*n+2,3*n+1,self.num_rounds))
        statements.append('\tassign y = t[%i];' % (3*n+2))

        # subst layers
        for n in range(self.num_rounds):
            statement = latency.get_subst_layer(3*n,2*n); 
            statements.append(statement)

        # linear layers
        for n in range(1,self.num_rounds):
            statement = latency.get_linear_layer(3*n-2,2*n-1)
            statements.append(statement)

        statements.append('\tendmodule\n')

        # substLayer calling the sboxes
        for n in range(self.num_rounds):
            statement = latency.get_sboxes_in_subst_layer(2*n)
            statements.append(statement)

        # sboxes implementation
        for n in range(self.num_rounds):
            for i in range(16):
                statement = latency.get_sboxes_implementation(self.round_functions[n].substitution.sboxes[i],2*n,i)
                statements.append(statement)

        # linear implementation
        for n in range(self.num_rounds-1):
            statement = latency.get_matrix_implementation(self.round_functions[n].linear.matrix,2*n+1)
            statements.append(statement)

        # key add const implementation
        statement = latency.get_key_add_and_const_implementation()
        statements.append(statement)
        return statements

    def get_prince_full(self,nr):
        prince_sbox = [0xB,0xF,0x3,0x2,0xA,0xC,0x9,0x1,0x6,0x7,0x8,0x0,0xE,0x5,0xD,0x4]
        prince_m1 = linear_functions.get_prince_m1()
        prince_m2 = linear_functions.get_prince_m2()
        zero_matrix = np.zeros((16,16),dtype=int)
        prince_mc = linear_functions.get_aes_shiftrows().dot(np.block([
                                  [prince_m1,zero_matrix,zero_matrix,zero_matrix],
                                  [zero_matrix,prince_m2,zero_matrix,zero_matrix],
                                  [zero_matrix,zero_matrix,prince_m2,zero_matrix],
                                  [zero_matrix,zero_matrix,zero_matrix,prince_m1],]))
        prince_matrix = linear_functions.get_aes_shiftrows().dot(prince_mc)
        prince_matrix_inverse = linear_functions.inverse(prince_matrix)
        prince_inv_sbox = [-1 for _ in range(16)]
        for i in range(16): prince_inv_sbox[prince_sbox[i]] = i

        if nr % 2 == 0: 
            front = (nr-2) // 2
        else: 
            front = (nr-2) // 2 + 1
        back = nr - front - 2
        for _ in range(front):
            r = components.round_function()
            r_subst = components.substitution_layer()
            for _ in range(16): r_subst.add_sbox(prince_sbox)
            r.add_substitution_layer(r_subst)
            r_linear = components.linear_layer()
            r_linear.matrix = prince_matrix
            r.add_linear_layer(r_linear)
            self.add_round_function(r)

        # middle layer
        r = components.round_function()
        r_subst = components.substitution_layer()
        for _ in range(16): r_subst.add_sbox(prince_sbox)
        r.add_substitution_layer(r_subst)
        r_linear = components.linear_layer()
        r_linear.matrix = prince_mc
        r.add_linear_layer(r_linear)
        self.add_round_function(r)

        r = components.round_function()
        r_subst = components.substitution_layer()
        for _ in range(16): r_subst.add_sbox(prince_inv_sbox)
        r.add_substitution_layer(r_subst)

        for _ in range(back):
            r_linear = components.linear_layer()
            r_linear.matrix = prince_mc
            r.add_linear_layer(r_linear)
            self.add_round_function(r)
            r = components.round_function()
            r_subst = components.substitution_layer()
            for _ in range(16): r_subst.add_sbox(prince_inv_sbox)
            r.add_substitution_layer(r_subst)
        r.linear = None
        self.add_round_function(r)
        return

    def get_uknitbc(self,nr,window=0):
        file = '../uknit64_cipher.pkl'
        cipher = utils.pickle_load(file)

        self.round_functions = []
        self.num_rounds = 0
        for n in range(window,nr+window-1):
            self.add_round_function(cipher.round_functions[n])
        rf = cipher.round_functions[nr+window-1]
        rf.linear = None
        self.add_round_function(rf)

    def get_prince(self,nr):
        # this only implements the front of prince
        prince_sbox = [0xB,0xF,0x3,0x2,0xA,0xC,0x9,0x1,0x6,0x7,0x8,0x0,0xE,0x5,0xD,0x4]
        prince_m1 = linear_functions.get_prince_m1()
        prince_m2 = linear_functions.get_prince_m2()
        zero_matrix = np.zeros((16,16),dtype=int)
        prince_matrix = linear_functions.get_aes_shiftrows().dot(np.block([
                                  [prince_m1,zero_matrix,zero_matrix,zero_matrix],
                                  [zero_matrix,prince_m2,zero_matrix,zero_matrix],
                                  [zero_matrix,zero_matrix,prince_m2,zero_matrix],
                                  [zero_matrix,zero_matrix,zero_matrix,prince_m1],]))
        self.round_functions = []
        self.num_rounds = 0
        for n in range(nr-1):
            r = components.round_function()
            r_subst = components.substitution_layer()
            for _ in range(16): r_subst.add_sbox(prince_sbox)
            r.add_substitution_layer(r_subst)
            r_linear = components.linear_layer()
            r_linear.matrix = prince_matrix
            r.add_linear_layer(r_linear)
            self.add_round_function(r)
        r = components.round_function()
        r_subst = components.substitution_layer()
        for _ in range(16): r_subst.add_sbox(prince_sbox)
        r.add_substitution_layer(r_subst)
        r.linear = None
        self.add_round_function(r)


    def compute_latency(self):
        verilog_file = 'design_%s_%s.v' % (config.FILE_PATHS['MAIN_FILE'],self.pop_index)
        statements = self._prepare_verilog_statements(verilog_file)
        utils.write_to_file('./%s_tmp/verilog/' % (config.FILE_PATHS['MAIN_FILE']) + verilog_file,statements)
        user_config = {
        "VERILOG_FILES": ["./%s_tmp/verilog/" % (config.FILE_PATHS['MAIN_FILE']) + verilog_file], # verilog file
        "DESIGN_NAME": "design_main_%s" % (self.pop_index), # the top module in the verilog files
        "ABC_OUTPUT_FILE" : "abc_%s.log" % (self.pop_index),
        "YOSYS_OUTPUT_FILE" : "yosys_%s.log" % (self.pop_index),
        "SAVE_NETLIST" : "design_main_%s.nl.v" % (self.pop_index), # file containing the final netlist
        }
        yosys = Yosys(user_config,self.pop_index,directory='./yosys/')
        yosys.run_yosys()
        return yosys.latency



    def is_equal(self,member):
        for i in range(self.num_rounds):
            if not self.round_functions[i].is_equal(member.round_functions[i]):
                return False
        return True
 
    def breed(self,member):
        if len(member.round_functions) != len(self.round_functions):
            raise Exception('Unable to breed 2 members with different round functions!')
        childA = Member()
        childB = Member()
        # there are 3 types of crossover breeding
        choice = np.random.choice(list(config.GENETIC_ALGO['CROSSOVER'].keys()),p=list(config.GENETIC_ALGO['CROSSOVER'].values()))
        if choice == 'SINGLE':
            cut = np.random.randint(1,2 * self.num_rounds - 1) # we can perform cut at (number of components - 1) positions
            for component_index in range(cut):
                if component_index % 2 == 0: # substitution
                    childA_r = components.round_function()
                    childB_r = components.round_function()
                    childA_r.add_substitution_layer(deepcopy(self.round_functions[component_index//2].substitution))
                    childB_r.add_substitution_layer(deepcopy(member.round_functions[component_index//2].substitution))
                else: # linear
                    childA_r.add_linear_layer(deepcopy(self.round_functions[component_index//2].linear))
                    childB_r.add_linear_layer(deepcopy(member.round_functions[component_index//2].linear))
                    childA.add_round_function(childA_r)
                    childB.add_round_function(childB_r)
            for component_index in range(cut,2 * self.num_rounds):
                if component_index % 2 == 0: # substitution
                    childA_r = components.round_function(); childA_r.round_index = component_index // 2
                    childB_r = components.round_function(); childB_r.round_index = component_index // 2
                    childA_r.add_substitution_layer(deepcopy(member.round_functions[component_index//2].substitution))
                    childB_r.add_substitution_layer(deepcopy(self.round_functions[component_index//2].substitution))
                else: # linear
                    childA_r.add_linear_layer(deepcopy(member.round_functions[component_index//2].linear))
                    childB_r.add_linear_layer(deepcopy(self.round_functions[component_index//2].linear))
                    childA.add_round_function(childA_r)
                    childB.add_round_function(childB_r)
        
        elif choice == 'DOUBLE':
            cut = np.random.choice(range(1,2 * self.num_rounds - 1), size=2, replace=False)
            cut.sort()
            for component_index in range(cut[0]):
                if component_index % 2 == 0: # substitution
                    childA_r = components.round_function(); childA_r.round_index = component_index // 2
                    childB_r = components.round_function(); childB_r.round_index = component_index // 2
                    childA_r.add_substitution_layer(deepcopy(self.round_functions[component_index//2].substitution))
                    childB_r.add_substitution_layer(deepcopy(member.round_functions[component_index//2].substitution))
                else: # linear
                    childA_r.add_linear_layer(deepcopy(self.round_functions[component_index//2].linear))
                    childB_r.add_linear_layer(deepcopy(member.round_functions[component_index//2].linear))
                    childA.add_round_function(childA_r)
                    childB.add_round_function(childB_r)
            for component_index in range(cut[0],cut[1]):
                if component_index % 2 == 0: # substitution
                    childA_r = components.round_function(); childA_r.round_index = component_index // 2
                    childB_r = components.round_function(); childB_r.round_index = component_index // 2
                    childA_r.add_substitution_layer(deepcopy(member.round_functions[component_index//2].substitution))
                    childB_r.add_substitution_layer(deepcopy(self.round_functions[component_index//2].substitution))
                else: # linear
                    childA_r.add_linear_layer(deepcopy(member.round_functions[component_index//2].linear))
                    childB_r.add_linear_layer(deepcopy(self.round_functions[component_index//2].linear))
                    childA.add_round_function(childA_r)
                    childB.add_round_function(childB_r)
            for component_index in range(cut[1], 2 * self.num_rounds):
                if component_index % 2 == 0: # substitution
                    childA_r = components.round_function(); childA_r.round_index = component_index // 2
                    childB_r = components.round_function(); childB_r.round_index = component_index // 2
                    childA_r.add_substitution_layer(deepcopy(self.round_functions[component_index//2].substitution))
                    childB_r.add_substitution_layer(deepcopy(member.round_functions[component_index//2].substitution))
                else: # linear
                    childA_r.add_linear_layer(deepcopy(self.round_functions[component_index//2].linear))
                    childB_r.add_linear_layer(deepcopy(member.round_functions[component_index//2].linear))
                    childA.add_round_function(childA_r)
                    childB.add_round_function(childB_r)
        elif choice == 'UNIFORM':
            for component_index in range(2 * self.num_rounds):
                if component_index % 2 == 0: # substitution
                    childA_r = components.round_function(); childA_r.round_index = component_index // 2
                    childB_r = components.round_function(); childB_r.round_index = component_index // 2

                    substA = components.substitution_layer()
                    substB = components.substitution_layer()
                    for sbox_index in range(16):
                        if np.random.randint(0,2) == 0:
                            substA.add_sbox(deepcopy(self.round_functions[component_index//2].substitution.sboxes[sbox_index]))
                            substB.add_sbox(deepcopy(member.round_functions[component_index//2].substitution.sboxes[sbox_index]))
                        else:
                            substA.add_sbox(deepcopy(member.round_functions[component_index//2].substitution.sboxes[sbox_index]))
                            substB.add_sbox(deepcopy(self.round_functions[component_index//2].substitution.sboxes[sbox_index]))
                    childA_r.add_substitution_layer(substA)
                    childB_r.add_substitution_layer(substB)
                    
                else: # linear
                    if np.random.randint(0,2) == 0:
                        childA_r.add_linear_layer(self.round_functions[component_index//2].linear)
                        childB_r.add_linear_layer(member.round_functions[component_index//2].linear)
                    else:
                        childA_r.add_linear_layer(member.round_functions[component_index//2].linear)
                        childB_r.add_linear_layer(self.round_functions[component_index//2].linear)
                    childA.add_round_function(childA_r)
                    childB.add_round_function(childB_r)
        return childA,childB
    
    def print_member(self):
        print('num_rounds: %s' % (self.num_rounds))
        print('generation: %s' % (self.gen_index))
        for i in range(self.num_rounds-1):
            for j in range(16):
                print(self.round_functions[i].substitution.sboxes[j],end='')
                DDT = sbox_functions.get_ddt(self.round_functions[i].substitution.sboxes[j])
                DDT[0,0] = 0
                print(np.max(DDT),end='')
            for j in range(64):
                for k in range(64):
                    print(self.round_functions[i].linear.matrix[j][k],end='')
        for j in range(16):
            print(self.round_functions[self.num_rounds-1].substitution.sboxes[j],end='')
        print(self.round_functions[self.num_rounds-1].linear)

class Generation:
    def __init__(self,num_rounds,gen_index):
        self.num_rounds = num_rounds
        self.gen_index = gen_index
        self.num_member = 0
        self.members = []
        self.next_members = []
        self.fittest_population = []
        self.next_fittest_population = []
    
    def randomize(self,num):
        for _ in range(num):
            member = Member()
            member.randomize(self.num_rounds)
            member.gen_index = self.gen_index
            member.pop_index = self.num_member
            self.members.append(member)
            self.num_member += 1

    def add_member(self,member):
        member = deepcopy(member)
        member.gen_index = self.gen_index
        member.pop_index = self.num_member
        self.members.append(member)
        self.num_member += 1
        

    def select_fittest_population(self,num_fittest_population):
        self.next_fittest_population = sorted(self.fittest_population+self.members,key=lambda x: x.fitness, reverse=True)[:num_fittest_population]
        # adjust back
        for index in range(len(self.next_fittest_population)):
            self.next_fittest_population[index] = deepcopy(self.next_fittest_population[index])

    def select_breeding_population(self,num_breeding_population):
        population = sorted(self.fittest_population+self.members,key=lambda x: x.fitness, reverse=True)
        self.breeding_population = []
        while len(self.breeding_population) < num_breeding_population:
            self._normalized_fitness(population)
            self._compute_diversity(population)
            self._normalized_diversity(population)
            rank = [config.GENETIC_FUNCTIONS['FITNESS_TO_DIVERSITY_RATIO'][0] * pop.fitness**2 + \
			            config.GENETIC_FUNCTIONS['FITNESS_TO_DIVERSITY_RATIO'][1] * pop.diversity**2 \
			            for pop in population]
            max_index = np.argmax(rank)
            if population[max_index] in self.breeding_population: # if it is already inside
                pass
            else:
                self.breeding_population.append(population[max_index])
            del population[max_index]

    def _normalized_fitness(self,population):
        min_fitness = min([pop.fitness for pop in population])
        sum_fitness = sum([pop.fitness + min_fitness for pop in population])
        for pop in population: pop.fitness = (pop.fitness + min_fitness) / sum_fitness

    def _normalized_diversity(self,population):
        sum_diversity = sum([pop.diversity for pop in population])
        if sum_diversity == 0:
            for pop in population: pop.diversity = 1 / len(population)
        else:
            for pop in population: pop.diversity = pop.diversity / sum_diversity
    
    def _compute_diversity(self,population):
        for i,memberA in enumerate(population):
            memberA.diversity = 0
            for j,memberB in enumerate(self.breeding_population):
                if i == j: continue
                memberA.diversity += self._compute_distance(memberA,memberB)
        
    def _compute_distance(self,memberA,memberB):
        distance = 0
        for nr in range(self.num_rounds-1):
            distance += substitution_functions.compute_distance(memberA.round_functions[nr].substitution,memberB.round_functions[nr].substitution)
            distance += linear_functions.compute_distance(memberA.round_functions[nr].linear,memberB.round_functions[nr].linear)
        distance += substitution_functions.compute_distance(memberA.round_functions[self.num_rounds-1].substitution,memberB.round_functions[self.num_rounds-1].substitution)
        return distance

    @staticmethod
    def ismember(memberA,group):
        for memberB in group:
            if memberA.is_equal(memberB): return True
        return False

    def breeding(self):
        self.next_members = []
        while len(self.next_members) < config.HYPERPARAMETERS['POPULATION_SIZE']:
            # equal probabilities
            prob = [1 for _ in range(len(self.breeding_population))]
            probs = [p/sum(prob) for p in prob]
            parents = np.random.choice(self.breeding_population,2,replace=False,p=probs)
            child1,child2 = parents[0].breed(parents[1])
            if self.ismember(child1,self.next_members):
                child1.mutate(prob=1)
            self.next_members.append(child1) 
            if self.ismember(child2,self.next_members):
                child2.mutate(prob=1)
            self.next_members.append(child2)

        # just in case it exceeds the number of members, we cap it
        self.next_members = self.next_members[:config.HYPERPARAMETERS['POPULATION_SIZE']]

    def mutate(self):
        for member in self.members:
            member.mutate(prob=config.GENETIC_ALGO['MUTATION_PROB'])

    def compute_fitness(self, max_threads=1):
        tmp_members = []
        with ProcessPoolExecutor(max_workers=max_threads) as executor:
            futures = [executor.submit(utils.call_compute, member) for member in self.members]
            for future in futures:
                tmp_members.append(future.result())
        self.members = sorted(tmp_members,key=lambda member: member.pop_index)
    
    def print_result(self):
        for i in range(len(self.next_fittest_population)):
            print(self.next_fittest_population[i].pop_index)
            print(self.next_fittest_population[i].fitness)
            print(self.next_fittest_population[i].security_diff)
            print(self.next_fittest_population[i].security_linear)
            print(self.next_fittest_population[i].latency)
            print()

    def save(self,folder):
        file = os.path.join(folder,'gen_%s_%s.pkl' % (self.num_rounds,self.gen_index))
        utils.pickle_dump(file,self)
        members = sorted(self.fittest_population+self.members,key=lambda x: x.fitness, reverse=True)[:config.HYPERPARAMETERS['POPULATION_SIZE']]
        datas = {
            'num_rounds' : self.num_rounds,
            'gen_index' : self.gen_index,
            'num_members' : self.num_member
        }
        for i,member in enumerate(members):
            mem = {
                'num_rounds' : member.num_rounds,
                'gen_index' : member.gen_index,
                'pop_index' : member.pop_index,
                'differential' : member.security_diff,
                'linear' : member.security_linear,
                'latency' : member.latency,
                'fitness' : member.fitness,
                'identifier' : member.identifier,
            }
            datas[str(i)] = mem

        # save the meta-data
        meta_file = os.path.join(folder,'summary_%s_%s.json' % (self.num_rounds,self.gen_index))
        
        with open(meta_file, "w") as f:
            json.dump(datas, f, indent=4)  # `indent=4` makes it human-readable        

    def next_gen(self,max_threads=1):
        print('moving on to the next generation')
        print('current num rounds: %s, gen_index: %s' % (self.num_rounds,self.gen_index))

        # terminating condition
        if self.gen_index == config.HYPERPARAMETERS['MAX_GENERATION'][self.num_rounds] - 1 and self.num_rounds == config.HYPERPARAMETERS['MAX_NUM_ROUNDS']:
            self.members = sorted(self.fittest_population+self.members,key=lambda x: x.fitness, reverse=True)[:config.HYPERPARAMETERS['POPULATION_SIZE']]
            self.next_fittest_population = []
            self.fittest_population = []
            self.breeding_population = []
            self.next_members = []
            return 0
        # continue to the next generation
        elif self.gen_index < config.HYPERPARAMETERS['MAX_GENERATION'][self.num_rounds] - 1: 
            self.gen_index += 1
                
            # main members
            self.members = self.next_members
            self.next_members = []
            for index,member in enumerate(self.members):
                member.gen_index = self.gen_index
                member.pop_index = index
            self.fittest_population = self.next_fittest_population
            self.next_fittest_population = []
            self.breeding_population = []

        else: # add one more round
            self.num_rounds += 1
            self.members = sorted(self.fittest_population+self.members,key=lambda x: x.fitness, reverse=True)[:config.HYPERPARAMETERS['POPULATION_SIZE']]
            self.next_members = []
            self.next_fittest_population = []
            self.fittest_population = []
            self.breeding_population = []
            self.gen_index = 0
            
            members = deepcopy(self.members)

            choices = np.random.choice(list(config.GENETIC_ALGO['ADD_ONE_ROUND'].keys()),size=len(members),replace=True,
                                            p=list(config.GENETIC_ALGO['ADD_ONE_ROUND'].values()))

            tmp_members = []
            with ProcessPoolExecutor(max_workers=max_threads) as executor:
                futures_1 = [executor.submit(utils.call_steal_one_round, member, members) for index,member in enumerate(self.members) if choices[index] == 'STEAL']
                futures_2 = [executor.submit(utils.smart_randomize_one_round, member) for index,member in enumerate(self.members) if choices[index] == 'RANDOM']
                for future in futures_1:
                    tmp_members.append(future.result())
                for future in futures_2:
                    tmp_members.append(future.result())

            for i,member in enumerate(tmp_members):
                member.gen_index = self.gen_index
                member.pop_index = i

            self.members = tmp_members
            # check if prince is in
            for i, member in enumerate(self.members):
                if member.identifier == 'PRINCE':
                    print('Prince is still in the pool. Replacing with a higher number of rounds')
                    member.get_prince(self.num_rounds)
                    break

        print('next num rounds: %s, gen_index: %s' % (self.num_rounds,self.gen_index))
        return 1

    def bruteforce_expand_pop(self,num_expanded_pop):
        # adding one round 
        self.next_members = []

        for i in range(num_expanded_pop):
            member = deepcopy(self.members[i % self.num_member])
            member.smart_randomize_one_round()
            member.pop_index = i
            self.next_members.append(member)
        self.members = self.next_members
        self.num_member = num_expanded_pop
        self.next_members = []

    def bruteforce_reduce_pop(self,num_pop):
        self.members = sorted(self.members,key=lambda x: x.fitness, reverse=True)[:num_pop]
        self.num_member = num_pop