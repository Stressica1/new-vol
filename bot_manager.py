#!/usr/bin/env python3
"""
🏔️ Alpine Bot Manager - Process Management
"""

import os
import sys
import psutil
import time
from typing import List, Dict

class AlpineBotManager:
    """Process manager for Alpine Trading Bot"""
    
    def __init__(self):
        self.name = "Alpine Bot Manager"
        self.version = "2.0"
        
        # Process names to manage
        self.bot_processes = [
            'alpine_bot.py',
            'working_trading_system.py',
            'simple_alpine.py',
            'run_alpine_bot.py',
            'trading_dashboard.py',
            'volume_anom_bot.py',
            'bot.py'
        ]
    
    def find_alpine_processes(self) -> List[Dict]:
        """Find all Alpine bot processes"""
        processes = []
        current_pid = os.getpid()
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['pid'] == current_pid:
                        continue
                    
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    
                    # Check if it's a bot process
                    if any(bot_name in cmdline for bot_name in self.bot_processes):
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline
                        })
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            print(f"❌ Error finding processes: {e}")
        
        return processes
    
    def kill_alpine_processes(self, exclude_current: bool = True) -> int:
        """Kill all Alpine bot processes"""
        processes = self.find_alpine_processes()
        killed_count = 0
        current_pid = os.getpid()
        
        for proc_info in processes:
            try:
                pid = proc_info['pid']
                
                if exclude_current and pid == current_pid:
                    continue
                
                # Try to terminate gracefully first
                proc = psutil.Process(pid)
                proc.terminate()
                
                # Wait up to 3 seconds for graceful termination
                try:
                    proc.wait(timeout=3)
                except psutil.TimeoutExpired:
                    # Force kill if graceful termination fails
                    proc.kill()
                
                killed_count += 1
                print(f"✅ Killed process {pid}: {proc_info['name']}")
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            except Exception as e:
                print(f"❌ Error killing process {pid}: {e}")
        
        return killed_count
    
    def is_bot_running(self) -> bool:
        """Check if any bot is currently running"""
        processes = self.find_alpine_processes()
        return len(processes) > 0
    
    def get_bot_status(self) -> Dict:
        """Get bot status information"""
        processes = self.find_alpine_processes()
        
        return {
            'running': len(processes) > 0,
            'process_count': len(processes),
            'processes': processes,
            'timestamp': time.time()
        }
    
    def cleanup_logs(self, days_to_keep: int = 30):
        """Clean up old log files"""
        try:
            log_dir = "logs"
            if not os.path.exists(log_dir):
                return
            
            current_time = time.time()
            cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)
            
            for filename in os.listdir(log_dir):
                filepath = os.path.join(log_dir, filename)
                
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        print(f"🗑️ Removed old log file: {filename}")
                        
        except Exception as e:
            print(f"❌ Error cleaning logs: {e}")

def main():
    """Test the bot manager"""
    manager = AlpineBotManager()
    print(f"✅ {manager.name} v{manager.version} initialized")
    
    # Check status
    status = manager.get_bot_status()
    print(f"🤖 Bot status: {status}")
    
    # Find processes
    processes = manager.find_alpine_processes()
    print(f"📊 Found {len(processes)} bot processes")

if __name__ == "__main__":
    main()
