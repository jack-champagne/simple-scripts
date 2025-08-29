#!/usr/bin/env python3
"""
GitHub Actions Usage Analyzer

This script analyzes GitHub Actions usage data from a CSV report,
calculating total minutes for different runner types and providing
cost analysis for business justification of self-hosted runners.
"""

import csv
import argparse
from collections import defaultdict
from pathlib import Path


def analyze_usage_data(csv_file_path):
    """
    Analyze GitHub Actions usage data from CSV file.
    
    Args:
        csv_file_path (str): Path to the CSV file containing usage data
        
    Returns:
        dict: Analysis results containing totals and breakdowns
    """
    results = {
        'total_linux_minutes': 0,
        'total_macos_minutes': 0,
        'total_windows_minutes': 0,
        'total_self_hosted_linux_minutes': 0,
        'repository_breakdown': defaultdict(lambda: {
            'linux': 0, 'macos': 0, 'windows': 0, 'self_hosted_linux': 0
        }),
        'daily_breakdown': defaultdict(lambda: {
            'linux': 0, 'macos': 0, 'windows': 0, 'self_hosted_linux': 0
        }),
        'total_cost': 0
    }
    
    # Cost per minute for different runner types (GitHub pricing)
    costs = {
        'actions_linux': 0.008,
        'actions_macos': 0.08,
        'actions_windows': 0.016,
        'actions_self_hosted_linux': 0  # Self-hosted runners are free
    }
    
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            
            for row in reader:
                sku = row['sku'].strip('"')
                quantity = float(row['quantity'].strip('"'))
                unit_type = row['unit_type'].strip('"')
                repository = row['repository'].strip('"')
                date = row['date'].strip('"')
                cost_per_unit = float(row['applied_cost_per_quantity'].strip('"'))
                
                # Only process minute-based usage
                if unit_type != 'minutes':
                    continue
                
                # Calculate costs
                line_cost = quantity * cost_per_unit
                results['total_cost'] += line_cost
                
                # Track different runner types
                if sku == 'actions_linux':
                    results['total_linux_minutes'] += quantity
                    results['repository_breakdown'][repository]['linux'] += quantity
                    results['daily_breakdown'][date]['linux'] += quantity
                elif sku == 'actions_macos':
                    results['total_macos_minutes'] += quantity
                    results['repository_breakdown'][repository]['macos'] += quantity
                    results['daily_breakdown'][date]['macos'] += quantity
                elif sku == 'actions_windows':
                    results['total_windows_minutes'] += quantity
                    results['repository_breakdown'][repository]['windows'] += quantity
                    results['daily_breakdown'][date]['windows'] += quantity
                elif sku == 'actions_self_hosted_linux':
                    results['total_self_hosted_linux_minutes'] += quantity
                    results['repository_breakdown'][repository]['self_hosted_linux'] += quantity
                    results['daily_breakdown'][date]['self_hosted_linux'] += quantity
    
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return None
    
    return results


