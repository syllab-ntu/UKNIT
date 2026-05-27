"""
This file contains some of the generic utility functions 
"""
import config
import pickle
import os
import shutil
import threading

def create_necessary_folders(folder):
    for string in [config.FILE_PATHS['ESPRESSO_DIFF_TEMP_FOLDER'],
                   config.FILE_PATHS['ESPRESSO_DIFF_SAVED_FOLDER'],
                   config.FILE_PATHS['ESPRESSO_LINEAR_TEMP_FOLDER'],
                   config.FILE_PATHS['ESPRESSO_LINEAR_SAVED_FOLDER'],
                   config.FILE_PATHS['VERILOG_FOLDER'],
                   config.FILE_PATHS['SAT_DIFF_FOLDER'],
                   config.FILE_PATHS['SAT_LINEAR_FOLDER']]:
        os.makedirs(string, exist_ok = True)

def pickle_load(file):
    with open(file, "rb") as f:
        member = pickle.load(f)
    return member


def pickle_dump(file,member):
    with open(file, "wb") as f:
        pickle.dump(member, f)

def write_to_file(file,statements):
    with open(file,'w') as f:
        for i in range(len(statements)-1):
            print(statements[i],file=f)
        print(statements[-1],file=f,end='')

def call_compute(member):
    # doing this because ProcessPoolExecutor *copies* the object :/ 
    member.compute_fitness()
    return member

def call_steal_one_round(member,members):
    member.steal_one_round(members)
    return member

def smart_randomize_one_round(member):
    member.smart_randomize_one_round()
    return member

def optimize_save():
    # return
    # copying all the espresso 
    src_folder = 'main_tmp/espresso_diff_tmp'
    dst_folder = 'main_tmp/espresso_diff'
    for filename in os.listdir(src_folder):
        if 'output' in filename:
            src_path = os.path.join(src_folder, filename)
            new_filename = '_'.join(filename.split('_')[:-1]) + '.txt'
            dst_path = os.path.join(dst_folder, new_filename)
            if os.path.isfile(src_path): shutil.move(src_path, dst_path)
    
    src_folder = 'main_tmp/espresso_linear_tmp'
    dst_folder = 'main_tmp/espresso_linear'
    for filename in os.listdir(src_folder):
        if 'output' in filename:
            src_path = os.path.join(src_folder, filename)
            new_filename = '_'.join(filename.split('_')[:-1]) + '.txt'
            dst_path = os.path.join(dst_folder, new_filename)
            if os.path.isfile(src_path): shutil.move(src_path, dst_path)
    
    
