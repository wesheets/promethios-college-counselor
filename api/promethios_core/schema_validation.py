#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_schema.py: Validate log entries against their schemas."""

import json
import jsonschema
import os
import sys

# Get the absolute path of the repository root directory
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Define paths for schemas and logs
SCHEMA_DIR = os.path.join(REPO_ROOT, "ResurrectionCodex", "01_Minimal_Governance_Core_MGC", "MGC_Schema_Registry")
LOG_DIR = os.path.join(REPO_ROOT, "logs")

# Define schema file paths
EMOTION_TELEMETRY_SCHEMA = os.path.join(SCHEMA_DIR, "mgc_emotion_telemetry.schema.json")
JUSTIFICATION_LOG_SCHEMA = os.path.join(SCHEMA_DIR, "loop_justification_log.schema.v1.json")

# Define log file paths
EMOTION_TELEMETRY_LOG = os.path.join(LOG_DIR, "emotion_telemetry.log.jsonl")
JUSTIFICATION_LOG = os.path.join(LOG_DIR, "justification.log.jsonl")

def validate_log_file(log_file_path, schema_file_path, log_type):
    """Validate all entries in a log file against its schema.
    
    Args:
        log_file_path: Path to the log file
        schema_file_path: Path to the schema file
        log_type: Type of log for reporting purposes
        
    Returns:
        Boolean indicating if all entries passed validation
    """
    print(f"Validating {log_type} log entries against schema...")
    
    try:
        # Load schema
        with open(schema_file_path, 'r') as f:
            schema = json.load(f)
        
        # Load log entries
        with open(log_file_path, 'r') as f:
            entries = [json.loads(line) for line in f]
        
        # Validate each entry
        all_valid = True
        for i, entry in enumerate(entries):
            try:
                jsonschema.validate(instance=entry, schema=schema)
                print(f"  Entry {i+1}: PASSED")
            except jsonschema.exceptions.ValidationError as e:
                print(f"  Entry {i+1}: FAILED - {e}")
                all_valid = False
        
        if all_valid:
            print(f"All {log_type} log entries passed schema validation")
        else:
            print(f"Some {log_type} log entries failed schema validation")
        
        return all_valid
    
    except Exception as e:
        print(f"Error during {log_type} schema validation: {e}")
        return False

def main():
    """Main function to validate all log files."""
    # Validate emotion telemetry log
    emotion_valid = validate_log_file(
        EMOTION_TELEMETRY_LOG,
        EMOTION_TELEMETRY_SCHEMA,
        "emotion telemetry"
    )
    
    # Validate justification log
    justification_valid = validate_log_file(
        JUSTIFICATION_LOG,
        JUSTIFICATION_LOG_SCHEMA,
        "justification"
    )
    
    # Overall result
    print("\n--- Schema Validation Summary ---")
    print(f"Emotion Telemetry Log: {'PASSED' if emotion_valid else 'FAILED'}")
    print(f"Justification Log: {'PASSED' if justification_valid else 'FAILED'}")
    
    if emotion_valid and justification_valid:
        print("\nOVERALL: All logs conform to required schemas")
        return 0
    else:
        print("\nOVERALL: Some logs failed schema validation")
        return 1

if __name__ == "__main__":
    sys.exit(main())
