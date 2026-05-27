'''
This file is the main file!
Run this!

'''
from cipher.Ciphers import *

from config import *
import utils
from datetime import datetime
import os


from seed_config import SEED, set_global_seed
set_global_seed(SEED)

def run(init=True,generation=None):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = f"./runs/RUN_{timestamp}/"
    os.makedirs(folder)
    utils.create_necessary_folders(folder)

    os.system('cp config.py %s' % (folder))
    file = f"{folder}seed.txt"
    with open(file,'w') as f:
        print(f"Global seed set to: {SEED}",file=f)

    num_pop = HYPERPARAMETERS['POPULATION_SIZE']
    num_threads = HYPERPARAMETERS['NUM_OF_THREADS']
    num_fittest = GENETIC_ALGO['NUM_FIT_CIPHERS']
    num_breeding = GENETIC_ALGO['BREEDING_POPULATION_PROPORTION'] * num_pop
    # openlane_containers.create_openlane_containers(num_threads)
    # print('openlane containers are successfully created!')
    if init:
        # intialization
        current_gen = 0
        generation = Generation(INIT_SETTINGS['INIT_NUM_ROUNDS'],current_gen)
        generation.randomize(num_pop)
        if INIT_SETTINGS['INCLUDE_PRINCE']:
            generation.members[0].identifier = 'PRINCE'
            generation.members[0].get_prince(INIT_SETTINGS['INIT_NUM_ROUNDS'])
            # print(generation.members[0].round_functions)
        
        if INIT_SETTINGS['INCLUDE_UKNIT']:
            for i,window in enumerate(range(0,9)):
                generation.members[i+1].identifier = 'UKNIT_%s' % (window)
                generation.members[i+1].get_uknitbc(INIT_SETTINGS['INIT_NUM_ROUNDS'],window=window)


    while generation != None:
        # compute fitness for each of the cipher
        generation.compute_fitness(num_threads)
        generation.print_result()
        # saving the results from espresso to be reused  
        utils.optimize_save()
        generation.save(folder)
        generation.select_fittest_population(num_fittest)
        generation.select_breeding_population(num_breeding)
        generation.breeding()
        # move to next 
        if not generation.next_gen(num_threads): break

def run_bruteforce():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    folder = f"./runs/RUN_{timestamp}/"
    os.makedirs(folder)
    utils.create_necessary_folders(folder)
    os.system('cp config.py %s' % (folder))
    file = f"{folder}seed.txt"
    with open(file,'w') as f:
        print(f"Global seed set to: {SEED}",file=f)

    num_pop = HYPERPARAMETERS['POPULATION_SIZE']
    num_threads = HYPERPARAMETERS['NUM_OF_THREADS']
    num_expanded_pop = BRUTEFORCE['EXPANDED_POPULATION_SIZE']
    # openlane_containers.create_openlane_containers(num_threads)
    
    # intialization
    current_gen = 0
    generation = Generation(INIT_SETTINGS['INIT_NUM_ROUNDS'],current_gen)
    generation.randomize(num_pop)

    while True:
        generation.bruteforce_expand_pop(num_expanded_pop)
        generation.compute_fitness(num_threads)
        generation.print_result()
        generation.bruteforce_reduce_pop(num_pop)
        utils.optimize_save()
        generation.save(folder)
        if generation.num_rounds == 12: break
    # cleaning
    # openlane_containers.delete_containers()




def start_from(file):
    print('start with file %s' % file)
    generation = read(file)
    run(init=False,generation=generation)


def read(file):
    generation = utils.pickle_load(file)
    # print(generation.members[0].security_diff)
    # print(generation.members[0].security_linear)
    # print(generation.members[0].latency)
    return generation


if __name__ == '__main__':
    # file = './runs/RUN_2025-09-25_09-33-23/gen_5_99.pkl'
    # file = './gen_5_99.pkl'
    # start_from(file)
    # run_bruteforce()
    run()
