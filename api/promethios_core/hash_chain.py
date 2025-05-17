#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_log_hashes.py: Utility to verify SHA256 hashes in Promethios log files."""

import json
import hashlib
import argparse
import os
import sys
import datetime

# Get the absolute path of the repository root directory
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(REPO_ROOT, "logs")

def calculate_entry_hash(entry_dict):
    """Calculate SHA256 hash for a log entry.
    
    Args:
        entry_dict: Dictionary containing the log entry data (without hash field)
        
    Returns:
        String containing the hex digest of the SHA256 hash
    """
    # Create a copy of the entry to avoid modifying the original
    entry_copy = entry_dict.copy()
    
    # Remove the hash field if it exists
    if 'entry_sha256_hash' in entry_copy:
        del entry_copy['entry_sha256_hash']
        
    # Sort keys for deterministic serialization
    entry_json = json.dumps(entry_copy, sort_keys=True)
    
    # Calculate hash
    return hashlib.sha256(entry_json.encode('utf-8')).hexdigest()

def verify_log_file(log_file):
    """Verify the integrity of a log file by checking embedded hashes.
    
    Args:
        log_file: Path to the log file
        
    Returns:
        Tuple of (success, manifest_entries)
        - success: Boolean indicating if all entries passed verification
        - manifest_entries: List of (line_number, hash) tuples for the manifest
    """
    print(f"Verifying {os.path.basename(log_file)}...", end=" ")
    
    success = True
    manifest_entries = []
    previous_hash = None
    
    with open(log_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                entry = json.loads(line.strip())
                
                # Check if entry has a hash
                if 'entry_sha256_hash' not in entry:
                    print(f"FAILED\nEntry at line {line_num} is missing entry_sha256_hash")
                    success = False
                    continue
                
                # Get the stored hash
                stored_hash = entry['entry_sha256_hash']
                
                # Calculate the expected hash
                expected_hash = calculate_entry_hash(entry)
                
                # Compare hashes
                if stored_hash != expected_hash:
                    print(f"FAILED\nHash mismatch at line {line_num}")
                    print(f"  Stored:   {stored_hash}")
                    print(f"  Expected: {expected_hash}")
                    success = False
                
                # Optional: Check chain integrity if previous_entry_hash is present
                if previous_hash is not None and 'previous_entry_hash' in entry:
                    if entry['previous_entry_hash'] != previous_hash:
                        print(f"FAILED\nChain integrity broken at line {line_num}")
                        print(f"  Stored previous hash:   {entry['previous_entry_hash']}")
                        print(f"  Expected previous hash: {previous_hash}")
                        success = False
                
                # Update previous hash for next iteration
                previous_hash = stored_hash
                
                # Add to manifest
                manifest_entries.append((line_num, stored_hash))
                
            except json.JSONDecodeError:
                print(f"FAILED\nInvalid JSON at line {line_num}")
                success = False
    
    if success:
        print("PASSED")
    
    return success, manifest_entries

def generate_manifest(manifest_entries, log_files):
    """Generate a manifest file containing all verified hashes.
    
    Args:
        manifest_entries: Dictionary mapping log files to lists of (line_num, hash) tuples
        log_files: List of log files that were verified
    """
    manifest_path = os.path.join(LOG_DIR, "sha256_manifest.txt")
    
    with open(manifest_path, 'w') as f:
        f.write("# SHA256 Manifest\n")
        f.write(f"# Generated: {datetime.datetime.now().isoformat()}\n\n")
        
        for log_file in log_files:
            basename = os.path.basename(log_file)
            f.write(f"## {basename}\n")
            
            for line_num, hash_value in manifest_entries[log_file]:
                f.write(f"{line_num}: {hash_value}\n")
            
            f.write("\n")
    
    print(f"SHA256 manifest generated: {manifest_path}")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Verify SHA256 hashes in Promethios log files and generate manifest.")
    parser.add_argument("--generate", action="store_true", help="Generate SHA256 manifest for all log files")
    
    args = parser.parse_args()
    
    # Ensure log directory exists
    if not os.path.exists(LOG_DIR):
        print(f"Error: Log directory {LOG_DIR} does not exist")
        return 1
    
    # Define log files to verify
    log_files = [
        os.path.join(LOG_DIR, "emotion_telemetry.log.jsonl"),
        os.path.join(LOG_DIR, "justification.log.jsonl")
    ]
    
    # Verify each log file
    all_success = True
    manifest_entries = {}
    
    for log_file in log_files:
        if not os.path.exists(log_file):
            print(f"Warning: Log file {log_file} does not exist, skipping")
            continue
        
        success, entries = verify_log_file(log_file)
        manifest_entries[log_file] = entries
        all_success = all_success and success
    
    # Generate manifest if requested and all verifications passed
    if args.generate and all_success:
        generate_manifest(manifest_entries, [f for f in log_files if os.path.exists(f)])
        print("All logs passed integrity verification")
    elif args.generate and not all_success:
        print("Some logs failed integrity verification, manifest not generated")
        return 1
    
    if all_success:
        print("All logs passed integrity verification")
        return 0
    else:
        print("Some logs failed integrity verification")
        return 1

if __name__ == "__main__":
    sys.exit(main())
