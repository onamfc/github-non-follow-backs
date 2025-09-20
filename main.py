#!/usr/bin/env python3
"""
GitHub Unfollow Tool
A tool to unfollow GitHub users who are not following you back.
Respects GitHub API rate limits and terms of service.

Author: Brandon Estrella
License: MIT
"""

import argparse
import logging
import sys
import time
from datetime import datetime

from config import (
    GITHUB_USERNAME, MAX_UNFOLLOWS_PER_RUN, LOG_FILE, LOG_LEVEL
)
from database import DatabaseManager
from github_client import GitHubClient

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

def sync_followers_and_following():
    """Sync followers and following lists from GitHub"""
    client = GitHubClient()
    db = DatabaseManager()
    
    logging.info("Starting sync of followers and following lists")
    
    try:
        # Get current following list
        logging.info("Fetching users I'm following...")
        following = client.get_all_following(GITHUB_USERNAME)
        db.update_following_list(following)
        
        # Get current followers list
        logging.info("Fetching my followers...")
        followers = client.get_all_followers(GITHUB_USERNAME)
        db.update_followers_list(followers)
        
        db.update_processing_status('sync', 'completed', 
                                   f'Following: {len(following)}, Followers: {len(followers)}')
        
        logging.info(f"Sync completed. Following: {len(following)}, Followers: {len(followers)}")
        
    except Exception as e:
        logging.error(f"Sync failed: {e}")
        db.update_processing_status('sync', 'failed', str(e))
        raise

def unfollow_batch():
    """Unfollow a batch of users who are not following back"""
    client = GitHubClient()
    db = DatabaseManager()
    
    logging.info(f"Starting unfollow batch (max {MAX_UNFOLLOWS_PER_RUN} users)")
    
    try:
        # Get users to unfollow
        users_to_unfollow = db.get_users_to_unfollow(MAX_UNFOLLOWS_PER_RUN)
        
        if not users_to_unfollow:
            logging.info("No users to unfollow")
            return
        
        unfollowed_count = 0
        failed_count = 0
        
        for user in users_to_unfollow:
            username = user['login']
            user_id = user['id']
            
            logging.info(f"Attempting to unfollow {username}")
            
            # Double-check that user is not following back
            # This is a safety measure in case data is stale
            try:
                # Verify user is still being followed
                if not client.check_if_following(username):
                    logging.info(f"Already not following {username}, marking as unfollowed")
                    db.mark_as_unfollowed(username, user_id)
                    continue
                
                # Attempt to unfollow
                if client.unfollow_user(username):
                    db.mark_as_unfollowed(username, user_id)
                    unfollowed_count += 1
                    logging.info(f"Successfully unfollowed {username}")
                else:
                    failed_count += 1
                    logging.error(f"Failed to unfollow {username}")
                
                # Small delay between unfollows to be extra respectful
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Error processing {username}: {e}")
                failed_count += 1
        
        db.update_processing_status('unfollow_batch', 'completed',
                                   f'Unfollowed: {unfollowed_count}, Failed: {failed_count}')
        
        logging.info(f"Unfollow batch completed. Unfollowed: {unfollowed_count}, Failed: {failed_count}")
        
    except Exception as e:
        logging.error(f"Unfollow batch failed: {e}")
        db.update_processing_status('unfollow_batch', 'failed', str(e))
        raise

def show_stats():
    """Display current statistics"""
    db = DatabaseManager()
    stats = db.get_stats()
    
    print("\n" + "="*50)
    print("GITHUB UNFOLLOW TOOL STATISTICS")
    print("="*50)
    print(f"Following: {stats['following']:,}")
    print(f"Followers: {stats['followers']:,}")
    print(f"Users to unfollow: {stats['to_unfollow']:,}")
    print(f"Already unfollowed: {stats['unfollowed']:,}")
    print(f"Follow ratio: {stats['followers']}/{stats['following']} = {stats['followers']/max(stats['following'], 1):.2%}")
    print("="*50)

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description='GitHub Unfollow Tool - Unfollow users who are not following you back',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --sync                  # Sync followers/following data
  python main.py --unfollow             # Unfollow batch of users
  python main.py --stats                # Show statistics
  python main.py --sync --unfollow      # Sync data then unfollow batch
        """
    )
    
    parser.add_argument('--sync', action='store_true',
                       help='Sync followers and following data from GitHub')
    parser.add_argument('--unfollow', action='store_true',
                       help='Unfollow a batch of users who are not following back')
    parser.add_argument('--stats', action='store_true',
                       help='Show current statistics')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be unfollowed without actually unfollowing')
    
    args = parser.parse_args()
    
    if not any([args.sync, args.unfollow, args.stats]):
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.stats:
            show_stats()
        
        if args.sync:
            sync_followers_and_following()
        
        if args.unfollow:
            if args.dry_run:
                db = DatabaseManager()
                users_to_unfollow = db.get_users_to_unfollow(MAX_UNFOLLOWS_PER_RUN)
                print(f"\nDRY RUN: Would unfollow {len(users_to_unfollow)} users:")
                for user in users_to_unfollow[:10]:  # Show first 10
                    print(f"  - {user['login']}")
                if len(users_to_unfollow) > 10:
                    print(f"  ... and {len(users_to_unfollow) - 10} more")
            else:
                unfollow_batch()
        
        if args.stats:  # Show stats again after operations
            show_stats()
            
    except KeyboardInterrupt:
        logging.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Operation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()