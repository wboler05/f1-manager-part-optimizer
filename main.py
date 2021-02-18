#!/usr/bin/env python

import argparse, os, sys
import pandas as pd
import numpy as np
import tqdm
from copy import deepcopy

import matplotlib.pyplot as plt

def extrapolate(graph_dict):
    if len(graph_dict) > 1:
        graph_dict_cp = deepcopy(graph_dict)
        first_key = list(graph_dict_cp.keys())[0]
        del graph_dict_cp[first_key]
        key_list = graph_dict[first_key]
        r_list = extrapolate(graph_dict_cp)
        final_list = list()
        for r in r_list:
            for v in key_list:
                z = deepcopy(r)
                z[first_key] = v
                final_list.append(z)
        return final_list
    else:
        first_key = list(graph_dict.keys())[0]
        key_list = graph_dict[first_key]
        final_list = list()
        for v in key_list:
            final_list.append({
                first_key:v,
            })
        return final_list

def generate_combinations(master_equipment_df):
    df = master_equipment_df
    type_dict = dict()
    types = set(df['type'])
    for t in types:
        type_dict[t] = set(df[df['type'] == t]['name'])
    print(df.columns)
    
    print(type_dict)
    print("Building combos")
    combos = extrapolate(type_dict)
    print(len(combos))

    sorted_types = sorted(list(types))

    combo_performances = list()
    df_filler = list()
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
            val_df = df[np.logical_and(df['type'] == t, df['name'] == name)]
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
    parser = argparse.ArgumentParser()
    parser.add_argument('master_equipment_file', help='CSV')
    parser.add_argument('--output-filename', '-o', default='combinations.csv', help='Output CSV')
    args = parser.parse_args()

    assert(os.path.exists(args.master_equipment_file))
    assert(os.path.isfile(args.master_equipment_file))
    df = pd.read_csv(args.master_equipment_file)
    combinations_df = generate_combinations(df)
    combinations_df.to_csv(args.output_filename, index=False)

if __name__ == '__main__':
    main()