def print_analysis_report(results):
    """Print a comprehensive analysis report."""
    if not results:
        return
    
    print("=" * 60)
    print("GitHub Actions Usage Analysis Report")
    print("=" * 60)
    
    # Summary totals
    print("\n📊 SUMMARY TOTALS")
    print(f"Linux runners:         {results['total_linux_minutes']:,.0f} minutes")
    print(f"macOS runners:         {results['total_macos_minutes']:,.0f} minutes")
    print(f"Windows runners:       {results['total_windows_minutes']:,.0f} minutes")
    print(f"Self-hosted Linux:     {results['total_self_hosted_linux_minutes']:,.0f} minutes")
    
    total_hosted_minutes = (results['total_linux_minutes'] + 
                           results['total_macos_minutes'] + 
                           results['total_windows_minutes'])
    print(f"Total GitHub-hosted:   {total_hosted_minutes:,.0f} minutes")
    
    # Cost analysis
    print(f"\n💰 COST ANALYSIS")
    print(f"Total actual cost:     ${results['total_cost']:.2f}")
    
    # Calculate theoretical costs at standard rates
    theoretical_linux_cost = results['total_linux_minutes'] * 0.008
    theoretical_macos_cost = results['total_macos_minutes'] * 0.08
    theoretical_windows_cost = results['total_windows_minutes'] * 0.016
    theoretical_total = theoretical_linux_cost + theoretical_macos_cost + theoretical_windows_cost
    
    print(f"Theoretical Linux cost: ${theoretical_linux_cost:.2f} ({results['total_linux_minutes']:,.0f} × $0.008)")
    if results['total_macos_minutes'] > 0:
        print(f"Theoretical macOS cost: ${theoretical_macos_cost:.2f} ({results['total_macos_minutes']:,.0f} × $0.080)")
    if results['total_windows_minutes'] > 0:
        print(f"Theoretical Windows cost: ${theoretical_windows_cost:.2f} ({results['total_windows_minutes']:,.0f} × $0.016)")
    print(f"Theoretical total cost: ${theoretical_total:.2f}")
    
    # Self-hosted runner analysis
    if results['total_self_hosted_linux_minutes'] > 0:
        print(f"\n🏠 SELF-HOSTED ANALYSIS")
        print(f"Self-hosted minutes:   {results['total_self_hosted_linux_minutes']:,.0f} (FREE)")
        saved_cost = results['total_self_hosted_linux_minutes'] * 0.008
        print(f"Cost savings:          ${saved_cost:.2f}")
    
    # Repository breakdown
    print(f"\n📁 REPOSITORY BREAKDOWN")
    for repo, usage in sorted(results['repository_breakdown'].items()):
        total_repo_minutes = sum(usage.values())
        if total_repo_minutes > 0:
            print(f"{repo:<30} {total_repo_minutes:>6.0f} minutes", end="")
            if usage['linux'] > 0:
                print(f" (L:{usage['linux']:.0f}", end="")
                if usage['macos'] > 0:
                    print(f", M:{usage['macos']:.0f}", end="")
                if usage['windows'] > 0:
                    print(f", W:{usage['windows']:.0f}", end="")
                if usage['self_hosted_linux'] > 0:
                    print(f", SH:{usage['self_hosted_linux']:.0f}", end="")
                print(")", end="")
            print()
    
    # Daily breakdown (top 5 days)
    print(f"\n📅 TOP USAGE DAYS")
    daily_totals = [(date, sum(usage.values())) for date, usage in results['daily_breakdown'].items()]
    daily_totals.sort(key=lambda x: x[1], reverse=True)
    
    for date, total_minutes in daily_totals[:5]:
        if total_minutes > 0:
            usage = results['daily_breakdown'][date]
            print(f"{date}: {total_minutes:>6.0f} minutes", end="")
            if usage['linux'] > 0:
                print(f" (L:{usage['linux']:.0f}", end="")
                if usage['macos'] > 0:
                    print(f", M:{usage['macos']:.0f}", end="")
                if usage['windows'] > 0:
                    print(f", W:{usage['windows']:.0f}", end="")
                if usage['self_hosted_linux'] > 0:
                    print(f", SH:{usage['self_hosted_linux']:.0f}", end="")
                print(")", end="")
            print()
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze GitHub Actions usage data from CSV report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s usage_report.csv
  %(prog)s --summary-only usage_report.csv
  %(prog)s --linux-only usage_report.csv
        """
    )
    
    parser.add_argument('csv_file', help='Path to the CSV usage report file')
    parser.add_argument('--summary-only', action='store_true', 
                       help='Show only summary totals')
    parser.add_argument('--linux-only', action='store_true',
                       help='Show only Linux runner usage (like the awk command)')
    
    args = parser.parse_args()
    
    # Verify file exists
    if not Path(args.csv_file).exists():
        print(f"Error: File '{args.csv_file}' does not exist.")
        return 1
    
    # Analyze the data
    results = analyze_usage_data(args.csv_file)
    if not results:
        return 1
    
    # Print results based on options
    if args.linux_only:
        print(f"Total actions_linux minutes: {results['total_linux_minutes']:,.0f}")
    elif args.summary_only:
        print(f"Linux:      {results['total_linux_minutes']:,.0f} minutes")
        print(f"macOS:      {results['total_macos_minutes']:,.0f} minutes")
        print(f"Windows:    {results['total_windows_minutes']:,.0f} minutes")
        print(f"Self-hosted: {results['total_self_hosted_linux_minutes']:,.0f} minutes")
        print(f"Total cost: ${results['total_cost']:.2f}")
    else:
        print_analysis_report(results)
    
    return 0


if __name__ == '__main__':
    exit(main())
