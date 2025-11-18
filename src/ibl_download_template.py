#!/usr/bin/env python3
"""
Template script for downloading IBL data
Customize this after getting IBL access credentials
"""

from one.api import ONE
import numpy as np
import pandas as pd
from pathlib import Path

# Initialize ONE (will prompt for credentials first time)
one = ONE(base_url='https://openalyx.internationalbrainlab.org')

# Define output directory
output_dir = Path('/home/user/paper1_upgrade/data/ibl')
output_dir.mkdir(parents=True, exist_ok=True)

print("Searching for high-quality sessions...")

# Search for sessions with:
# - Neuropixels recordings (spikes.times)
# - Behavioral data (trials)
# - Good performance
sessions = one.search(
    dataset=['spikes.times', 'spikes.clusters', 'trials.choice'],
    task_protocol='_iblrig_tasks_ephysChoiceWorld'
)

print(f"Found {len(sessions)} candidate sessions")

# Download first 10 sessions as a test
n_sessions_to_download = 10

all_neurons = []

for i, eid in enumerate(sessions[:n_sessions_to_download]):
    print(f"\nDownloading session {i+1}/{n_sessions_to_download}: {eid}")
    
    try:
        # Load spike data
        spikes = one.load_object(eid, 'spikes')
        clusters = one.load_object(eid, 'clusters')
        trials = one.load_object(eid, 'trials')
        
        # Get session info
        session_info = one.get_details(eid)
        
        # Extract neuron information
        for cluster_id in range(len(clusters['depths'])):
            neuron_info = {
                'session_id': eid,
                'cluster_id': cluster_id,
                'depth': clusters['depths'][cluster_id],
                'brain_region': clusters.get('brainLocation', ['Unknown'])[cluster_id] 
                               if hasattr(clusters.get('brainLocation', []), '__getitem__') 
                               else 'Unknown',
                'n_spikes': np.sum(spikes['clusters'] == cluster_id),
                'recording_duration': trials['intervals'][-1][-1] if len(trials['intervals']) > 0 else 0,
            }
            
            # Calculate firing rate
            if neuron_info['recording_duration'] > 0:
                neuron_info['mean_firing_rate'] = neuron_info['n_spikes'] / neuron_info['recording_duration']
            else:
                neuron_info['mean_firing_rate'] = 0
            
            all_neurons.append(neuron_info)
        
        print(f"  Extracted {len(clusters['depths'])} neurons")
        
    except Exception as e:
        print(f"  Error loading session: {e}")
        continue

# Create summary dataframe
neurons_df = pd.DataFrame(all_neurons)

# Filter for high-quality neurons
neurons_filtered = neurons_df[
    (neurons_df['mean_firing_rate'] > 1.0) &  # >1 Hz
    (neurons_df['mean_firing_rate'] < 50.0) &  # <50 Hz (exclude artifacts)
    (neurons_df['n_spikes'] > 5000)  # >5000 spikes
]

print(f"\n{'='*60}")
print(f"DOWNLOAD SUMMARY")
print(f"{'='*60}")
print(f"Total neurons found: {len(neurons_df)}")
print(f"High-quality neurons: {len(neurons_filtered)}")
print(f"\nBrain regions:")
print(neurons_filtered['brain_region'].value_counts())
print(f"\nFiring rate statistics:")
print(neurons_filtered['mean_firing_rate'].describe())

# Save metadata
neurons_filtered.to_csv(output_dir / 'ibl_neurons_metadata.csv', index=False)
print(f"\nMetadata saved to: {output_dir / 'ibl_neurons_metadata.csv'}")

print(f"\nTo analyze these neurons, run:")
print(f"  python code/analyze_ibl_data.py")
