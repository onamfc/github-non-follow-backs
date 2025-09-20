import requests
import time
import logging
from datetime import datetime, timedelta
from config import GITHUB_TOKEN, GITHUB_API_BASE, ITEMS_PER_PAGE, DELAY_BETWEEN_REQUESTS

class GitHubClient:
    def __init__(self):
        self.token = GITHUB_TOKEN
        self.base_url = GITHUB_API_BASE
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-Unfollow-Tool/1.0'
        })
        self.rate_limit_remaining = 5000
        self.rate_limit_reset = datetime.now()
        
    def _check_rate_limit(self):
        """Check and handle rate limiting"""
        if self.rate_limit_remaining <= 100:  # Conservative buffer
            sleep_time = (self.rate_limit_reset - datetime.now()).total_seconds()
            if sleep_time > 0:
                logging.warning(f"Rate limit low. Sleeping for {sleep_time} seconds")
                time.sleep(sleep_time + 60)  # Extra minute buffer
        
        # Always add delay between requests to be respectful
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    def _update_rate_limit_info(self, response):
        """Update rate limit info from response headers"""
        if 'X-RateLimit-Remaining' in response.headers:
            self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        
        if 'X-RateLimit-Reset' in response.headers:
            reset_timestamp = int(response.headers['X-RateLimit-Reset'])
            self.rate_limit_reset = datetime.fromtimestamp(reset_timestamp)
    
    def _make_request(self, method, url, **kwargs):
        """Make a request with rate limiting and error handling"""
        self._check_rate_limit()
        
        try:
            response = self.session.request(method, url, **kwargs)
            self._update_rate_limit_info(response)
            
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                logging.error("Rate limit exceeded. Waiting...")
                time.sleep(3600)  # Wait an hour
                return self._make_request(method, url, **kwargs)
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")
            raise
    
    def get_all_following(self, username):
        """Get all users that the specified user is following"""
        following = []
        page = 1
        
        while True:
            url = f"{self.base_url}/users/{username}/following"
            params = {'page': page, 'per_page': ITEMS_PER_PAGE}
            
            logging.info(f"Fetching following page {page}")
            response = self._make_request('GET', url, params=params)
            
            users = response.json()
            if not users:
                break
                
            following.extend(users)
            page += 1
            
            logging.info(f"Collected {len(following)} following users so far")
        
        logging.info(f"Total following users collected: {len(following)}")
        return following
    
    def get_all_followers(self, username):
        """Get all followers of the specified user"""
        followers = []
        page = 1
        
        while True:
            url = f"{self.base_url}/users/{username}/followers"
            params = {'page': page, 'per_page': ITEMS_PER_PAGE}
            
            logging.info(f"Fetching followers page {page}")
            response = self._make_request('GET', url, params=params)
            
            users = response.json()
            if not users:
                break
                
            followers.extend(users)
            page += 1
            
            logging.info(f"Collected {len(followers)} followers so far")
        
        logging.info(f"Total followers collected: {len(followers)}")
        return followers
    
    def unfollow_user(self, username):
        """Unfollow a specific user"""
        url = f"{self.base_url}/user/following/{username}"
        
        try:
            response = self._make_request('DELETE', url)
            logging.info(f"Successfully unfollowed {username}")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to unfollow {username}: {e}")
            return False
    
    def check_if_following(self, username):
        """Check if I'm following a specific user"""
        url = f"{self.base_url}/user/following/{username}"
        
        try:
            response = self._make_request('GET', url)
            return response.status_code == 204
        except requests.exceptions.RequestException:
            return False
    
    def get_rate_limit_status(self):
        """Get current rate limit status"""
        url = f"{self.base_url}/rate_limit"
        response = self._make_request('GET', url)
        return response.json()