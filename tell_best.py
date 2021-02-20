#!/usr/bin/env python

import argparse, os, sys
import pandas as pd
import numpy as np

from copy import deepcopy

def get_fitness(arr, coeffs):
    return np.sum(arr * coeffs, axis=1)

def update_fitness(df, coeffs):
    columns = ['power', 'aero', 'grip', 'reliability', 'pit_stop_time']
    arr = df[columns].values
    df['fitness'] = get_fitness(arr, coeffs)
    return df

def tell_best(combo_filename, coeffs):
    df = pd.read_csv(combo_filename)
    df = update_fitness(df, np.array(coeffs))
    return df.loc[df['fitness'].idxmax()]

def optimize(combo_filename, optimize_file, use_wins, aggregate_tracks):
    perf_columns = ['power', 'aero', 'grip', 'reliability', 'pit_stop_time']
    group_columns = ['Brakes', 'Gearbox', 'Rear Wing', 'Front Wing', 'Suspension', 'Engine']
    df = pd.read_csv(combo_filename)
    rankings_df = pd.read_csv(optimize_file).dropna()
    print(len(rankings_df))
    avg = None
    if aggregate_tracks:
        track_groups = rankings_df.groupby(by=group_columns + ['Track']).mean()[['Win', 'Points']]
        avg = track_groups.groupby(by=group_columns).mean()
    else:
        avg = rankings_df.groupby(by=group_columns).mean()[['Win','Points']]

    learn_df = pd.DataFrame(columns=perf_columns + ['fitness'])
    for row in avg.iterrows():
        fitness = None
        if use_wins:
            fitness = row[1]['Win']
        else:
            fitness = row[1]['Points']
        #fitness = row[1]['Win'] * row[1]["Points"]
        lookup = df
        for i,c in enumerate(group_columns):
            lookup = lookup[lookup[c] == row[0][i]]
        item = lookup.iloc[0][perf_columns]
        item['fitness'] = fitness
        learn_df = learn_df.append(item)

    data = learn_df.values
    A = data[:,:-1]
    b = data[:,-1]
    x_hat = np.linalg.lstsq(A,b, rcond=None)[0]
    print("Coeffs: {}".format(x_hat))

    return x_hat

def main():

    data_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
    combinations_file_default_path = os.path.join(data_dir, 'combinations.csv')

    parser = argparse.ArgumentParser()
    parser.add_argument('combo_file', type=str, default=combinations_file_default_path, help='CSV with all possible combinations')
    parser.add_argument('--coeffs', '-c', nargs=5, type=float, default=[1.0, 1.0, 1.0, 1.0, -1.0], help='Coeffs from [power, aero, grip, reliability, pit_stop_time]')
    parser.add_argument('--optimize', '-p', type=str, help='File to optimize against')
    parser.add_argument('--use-wins', '-w', action='store_true', help='Use wins instead of points')
    parser.add_argument('--aggregate-tracks', action='store_true', help='Aggregates means of fitness by tracks')
    args = parser.parse_args()

    coeffs = args.coeffs
    if args.optimize is not None:
        coeffs = optimize(args.combo_file, args.optimize, args.use_wins, args.aggregate_tracks)
    print(tell_best(args.combo_file, coeffs))


if __name__ == '__main__':
    main()