"""
Download and organize IBL (International Brain Lab) dataset
This provides access to 1000+ neurons from multiple brain regions

Author: Harel Joseph Wilner  
Date: November 2024

Note: This script provides instructions and example code.
Actual data download requires registration with IBL.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import json

def print_ibl_instructions():
    """
    Print detailed instructions for accessing IBL data.
    """
    print("\n" + "="*80)
    print("INTERNATIONAL BRAIN LAB (IBL) DATA ACCESS GUIDE")
    print("="*80 + "\n")
    
    print("The IBL provides the world's largest standardized dataset of neural recordings")
    print("from behaving mice, including Neuropixels recordings from multiple brain regions.")
    print()
    
    print("📊 DATASET OVERVIEW:")
    print("-" * 80)
    print("• 1000+ high-quality neurons")
    print("• 10+ brain regions (including V1, PFC, M1, CA1, Striatum)")
    print("• Standardized behavioral task (2AFC visual decision making)")
    print("• Trial-by-trial behavioral data")
    print("• Open access (after registration)")
    print()
    
    print("🔗 STEP-BY-STEP ACCESS:")
    print("-" * 80)
    print()
    print("STEP 1: Visit IBL Data Sharing Portal")
    print("  → https://data.internationalbrainlab.org")
    print("  → Click 'Request Access'")
    print("  → Fill out simple form (name, email, institution)")
    print("  → Approval usually within 24-48 hours")
    print()
    
    print("STEP 2: Install IBL Python packages")
    print("  Run in terminal:")
    print("  $ pip install ibllib ONE-api")
    print()
    
    print("STEP 3: Set up authentication")
    print("  Run in Python:")
    print("  >>> from one.api import ONE")
    print("  >>> one = ONE(base_url='https://openalyx.internationalbrainlab.org')")
    print("  >>> # Follow prompts to enter credentials")
    print()
    
    print("STEP 4: Download example session")
    print("  >>> # List available sessions")
    print("  >>> sessions = one.search(dataset='spikes.times')")
    print("  >>> print(f'Found {len(sessions)} sessions')")
    print("  >>> ")
    print("  >>> # Download first session")
    print("  >>> eid = sessions[0]")
    print("  >>> spikes = one.load_object(eid, 'spikes')")
    print("  >>> trials = one.load_object(eid, 'trials')")
    print()
    
    print("📚 DOCUMENTATION:")
    print("-" * 80)
    print("• Main docs: https://docs.internationalbrainlab.org")
    print("• Tutorials: https://int-brain-lab.github.io/iblenv/notebooks_external/")
    print("• Paper: https://www.nature.com/articles/s41586-020-03171-x")
    print()
    
    print("💡 RECOMMENDED DATASETS FOR PAPER 1:")
    print("-" * 80)
    print("1. 'Brain Wide Map' - recordings from all brain regions")
    print("2. 'Repeated Site' - high-quality recordings for consistency checks")
    print("3. Filter for sessions with >50 neurons and good behavior (>80% correct)")
    print()
    
    print("="*80)
    print()


def create_ibl_download_script():
    """
    Create a template script for IBL data download.
    """
    script_content = '''#!/usr/bin/env python3
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
    print(f"\\nDownloading session {i+1}/{n_sessions_to_download}: {eid}")
    
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

print(f"\\n{'='*60}")
print(f"DOWNLOAD SUMMARY")
print(f"{'='*60}")
print(f"Total neurons found: {len(neurons_df)}")
print(f"High-quality neurons: {len(neurons_filtered)}")
print(f"\\nBrain regions:")
print(neurons_filtered['brain_region'].value_counts())
print(f"\\nFiring rate statistics:")
print(neurons_filtered['mean_firing_rate'].describe())

# Save metadata
neurons_filtered.to_csv(output_dir / 'ibl_neurons_metadata.csv', index=False)
print(f"\\nMetadata saved to: {output_dir / 'ibl_neurons_metadata.csv'}")

print(f"\\nTo analyze these neurons, run:")
print(f"  python code/analyze_ibl_data.py")
'''
    
    # Save script
    script_path = Path('/home/user/paper1_upgrade/code/ibl_download_template.py')
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    print(f"✅ Template script created: {script_path}")
    print(f"   Customize this after obtaining IBL credentials")
    print()


def create_alternative_data_guide():
    """
    Provide alternatives if IBL access is delayed.
    """
    print("\n" + "="*80)
    print("ALTERNATIVE DATA SOURCES (while waiting for IBL access)")
    print("="*80 + "\n")
    
    print("1. ALLEN BRAIN OBSERVATORY (No registration required!)")
    print("-" * 80)
    print("   → https://observatory.brain-map.org")
    print("   → Visual cortex recordings (V1, LM, AL, PM, AM)")
    print("   → 2-photon calcium imaging + Neuropixels")
    print("   → Open access, download immediately")
    print("   → Installation: pip install allensdk")
    print()
    
    print("2. DANDI ARCHIVE (Open neuroscience data)")
    print("-" * 80)
    print("   → https://dandiarchive.org")
    print("   → Search: 'neuropixels', 'hippocampus', 'behavior'")
    print("   → Many datasets available immediately")
    print("   → Installation: pip install dandi")
    print()
    
    print("3. NEURODATA WITHOUT BORDERS (NWB)")
    print("-" * 80)
    print("   → https://www.nwb.org")
    print("   → Standardized format for many datasets")
    print("   → Includes behavioral data")
    print("   → Installation: pip install pynwb")
    print()
    
    print("4. EXPAND EXISTING BUZSAKI DATA")
    print("-" * 80)
    print("   → https://buzsakilab.com/wp/datasets/")
    print("   → Download additional sessions beyond the 5 you used")
    print("   → Same analysis pipeline")
    print("   → Could get to 100-150 neurons easily")
    print()
    
    print("💡 RECOMMENDATION: Start with Allen + DANDI while waiting for IBL")
    print("   This gets you 200-300 neurons from multiple regions in 1-2 weeks")
    print()
    print("="*80 + "\n")


def create_data_inventory():
    """
    Create a template for tracking dataset progress.
    """
    inventory = {
        "datasets": {
            "buzsaki_existing": {
                "status": "complete",
                "n_neurons": 25,
                "regions": ["hippocampus_CA1"],
                "species": "rat",
                "has_behavior": False,
                "notes": "Original Paper 1 data"
            },
            "ibl": {
                "status": "pending_access",
                "target_neurons": 500,
                "regions": ["V1", "PFC", "M1", "CA1", "striatum"],
                "species": "mouse",
                "has_behavior": True,
                "notes": "Waiting for data access approval"
            },
            "allen": {
                "status": "available",
                "target_neurons": 200,
                "regions": ["V1", "LM", "AL", "PM"],
                "species": "mouse",
                "has_behavior": True,
                "notes": "No registration required - start here!"
            },
            "dandi": {
                "status": "available",
                "target_neurons": 100,
                "regions": ["various"],
                "species": "mouse",
                "has_behavior": True,
                "notes": "Search for specific datasets"
            }
        },
        "milestones": {
            "week_1": "Request IBL access + Download Allen data",
            "week_2": "Analyze Allen data (200 neurons)",
            "week_3": "Download DANDI data (100 neurons)",
            "week_4": "Receive IBL access + download (500 neurons)",
            "week_6": "Complete analysis of 800+ neurons",
            "week_8": "Create figures + write manuscript"
        },
        "target_totals": {
            "neurons": 800,
            "regions": 5,
            "sessions": 50
        }
    }
    
    # Save inventory
    inventory_path = Path('/home/user/paper1_upgrade/data/data_inventory.json')
    inventory_path.parent.mkdir(exist_ok=True)
    
    with open(inventory_path, 'w') as f:
        json.dump(inventory, f, indent=2)
    
    print(f"✅ Data inventory created: {inventory_path}")
    print()


def main():
    """Main function."""
    print("\n" + "🚀 "*20)
    print("PAPER 1 UPGRADE: DATA ACQUISITION GUIDE")
    print("🚀 "*20 + "\n")
    
    # Print IBL instructions
    print_ibl_instructions()
    
    # Create download template
    create_ibl_download_script()
    
    # Alternative sources
    create_alternative_data_guide()
    
    # Create inventory
    create_data_inventory()
    
    print("\n" + "="*80)
    print("NEXT IMMEDIATE STEPS:")
    print("="*80)
    print()
    print("1. ✅ Request IBL data access (do this TODAY!)")
    print("     → https://data.internationalbrainlab.org")
    print()
    print("2. ✅ Install Allen SDK and download sample data (can do NOW)")
    print("     $ pip install allensdk")
    print("     $ python code/download_allen_data.py")
    print()
    print("3. ✅ While waiting for approvals, expand Buzsaki analysis")
    print("     → Download more sessions from buzsakilab.com")
    print("     → Could get to 100 neurons in current region")
    print()
    print("4. ⏰ Expected timeline:")
    print("     • Allen data: Today (no approval needed)")
    print("     • IBL approval: 1-2 days")
    print("     • Full dataset: 2-4 weeks")
    print()
    print("="*80)
    print()
    print("📧 Need help? I can assist with:")
    print("   • Writing data access request emails")
    print("   • Troubleshooting API issues")
    print("   • Optimizing download scripts")
    print("   • Anything else!")
    print()
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
