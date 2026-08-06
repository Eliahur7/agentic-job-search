#!/usr/bin/env python3
"""
CLI tool for managing the Agentic Job Search pipeline locally.
Examples:
  python3 backend/app/cli.py list
  python3 backend/app/cli.py list --status Applied
  python3 backend/app/cli.py mark <job_id> Applied
  python3 backend/app/cli.py show <job_id>
  python3 backend/app/cli.py digest
"""

import sys
import os
import argparse
from datetime import datetime

# Add parent directory to path for imports
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.database import get_pipeline_snapshot, update_job_status


def format_job(job: dict, include_url: bool = False) -> str:
    """Format a job record for display."""
    status_badge = "✓" if job.get("applied") else " "
    url_str = f"\n  URL: {job.get('url', 'N/A')}" if include_url and job.get("url") else ""
    return (
        f"[{status_badge}] {job['company']} — {job['title']}\n"
        f"    ID: {job['id'][:60]}...\n"
        f"    Match: {job.get('match_score', 'N/A')}% | Status: {job.get('status', 'N/A')}\n"
        f"    Processed: {job.get('processed_at', 'N/A')}{url_str}"
    )


def cmd_list(args):
    """List jobs in the pipeline, optionally filtered by status."""
    jobs = get_pipeline_snapshot()
    
    if args.status:
        jobs = [j for j in jobs if j.get("status", "").lower() == args.status.lower()]
    
    if not jobs:
        print(f"No jobs found" + (f" with status '{args.status}'" if args.status else ""))
        return
    
    print(f"\n{'Pipeline Snapshot':^60}\n")
    for i, job in enumerate(jobs, 1):
        print(f"{i}. {format_job(job)}")
    
    applied_count = sum(1 for j in jobs if j.get("applied"))
    print(f"\nTotal: {len(jobs)} | Applied: {applied_count}")


def cmd_show(args):
    """Show details of a specific job."""
    jobs = get_pipeline_snapshot()
    job = next((j for j in jobs if j["id"] == args.job_id), None)
    
    if not job:
        print(f"Job not found: {args.job_id}")
        return
    
    print(f"\n{'Job Details':^60}\n")
    print(format_job(job, include_url=True))
    print(f"\n  Status: {job.get('status')}")
    print(f"  Applied: {'Yes' if job.get('applied') else 'No'}")
    print(f"  Notes: {job.get('notes', 'None')}")
    if job.get("raw_description"):
        desc = job["raw_description"]
        print(f"\n  Description (first 300 chars):\n  {desc[:300]}...")


def cmd_mark(args):
    """Mark a job as applied (or update status)."""
    jobs = get_pipeline_snapshot()
    job = next((j for j in jobs if j["id"] == args.job_id), None)
    
    if not job:
        print(f"Job not found: {args.job_id}")
        return
    
    status = args.status or "Applied"
    notes = args.notes or ""
    update_job_status(args.job_id, status, notes)
    print(f"✓ Job marked as '{status}'\n  ID: {args.job_id[:60]}...\n  Company: {job['company']}")


def cmd_digest(args):
    """Print a daily digest of the pipeline."""
    jobs = get_pipeline_snapshot()
    
    if not jobs:
        print("No jobs in pipeline yet.")
        return
    
    print(f"\n{'Daily Job Pipeline Digest':^60}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Summarize by status
    statuses = {}
    for job in jobs:
        st = job.get("status", "Unknown")
        if st not in statuses:
            statuses[st] = []
        statuses[st].append(job)
    
    for status, job_list in sorted(statuses.items()):
        print(f"\n{status.upper()} ({len(job_list)}):")
        for job in sorted(job_list, key=lambda j: j.get("match_score", 0), reverse=True):
            score = job.get("match_score", "N/A")
            applied = "✓ APPLIED" if job.get("applied") else ""
            print(f"  • {job['company']:<30} {job['title']:<40} {score}% {applied}")
    
    applied_count = sum(1 for j in jobs if j.get("applied"))
    total = len(jobs)
    print(f"\n{'─'*60}")
    print(f"Total Jobs: {total} | Applied: {applied_count} | Pending: {total - applied_count}")


def main():
    parser = argparse.ArgumentParser(
        description="Agentic Job Search Pipeline Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # list
    list_parser = subparsers.add_parser("list", help="List jobs in pipeline")
    list_parser.add_argument("--status", help="Filter by status (e.g., Applied, Evaluated)")
    list_parser.set_defaults(func=cmd_list)
    
    # show
    show_parser = subparsers.add_parser("show", help="Show details of a job")
    show_parser.add_argument("job_id", help="Job ID to display")
    show_parser.set_defaults(func=cmd_show)
    
    # mark
    mark_parser = subparsers.add_parser("mark", help="Mark job as applied or update status")
    mark_parser.add_argument("job_id", help="Job ID to update")
    mark_parser.add_argument("status", nargs="?", default="Applied", help="New status (default: Applied)")
    mark_parser.add_argument("--notes", help="Optional notes")
    mark_parser.set_defaults(func=cmd_mark)
    
    # digest
    digest_parser = subparsers.add_parser("digest", help="Print daily pipeline digest")
    digest_parser.set_defaults(func=cmd_digest)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)


if __name__ == "__main__":
    main()
