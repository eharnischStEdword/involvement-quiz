#!/usr/bin/env python3
"""
Memory monitoring script for the involvement quiz application.
This script helps track memory usage and identify potential memory leaks.
"""

import time
import json
import requests
from datetime import datetime
import argparse

def get_memory_status(url):
    """Get memory status from the application"""
    try:
        response = requests.get(f"{url}/api/memory-status", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting memory status: {e}")
        return None

def get_health_status(url):
    """Get health status from the application"""
    try:
        response = requests.get(f"{url}/api/health", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error getting health status: {e}")
        return None

def monitor_memory(url, interval=60, duration=None):
    """Monitor memory usage over time"""
    print(f"Starting memory monitoring for {url}")
    print(f"Interval: {interval} seconds")
    if duration:
        print(f"Duration: {duration} seconds")
    print("-" * 80)
    
    start_time = time.time()
    measurements = []
    
    try:
        while True:
            current_time = time.time()
            
            # Check if we should stop
            if duration and (current_time - start_time) >= duration:
                break
            
            # Get memory status
            memory_data = get_memory_status(url)
            health_data = get_health_status(url)
            
            if memory_data and health_data:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Extract key metrics
                process_rss = memory_data.get('process', {}).get('rss_mb', 'N/A')
                process_percent = memory_data.get('process', {}).get('percent', 'N/A')
                system_percent = memory_data.get('system', {}).get('percent', 'N/A')
                cache_memory = memory_data.get('cache', {}).get('memory_usage_mb', 'N/A')
                health_status = health_data.get('status', 'N/A')
                
                # Print current status
                print(f"[{timestamp}] "
                      f"Process: {process_rss}MB ({process_percent}%) | "
                      f"System: {system_percent}% | "
                      f"Cache: {cache_memory}MB | "
                      f"Health: {health_status}")
                
                # Store measurement
                measurements.append({
                    'timestamp': timestamp,
                    'process_rss_mb': process_rss,
                    'process_percent': process_percent,
                    'system_percent': system_percent,
                    'cache_memory_mb': cache_memory,
                    'health_status': health_status
                })
                
                # Check for potential issues
                if isinstance(process_percent, (int, float)) and process_percent > 80:
                    print(f"  ⚠️  WARNING: High process memory usage ({process_percent}%)")
                
                if isinstance(system_percent, (int, float)) and system_percent > 80:
                    print(f"  ⚠️  WARNING: High system memory usage ({system_percent}%)")
                
                if isinstance(cache_memory, (int, float)) and cache_memory > 40:
                    print(f"  ⚠️  WARNING: Cache near memory limit ({cache_memory}MB)")
                
                if health_status != 'healthy':
                    print(f"  ⚠️  WARNING: Health status is {health_status}")
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    
    # Print summary
    print("\n" + "=" * 80)
    print("MONITORING SUMMARY")
    print("=" * 80)
    
    if measurements:
        # Calculate statistics
        process_values = [m['process_rss_mb'] for m in measurements if isinstance(m['process_rss_mb'], (int, float))]
        process_percent_values = [m['process_percent'] for m in measurements if isinstance(m['process_percent'], (int, float))]
        
        if process_values:
            print(f"Process Memory (RSS):")
            print(f"  Min: {min(process_values):.2f}MB")
            print(f"  Max: {max(process_values):.2f}MB")
            print(f"  Avg: {sum(process_values)/len(process_values):.2f}MB")
        
        if process_percent_values:
            print(f"Process Memory (%):")
            print(f"  Min: {min(process_percent_values):.2f}%")
            print(f"  Max: {max(process_percent_values):.2f}%")
            print(f"  Avg: {sum(process_percent_values)/len(process_percent_values):.2f}%")
        
        # Check for memory growth
        if len(process_values) > 10:
            first_half = process_values[:len(process_values)//2]
            second_half = process_values[len(process_values)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            growth = ((second_avg - first_avg) / first_avg) * 100 if first_avg > 0 else 0
            
            print(f"\nMemory Growth Analysis:")
            print(f"  First half avg: {first_avg:.2f}MB")
            print(f"  Second half avg: {second_avg:.2f}MB")
            print(f"  Growth: {growth:.2f}%")
            
            if growth > 10:
                print(f"  ⚠️  WARNING: Significant memory growth detected!")
            elif growth > 5:
                print(f"  ⚠️  CAUTION: Moderate memory growth detected")
            else:
                print(f"  ✅ Memory usage appears stable")
        
        print(f"\nTotal measurements: {len(measurements)}")
        print(f"Monitoring duration: {time.time() - start_time:.1f} seconds")
        
        # Save data to file
        filename = f"memory_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(measurements, f, indent=2)
        print(f"Data saved to: {filename}")

def main():
    parser = argparse.ArgumentParser(description='Monitor memory usage of the involvement quiz application')
    parser.add_argument('--url', default='https://involvement-quiz.onrender.com',
                       help='Application URL (default: https://involvement-quiz.onrender.com)')
    parser.add_argument('--interval', type=int, default=60,
                       help='Monitoring interval in seconds (default: 60)')
    parser.add_argument('--duration', type=int, default=None,
                       help='Monitoring duration in seconds (default: run indefinitely)')
    
    args = parser.parse_args()
    
    monitor_memory(args.url, args.interval, args.duration)

if __name__ == '__main__':
    main() 