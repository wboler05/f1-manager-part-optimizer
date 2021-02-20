#!/usr/bin/env python

import argparse, os, sys
import pandas as pd
import numpy as np
import tqdm
from copy import deepcopy

import matplotlib.pyplot as plt

def fold_in_combos(graph_dict):
    '''
    Given a dict of equipment types and names, enumerate all combinations

    We are looking for sets of the following:
    {brakes}{gearbox}{rear wing}{front wing}{suspension}{engine}
    This produces a table of all protential combinations of these types

    @param dict : k=type, v=list of names
    @return list(dict) : list of dict of value combo, accessed by type
        i.e.: 
            ret_val[0] = {'Engine': 'Passion', 'Suspension': 'Bungee', ... , 'Gearbox': 'MSM' }
    '''
    # Instantiate return value
    final_list = list()
    # Pop first entry
    first_key = list(graph_dict.keys())[0]
    key_list = graph_dict[first_key]
    if len(graph_dict) > 1:
        # Build next list from remaining keys
        r_list = fold_in_combos({k:v for k,v in graph_dict.items() if k != first_key})
        # Combine all combinations
        for r in r_list:
            for v in key_list:
                z = deepcopy(r)
                z[first_key] = v
                final_list.append(z)
    else:
        # If entry size is 1, build nth layer
        for v in key_list:
            final_list.append({
                first_key:v,
            })
    # Return combinations
    return final_list


def generate_combinations(master_equipment_df):
    type_dict = dict()
    types = set(master_equipment_df['type'])
    for t in types:
        type_dict[t] = set(master_equipment_df[master_equipment_df['type'] == t]['name'])
    print(master_equipment_df.columns)
    
    print(type_dict)
    print("Building combos")
    combos = fold_in_combos(type_dict)
    print(len(combos))

    sorted_types = sorted(list(types))

    combo_performances = list()
    df_filler = list()
    # TODO I'm doing something stupid here that I'll fix later
    for i,c_dict in tqdm.tqdm(enumerate(combos), total=len(combos)):
        assignment_dict = dict()
        total_dict = {
            'power': 0.,
            'aero': 0.,
            'grip': 0.,
            'reliability': 0.,
            'pit_stop_time': 0.,
        }
        for t,name in c_dict.items():
            val_df = master_equipment_df[np.logical_and(
                master_equipment_df['type'] == t, 
                master_equipment_df['name'] == name
            )]
            assignment_dict[t] = {
                'name':name,
                'power':val_df['power'].iat[0],
                'aero':val_df['aero'].iat[0],
                'grip':val_df['grip'].iat[0],
                'reliability':val_df['reliability'].iat[0],
                'pit_stop_time':val_df['pit_stop_time'].iat[0],
            }
            total_dict['power'] += assignment_dict[t]['power']
            total_dict['aero'] += assignment_dict[t]['aero']
            total_dict['grip'] += assignment_dict[t]['grip']
            total_dict['reliability'] += assignment_dict[t]['reliability']
            total_dict['pit_stop_time'] += assignment_dict[t]['pit_stop_time']
        assignment_dict['total'] = total_dict
        combo_performances.append(assignment_dict)

        df_filler.append({
            **{t:assignment_dict[t]['name'] for t in sorted_types },
            **{t:assignment_dict['total'][t] for t in ['power', 'aero', 'grip', 'reliability', 'pit_stop_time']}
        })

    combo_df = pd.DataFrame(df_filler, columns=list(sorted_types) + [
        'power', 'aero', 'grip', 'reliability', 'pit_stop_time',
    ])
    print(combo_df)
    return combo_df



def main():

    data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
    combinations_file_default_path = os.path.join(data_dir, 'combinations.csv')

    parser = argparse.ArgumentParser()
    parser.add_argument('master_equipment_file', help='CSV with full list of available equipement')
    parser.add_argument('--output-filename', '-o', default=combinations_file_default_path, help='Output CSV of combinations')
    args = parser.parse_args()

    assert(os.path.exists(args.master_equipment_file))
    assert(os.path.isfile(args.master_equipment_file))
    df = pd.read_csv(args.master_equipment_file)
    combinations_df = generate_combinations(df)
    combinations_df.to_csv(args.output_filename, index=False)

if __name__ == '__main__':
    main()