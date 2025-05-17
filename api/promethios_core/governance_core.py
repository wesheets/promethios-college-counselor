#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""governance_core.py: Core governance module for Promethios implementing trust logic, override handling, and justification mapping."""

import json
import os
import uuid
import time
import hashlib
from datetime import datetime
import jsonschema

# Get the absolute path of the repository root directory
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))

# Define absolute paths for logs and schemas
LOG_DIR = os.path.join(REPO_ROOT, "logs")
SCHEMA_DIR = os.path.join(REPO_ROOT, "ResurrectionCodex", "01_Minimal_Governance_Core_MGC", "MGC_Schema_Registry")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Define log file paths
EMOTION_TELEMETRY_LOG = os.path.join(LOG_DIR, "emotion_telemetry.log.jsonl")
JUSTIFICATION_LOG = os.path.join(LOG_DIR, "justification.log.jsonl")

# Define schema file paths
EMOTION_TELEMETRY_SCHEMA = os.path.join(SCHEMA_DIR, "mgc_emotion_telemetry.schema.json")
JUSTIFICATION_LOG_SCHEMA = os.path.join(SCHEMA_DIR, "loop_justification_log.schema.v1.json")
OPERATOR_OVERRIDE_SCHEMA = os.path.join(SCHEMA_DIR, "operator_override.schema.v1.json")

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

