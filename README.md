# GitHub Unfollow Tool

A Python tool to help you unfollow GitHub users who are not following you back. This tool respects GitHub's API rate limits and Terms of Service, making it safe to use for managing your GitHub following list. Obviously, the settings can be changed, so use it responsibly and at your own risk!

## Features

- **Rate Limited**: Respects GitHub API rate limits (5000 requests/hour)
- **Database Tracking**: Uses SQLite to track followers, following, and unfollowed users
- **Batch Processing**: Processes users in configurable batches
- **Cron-Friendly**: Designed to run as scheduled jobs
- **Comprehensive Logging**: Detailed logging for monitoring and debugging
- **Statistics**: View your current follow/unfollow statistics
- **Dry Run Mode**: Test what would be unfollowed without actually unfollowing
- **Safe & Respectful**: Built with GitHub ToS compliance in mind

## Prerequisites

- Python 3.7 or higher
- A GitHub Personal Access Token with appropriate permissions

## Installation

1. Clone this repository:
```bash
git clone https://github.com/onamfc/github-non-follow-backs.git
cd GithubNonFollwBacks
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create your environment configuration:
```bash
cp .env.example .env
```

4. Edit `.env` file with your settings:
```bash
GITHUB_TOKEN=your_github_personal_access_token_here
GITHUB_USERNAME=your_username
BATCH_SIZE=10
DELAY_BETWEEN_REQUESTS=1
MAX_UNFOLLOWS_PER_RUN=50
```

## GitHub Token Setup

1. Go to GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a descriptive name like "Unfollow Tool"
4. Select the following scopes:
   - `user:follow` (to manage who you follow)
   - `read:user` (to read user information)
5. Copy the generated token and add it to your `.env` file

## Usage

### Basic Commands

```bash
# Show current statistics
python main.py --stats

# Sync your followers and following data from GitHub
python main.py --sync

# Unfollow a batch of users who are not following you back
python main.py --unfollow

# Dry run to see what would be unfollowed
python main.py --unfollow --dry-run

# Sync data and then unfollow batch
python main.py --sync --unfollow
```

### Recommended Workflow

1. **First run** - Sync your data:
```bash
python main.py --sync --stats
```

2. **Test with dry run**:
```bash
python main.py --unfollow --dry-run
```

3. **Start unfollowing**:
```bash
python main.py --unfollow --stats
```

## Automation with Cron

You can automate this tool using cron jobs. Here are some examples:

```bash
# Edit your crontab
crontab -e
```

### Example Cron Jobs

```bash
# Sync data every 6 hours
0 */6 * * * cd /path/to/github-unfollow-tool && python main.py --sync

# Unfollow batch every hour during business hours
0 9-17 * * * cd /path/to/github-unfollow-tool && python main.py --unfollow

# Full sync and unfollow every morning at 8 AM
0 8 * * * cd /path/to/github-unfollow-tool && python main.py --sync --unfollow --stats
```

## Configuration Options

The `.env` file supports the following configuration options:

| Variable | Default       | Description |
|----------|---------------|-------------|
| `GITHUB_TOKEN` | -             | Your GitHub Personal Access Token (required) |
| `GITHUB_USERNAME` | your_username | Your GitHub username |
| `BATCH_SIZE` | 10            | Number of users to process in each batch |
| `DELAY_BETWEEN_REQUESTS` | 1.0           | Seconds to wait between API requests |
| `MAX_UNFOLLOWS_PER_RUN` | 50            | Maximum users to unfollow per execution |

## Database Schema

The tool creates a SQLite database (`github_followers.db`) with the following tables:

- **following**: Users you are following
- **followers**: Users following you
- **unfollowed**: Users you have unfollowed (prevents re-following)
- **processing_status**: Logs of tool execution

## Rate Limiting & GitHub ToS Compliance

This tool is designed to be respectful of GitHub's infrastructure and policies:

- **Rate Limiting**: Monitors and respects the 5000 requests/hour limit
- **Request Delays**: Adds delays between requests (configurable)
- **Conservative Batching**: Processes users in small batches
- **Error Handling**: Gracefully handles API errors and timeouts
- **Logging**: Comprehensive logging for monitoring

## Safety Features

- **Double-checking**: Verifies users are still not following before unfollowing
- **Database Tracking**: Prevents accidentally unfollowing the same user multiple times
- **Dry Run Mode**: Test operations without making actual changes
- **Error Recovery**: Graceful error handling and recovery
- **Conservative Defaults**: Safe default values for batch sizes and delays

## Logging

The tool creates detailed logs in `github_unfollow.log`. Log levels include:

- `INFO`: Normal operations and statistics
- `WARNING`: Rate limit warnings and recoverable issues
- `ERROR`: Errors and failures

## Troubleshooting

### Common Issues

1. **Authentication Error**:
   - Verify your GitHub token has correct permissions
   - Check that the token hasn't expired

2. **Rate Limit Exceeded**:
   - The tool should handle this automatically
   - Increase `DELAY_BETWEEN_REQUESTS` if needed

3. **Database Locked**:
   - Make sure only one instance is running at a time
   - Check file permissions on the database

### Getting Help

1. Check the log file: `github_unfollow.log`
2. Run with `--stats` to see current state
3. Try a dry run first: `--dry-run`
4. Open an issue on GitHub if problems persist

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Disclaimer

This tool is for educational and personal use. Users are responsible for complying with GitHub's Terms of Service and API usage policies. Use responsibly and respect the GitHub community.


