import os
from dotenv import load_dotenv

load_dotenv()

# GitHub Configuration
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME', 'onamfc')

# Rate limiting and batch configuration
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 10))
DELAY_BETWEEN_REQUESTS = float(os.getenv('DELAY_BETWEEN_REQUESTS', 1.0))
MAX_UNFOLLOWS_PER_RUN = int(os.getenv('MAX_UNFOLLOWS_PER_RUN', 50))

# GitHub API Configuration
GITHUB_API_BASE = 'https://api.github.com'
ITEMS_PER_PAGE = 100  # GitHub API maximum

# Database Configuration
DATABASE_FILE = 'github_followers.db'

# Logging Configuration
LOG_FILE = 'github_unfollow.log'
LOG_LEVEL = 'INFO'