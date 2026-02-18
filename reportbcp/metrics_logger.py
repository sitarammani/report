#!/usr/bin/env python3
"""
Performance and Stability Metrics Logging
Tracks: categorization latency, conflicts, hash stability, LLM performance
"""

import logging
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import hashlib
import time
import psutil

class MetricsLogger:
    """Centralized metrics logging with performance tracking"""
    
    def __init__(self, log_dir: str = None):
        """Initialize metrics logger"""
        
        # Set up log directory
        if log_dir is None:
            home = Path.home()
            log_dir = home / '.config' / 'SpendingApp' / 'logs'
        else:
            log_dir = Path(log_dir)
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up main application log
        self.setup_logger()
        
        # Metrics storage
        self.categorization_times = []
        self.conflicts = []
        self.llm_inferences = []
        self.hash_values = {}
        
    def setup_logger(self):
        """Configure logging with both file and console output"""
        
        log_file = self.log_dir / f"spending_app_{datetime.now().strftime('%Y%m%d')}.log"
        
        self.logger = logging.getLogger('SpendingApp')
        self.logger.setLevel(logging.DEBUG)
        
        # File handler - detailed logs
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler - user-friendly output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Log to file only (start.py shows the startup message)
        self.logger.debug("═" * 70)
        self.logger.debug("Application session started")
        self.logger.debug("═" * 70)
    
    def log_categorization_start(self, transaction_count: int):
        """Log start of categorization process"""
        self.logger.debug(f"\n📊 CATEGORIZATION PROCESS START")
        self.logger.debug(f"   Transactions to process: {transaction_count}")
        self.categorization_start_time = time.time()
        self.transaction_count = transaction_count
        self.conflicts_this_batch = 0
    
    def log_categorization_result(self, vendor: str, category: str, 
                                 matching_rules: int, notes: str = ""):
        """Log individual transaction categorization"""
        
        conflict = "CONFLICT" if matching_rules > 1 else "OK"
        
        if matching_rules > 1:
            self.conflicts_this_batch += 1
            self.logger.debug(
                f"   TX: {vendor:30} → {category:25} "
                f"[{matching_rules} rules matched] {conflict}"
            )
        else:
            self.logger.debug(
                f"   TX: {vendor:30} → {category:25} ✓"
            )
    
    def log_categorization_complete(self):
        """Log completion of categorization process"""
        
        latency = time.time() - self.categorization_start_time
        per_transaction = latency / self.transaction_count if self.transaction_count > 0 else 0
        
        self.categorization_times.append({
            'timestamp': datetime.now().isoformat(),
            'total_time_seconds': latency,
            'transaction_count': self.transaction_count,
            'time_per_transaction_ms': per_transaction * 1000,
            'conflict_count': self.conflicts_this_batch,
            'conflict_rate_percent': (self.conflicts_this_batch / self.transaction_count * 100) 
                                     if self.transaction_count > 0 else 0
        })
        
        self.logger.debug(f"\n✅ CATEGORIZATION COMPLETE")
        self.logger.debug(f"   Total time: {latency:.2f} seconds")
        self.logger.debug(f"   Per transaction: {per_transaction*1000:.2f} ms")
        self.logger.debug(f"   Conflicts detected: {self.conflicts_this_batch}")
        self.logger.debug(f"   Conflict rate: {self.conflicts_this_batch/self.transaction_count*100:.1f}%")
    
    def log_hash_stability_check(self, vendor: str, category: str, 
                                rule_id: str, priority: int):
        """Track deterministic hash for categorization stability"""
        
        # Create stable hash of categorization decision
        hash_input = f"{vendor}|{category}|{rule_id}|{priority}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        
        key = vendor.upper()
        
        if key in self.hash_values:
            if self.hash_values[key] != hash_value:
                self.logger.warning(
                    f"⚠️  HASH INSTABILITY DETECTED: {vendor} "
                    f"({self.hash_values[key][:8]} → {hash_value[:8]})"
                )
            else:
                self.logger.debug(f"✓ Hash stable: {vendor} (consistency verified)")
        else:
            self.hash_values[key] = hash_value
            self.logger.debug(f"📌 Hash recorded: {vendor} ({hash_value[:8]})")
    
    def log_llm_query_start(self, question: str):
        """Log start of LLM inference"""
        
        self.logger.debug(f"\n🤖 LLM QUERY START")
        self.logger.debug(f"   Question: {question}")
        self.logger.debug(f"   Model: Mistral")
        
        # Get current process memory
        process = psutil.Process(os.getpid())
        self.memory_before = process.memory_info().rss / 1024 / 1024  # MB
        self.logger.debug(f"   Memory before: {self.memory_before:.1f} MB")
        
        self.llm_start_time = time.time()
        self.llm_current_question = question  # Store question for later
    
    def log_llm_inference_complete(self, response: str, tokens_generated: int = None):
        """Log completion of LLM inference"""
        
        inference_time = time.time() - self.llm_start_time
        
        # Get current process memory
        process = psutil.Process(os.getpid())
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - self.memory_before
        
        self.llm_inferences.append({
            'timestamp': datetime.now().isoformat(),
            'question': getattr(self, 'llm_current_question', 'unknown'),
            'response': response,
            'inference_time_seconds': inference_time,
            'response_length': len(response),
            'memory_used_mb': memory_used,
            'memory_peak_mb': memory_after,
            'tokens_generated': tokens_generated
        })
        
        self.logger.debug(f"\n✅ LLM INFERENCE COMPLETE")
        self.logger.debug(f"   Inference time: {inference_time:.2f} seconds")
        self.logger.debug(f"   Response length: {len(response)} characters")
        self.logger.debug(f"   Memory used: {memory_used:.1f} MB")
        self.logger.debug(f"   Memory peak: {memory_after:.1f} MB")
        
        if tokens_generated:
            tokens_per_second = tokens_generated / inference_time
            self.logger.debug(f"   Tokens/second: {tokens_per_second:.1f}")
    
    def log_potential_hallucination(self, question: str, response: str, 
                                   severity: str = "LOW"):
        """Log potential LLM hallucination"""
        
        self.logger.warning(
            f"⚠️  POTENTIAL HALLUCINATION [{severity}]\n"
            f"   Question: {question}\n"
            f"   Response: {response[:100]}...\n"
            f"   Review manually!"
        )
    
    def log_conflict_detected(self, vendor: str, matching_rules: list):
        """Log rule conflict"""
        
        rule_str = ", ".join([f"{r['rule_id']}({r['category']})" for r in matching_rules])
        
        self.conflicts.append({
            'timestamp': datetime.now().isoformat(),
            'vendor': vendor,
            'matching_rules': rule_str,
            'count': len(matching_rules)
        })
        
        self.logger.warning(
            f"⚠️  RULE CONFLICT: {vendor} matches multiple rules:\n"
            f"      {rule_str}"
        )
    
    def save_metrics_summary(self):
        """Save metrics summary to JSON file"""
        
        summary = {
            'generated_at': datetime.now().isoformat(),
            'categorization_metrics': {
                'batches': len(self.categorization_times),
                'total_transactions': sum(c['transaction_count'] for c in self.categorization_times),
                'average_latency_seconds': sum(c['total_time_seconds'] for c in self.categorization_times) 
                                          / len(self.categorization_times) if self.categorization_times else 0,
                'average_per_transaction_ms': sum(c['time_per_transaction_ms'] for c in self.categorization_times) 
                                             / len(self.categorization_times) if self.categorization_times else 0,
                'total_conflicts': sum(c['conflict_count'] for c in self.categorization_times),
                'average_conflict_rate_percent': sum(c['conflict_rate_percent'] for c in self.categorization_times) 
                                                / len(self.categorization_times) if self.categorization_times else 0,
                'details': self.categorization_times
            },
            'hash_stability': {
                'tracked_vendors': len(self.hash_values),
                'hashes': self.hash_values
            },
            'llm_metrics': {
                'total_queries': len(self.llm_inferences),
                'average_inference_time_seconds': sum(i['inference_time_seconds'] for i in self.llm_inferences) 
                                                 / len(self.llm_inferences) if self.llm_inferences else 0,
                'average_memory_used_mb': sum(i['memory_used_mb'] for i in self.llm_inferences) 
                                         / len(self.llm_inferences) if self.llm_inferences else 0,
                'peak_memory_mb': max([i['memory_peak_mb'] for i in self.llm_inferences]) if self.llm_inferences else 0,
                'details': self.llm_inferences
            },
            'conflicts': {
                'total_conflicts': len(self.conflicts),
                'details': self.conflicts
            }
        }
        
        metrics_file = self.log_dir / f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(metrics_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        self.logger.debug(f"📊 Metrics saved: {metrics_file}")
        return metrics_file
    
    def get_llm_query_history(self) -> list:
        """Return formatted LLM query history"""
        if not self.llm_inferences:
            return []
        
        history = []
        for i, inference in enumerate(self.llm_inferences, 1):
            response_preview = inference.get('response', '')[:100]
            if len(inference.get('response', '')) > 100:
                response_preview += '...'
            
            history.append({
                'index': i,
                'timestamp': inference.get('timestamp', 'unknown'),
                'question': inference.get('question', 'unknown'),
                'response_preview': response_preview,
                'inference_time': inference.get('inference_time_seconds', 0),
                'response_length': inference.get('response_length', 0),
                'memory_peak': inference.get('memory_peak_mb', 0)
            })
        return history
    
    def get_llm_query_full(self, query_index: int) -> dict:
        """Return full details of a specific LLM query (0-indexed)"""
        if 0 <= query_index < len(self.llm_inferences):
            return self.llm_inferences[query_index]
        return None

    def display_summary(self, summary_data=None):
        """Display summary to console (for menu viewing)"""
        # Use current in-memory metrics, not JSON file (they're more up-to-date)
        avg_latency = sum(c['total_time_seconds'] for c in self.categorization_times) / len(self.categorization_times) if self.categorization_times else 0
        avg_conflict = sum(c['conflict_rate_percent'] for c in self.categorization_times) / len(self.categorization_times) if self.categorization_times else 0
        avg_llm_time = sum(i['inference_time_seconds'] for i in self.llm_inferences) / len(self.llm_inferences) if self.llm_inferences else 0
        avg_llm_memory = sum(i['memory_used_mb'] for i in self.llm_inferences) / len(self.llm_inferences) if self.llm_inferences else 0
        
        print(f"\n{'='*70}")
        print("PERFORMANCE SUMMARY")
        print(f"{'='*70}")
        print(f"Categorization Latency: {avg_latency:.2f}s avg")
        print(f"Conflict Frequency: {avg_conflict:.1f}%")
        print(f"Hash Stability: {len(self.hash_values)} vendors tracked")
        print(f"LLM Inference Time: {avg_llm_time:.2f}s avg")
        print(f"LLM Memory Usage: {avg_llm_memory:.1f}MB avg")
        print(f"{'='*70}\n")
    
    def close(self):
        """Close logging handlers"""
        for handler in self.logger.handlers:
            handler.close()
        self.logger.info("Application closed")
        self.logger.info("═" * 70)


# Global metrics logger instance
_metrics_logger = None

def get_metrics_logger() -> MetricsLogger:
    """Get or create global metrics logger"""
    global _metrics_logger
    if _metrics_logger is None:
        _metrics_logger = MetricsLogger()
    return _metrics_logger

def init_metrics_logger(log_dir: str = None) -> MetricsLogger:
    """Initialize metrics logger"""
    global _metrics_logger
    _metrics_logger = MetricsLogger(log_dir)
    return _metrics_logger