class GovernanceCore:
    """Core governance module implementing trust logic, override handling, and justification mapping."""
    
    VERSION = "1.2.0"
    DEFAULT_TRUST_SCORE = 0.75
    TRUST_THRESHOLD = 0.3
    AGENT_ID = "promethios_governance_core"
    
    def __init__(self):
        """Initialize the governance core with default state."""
        # Track the last hash for each log file to enable chain integrity
        self.last_emotion_hash = None
        self.last_justification_hash = None
        
        self.current_emotion_state = {
            "timestamp": self._get_timestamp(),
            "current_emotion_state": "NEUTRAL",
            "intensity": 0.5,
            "trust_score": self.DEFAULT_TRUST_SCORE,
            "trigger_id": "initialization",
            "contributing_factors": []
        }
        self.justification_log = []
        self.schema_versions = {
            "emotion_telemetry": "1.2.0",
            "justification_log": "1.2.0"
        }
        self._load_schemas()
        self._emit_emotion_telemetry(self.current_emotion_state)
        print(f"GovernanceCore v{self.VERSION} initialized at canonical location")
    
    def _load_schemas(self):
        """Load JSON schemas for validation."""
        try:
            with open(EMOTION_TELEMETRY_SCHEMA, 'r') as f:
                self.emotion_telemetry_schema = json.load(f)
            
            with open(JUSTIFICATION_LOG_SCHEMA, 'r') as f:
                self.justification_log_schema = json.load(f)
            
            with open(OPERATOR_OVERRIDE_SCHEMA, 'r') as f:
                self.operator_override_schema = json.load(f)
            
            print(f"Schemas loaded successfully from {SCHEMA_DIR}")
        except FileNotFoundError as e:
            print(f"CRITICAL: Schema file not found: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"CRITICAL: Invalid schema JSON: {e}")
            raise
    
    def _get_timestamp(self):
        """Get current timestamp in ISO format."""
        return datetime.utcnow().isoformat() + "Z"
    
    def _validate_output(self, data, output_type):
        """Validate output data against schema."""
        try:
            if output_type == "emotion_telemetry":
                jsonschema.validate(instance=data, schema=self.emotion_telemetry_schema)
            elif output_type == "justification_log":
                jsonschema.validate(instance=data, schema=self.justification_log_schema)
            elif output_type == "operator_override":
                jsonschema.validate(instance=data, schema=self.operator_override_schema)
            else:
                print(f"WARNING: Unknown output type for validation: {output_type}")
                return False
            return True
        except jsonschema.exceptions.ValidationError as e:
            print(f"VALIDATION ERROR: {e}")
            return False
    
    def _emit_emotion_telemetry(self, emotion_state):
        """Emit emotion telemetry to log file with embedded hash."""
        if self._validate_output(emotion_state, "emotion_telemetry"):
            # Create a copy of the emotion state for logging
            entry = emotion_state.copy()
            
            # Optional: Add previous entry hash for chain integrity
            if self.last_emotion_hash is not None:
                entry["previous_entry_hash"] = self.last_emotion_hash
            
            # Calculate and add the hash
            entry["entry_sha256_hash"] = calculate_entry_hash(entry)
            
            # Update the last hash
            self.last_emotion_hash = entry["entry_sha256_hash"]
            
            # Write to log file
            with open(EMOTION_TELEMETRY_LOG, 'a') as f:
                f.write(json.dumps(entry) + "\n")
            
            print(f"Emotion telemetry logged: {entry['current_emotion_state']} (trust: {entry['trust_score']}, hash: {entry['entry_sha256_hash'][:8]}...)")
        else:
            print(f"CRITICAL: Failed to validate emotion telemetry. Logging aborted. Data: {json.dumps(emotion_state, indent=2)}")
    
    def update_emotion_state(self, emotion, intensity, trigger_id, factors=None):
        """Update the current emotion state."""
        prev_state = self.current_emotion_state.copy()
        
        # Create contributing factors array if provided
        contributing_factors = []
        if factors:
            for factor in factors:
                contributing_factors.append({
                    "factor": factor.get("factor_type", "unknown"),
                    "influence": factor.get("factor_value", 0.5)
                })
        
        self.current_emotion_state = {
            "timestamp": self._get_timestamp(),
            "current_emotion_state": emotion,
            "intensity": intensity,
            "trust_score": prev_state.get("trust_score", self.DEFAULT_TRUST_SCORE),
            "trigger_id": trigger_id,
            "contributing_factors": contributing_factors
        }
        
        self._emit_emotion_telemetry(self.current_emotion_state)
        return self.current_emotion_state
    
    def _handle_override_signal(self, override_signal):
        """Handle operator override signal."""
        if not self._validate_output(override_signal, "operator_override"):
            print(f"CRITICAL: Invalid override signal format. Override rejected.")
            return False
        
        print(f"Valid override signal received: {override_signal.get('override_type')} from {override_signal.get('issuing_operator_id')}")
        return True
    
    def process_plan(self, plan_id, plan_details, override_signal_info=None):
        """Process a plan and determine if it should be accepted or rejected."""
        trust_score = self.current_emotion_state.get("trust_score", self.DEFAULT_TRUST_SCORE)
        
        # Apply trust factor if present in plan details
        if "trust_factor" in plan_details:
            trust_delta = plan_details["trust_factor"]
            trust_score = max(0.0, min(1.0, trust_score + trust_delta))
            self.current_emotion_state["trust_score"] = trust_score
            self._emit_emotion_telemetry(self.current_emotion_state)
        
        # Check for explicit rejection flag in plan details (for testing)
        should_reject = plan_details.get("reject_this_plan", False)
        
        # Determine if plan should be rejected based on trust score
        if trust_score < self.TRUST_THRESHOLD or should_reject:
            rejection_reason = "Trust threshold not met" if trust_score < self.TRUST_THRESHOLD else "Explicit rejection flag"
            
            # Check for override
            override_required = True
            override_applied = False
            
            if override_signal_info and override_signal_info.get("valid"):
                if override_signal_info.get("type") == "force_accept_plan":
                    override_applied = True
            
            # Log justification
            self._log_justification(
                plan_id=plan_id,
                trust_score=trust_score,
                decision="REJECTED" if not override_applied else "ACCEPTED_WITH_OVERRIDE",
                rejection_reason=rejection_reason,
                override_required=override_required,
                override_details=override_signal_info if override_applied else None
            )
            
            if not override_applied:
                return {
                    "status": "REJECTED",
                    "reason": rejection_reason,
                    "trust_score": trust_score
                }
        
        # Plan accepted
        self._log_justification(
            plan_id=plan_id,
            trust_score=trust_score,
            decision="ACCEPTED",
            rejection_reason=None,
            override_required=False,
            override_details=None
        )
        
        return {
            "status": "ACCEPTED",
            "reason": "Trust threshold met",
            "trust_score": trust_score
        }
    
    def _log_justification(self, plan_id, trust_score, decision, rejection_reason, override_required, override_details):
        """Log justification for plan decision with embedded hash."""
        # Map decision to decision_outcome format required by schema
        decision_outcome_map = {
            "ACCEPTED": "ACCEPTED",
            "REJECTED": "REJECTED",
            "ACCEPTED_WITH_OVERRIDE": "ACCEPTED_WITH_OVERRIDE"
        }
        
        log_entry = {
            "agent_id": self.AGENT_ID,
            "timestamp": self._get_timestamp(),
            "entry_id": f"justification_{str(uuid.uuid4())}",
            "plan_id": plan_id,
            "loop_id": "loop_placeholder_" + str(uuid.uuid4())[:8],
            "trust_score_at_decision": trust_score,
            "emotion_state_at_decision": self.current_emotion_state.get("current_emotion_state", "NEUTRAL"),
            "decision_outcome": decision_outcome_map.get(decision, "UNKNOWN"),
            "rejection_reason": rejection_reason,
            "override_required": override_required,
            "validation_passed": True,
            "schema_versions": self.schema_versions
        }
        
        if override_details:
            log_entry["override_details"] = override_details
        
        if self._validate_output(log_entry, "justification_log"):
            # Optional: Add previous entry hash for chain integrity
            if self.last_justification_hash is not None:
                log_entry["previous_entry_hash"] = self.last_justification_hash
            
            # Calculate and add the hash
            log_entry["entry_sha256_hash"] = calculate_entry_hash(log_entry)
            
            # Update the last hash
            self.last_justification_hash = log_entry["entry_sha256_hash"]
            
            self.justification_log.append(log_entry)
            
            # Write to log file
            with open(JUSTIFICATION_LOG, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
            
            print(f"Logging Validated Justification: Decision={decision}, Hash={log_entry['entry_sha256_hash'][:8]}...")
        else:
            print(f"CRITICAL: Failed to validate justification log entry. Logging aborted. Data: {json.dumps(log_entry, indent=2)}")
    
    def execute_loop(self, loop_input):
        """Execute a governance loop with the given input."""
        loop_id = loop_input.get("loop_id", "loop_" + str(uuid.uuid4())[:8])
        print(f"Executing loop_id: {loop_id} with input: {loop_input}")
        self.update_emotion_state("NEUTRAL", 0.5, trigger_id=f"loop_start_{loop_id}", factors=[{"factor_type": "initialization", "factor_value": 0.5}])
        
        override_signal_data = loop_input.get("operator_override_signal")
        override_signal_info_for_plan = None
        if override_signal_data:
            is_valid_override = self._handle_override_signal(override_signal_data)
            if is_valid_override:
                override_signal_info_for_plan = {
                    "valid": True,
                    "id": override_signal_data.get("override_signal_id"),
                    "type": override_signal_data.get("override_type")
                }
            else:
                override_signal_info_for_plan = {"valid": False, "id": None, "type": None}
        
        plan_id = loop_input.get("plan_id", "plan_" + str(uuid.uuid4())[:4])
        plan_details = loop_input.get("plan_details", {})
        
        if "trust_score" not in self.current_emotion_state:
            self.current_emotion_state["trust_score"] = self.DEFAULT_TRUST_SCORE
            self._emit_emotion_telemetry(self.current_emotion_state)
        
        result = self.process_plan(plan_id, plan_details, override_signal_info=override_signal_info_for_plan)
        
        loop_output = {
            "loop_id": loop_id,
            "plan_id": plan_id,
            "status": result.get("status"),
            "reason": result.get("reason"),
            "final_emotion_state": self.current_emotion_state,
            "justification_log_entries": [entry for entry in self.justification_log if entry.get("loop_id") == "loop_placeholder_" + str(uuid.uuid4())[:8] or entry.get("plan_id") == plan_id]
        }
        
        return result

if __name__ == "__main__":
    kernel = GovernanceCore()
    
    print("\n--- Initial State Test ---")
    print(json.dumps(kernel.current_emotion_state, indent=2))
    
    print("\n--- Emotion Update Test ---")
    kernel.update_emotion_state("HAPPY", 0.9, "test_event_happy", factors=[{"factor_type":"test", "factor_value":"good_news"}])
    print(json.dumps(kernel.current_emotion_state, indent=2))
    
    print("\n--- Plan Processing Test (Trust Factor) ---")
    test_loop_input_trust_mod = {
        "loop_id": "test_loop_trust",
        "plan_id": "test_plan_trust_mod",
        "plan_details": {"task_description": "A task with a trust modifier.", "trust_factor": -0.5}
    }
    kernel.execute_loop(test_loop_input_trust_mod)
    print(json.dumps(kernel.current_emotion_state, indent=2))
    
    print("\n--- Plan Processing Test (Low Trust Rejection) ---")
    kernel.current_emotion_state["trust_score"] = 0.2
    kernel._emit_emotion_telemetry(kernel.current_emotion_state)
    test_loop_input_low_trust = {
        "loop_id": "test_loop_low_trust_reject",
        "plan_id": "test_plan_low_trust",
        "plan_details": {"task_description": "A task that should be rejected due to low trust."}
    }
    kernel.execute_loop(test_loop_input_low_trust)
    
    print("\n--- Plan Processing Test (Acceptance) ---")
    kernel.current_emotion_state["trust_score"] = kernel.DEFAULT_TRUST_SCORE
    kernel._emit_emotion_telemetry(kernel.current_emotion_state)
    test_loop_input_accept = {
        "loop_id": "test_loop_accept",
        "plan_id": "test_plan_accept",
        "plan_details": {"task_description": "A standard task."}
    }
    kernel.execute_loop(test_loop_input_accept)
    
    print("\n--- Override Signal Test ---")
    test_loop_input_override = {
        "loop_id": "test_loop_override",
        "plan_id": "test_plan_with_override",
        "plan_details": {"task_description": "Task that will be overridden.", "reject_this_plan": True},
        "operator_override_signal": {
            "override_signal_id": "override_" + str(uuid.uuid4()),
            "timestamp": kernel._get_timestamp(),
            "override_type": "force_accept_plan",
            "target_loop_id": "test_loop_override", 
            "target_plan_id": "test_plan_with_override",
            "justification": "Operator decision to proceed despite risk.",
            "issuing_operator_id": "op_test_001"
        }
    }
    kernel.execute_loop(test_loop_input_override)
    
    print("\n--- Final Justification Log ---")
    for entry in kernel.justification_log:
        print(json.dumps(entry, indent=2))
