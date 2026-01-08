#!/usr/bin/env python3
"""
X Bot for posting bash shell tips every second day
"""

import tweepy
import json
import os
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class BashTipBot:
    # Hashtag pool for rotation (research shows 1-2 hashtags optimal for engagement)
    HASHTAG_POOL = [
        '#Linux',
        '#Bash',
        '#Terminal',
        '#TechTwitter',
        '#LinuxTips',
        '#DevOps',
    ]

    def __init__(self):
        # Load API credentials from environment variables
        self.api_key = os.getenv('X_API_KEY')
        self.api_secret = os.getenv('X_API_SECRET')
        self.access_token = os.getenv('X_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('X_ACCESS_TOKEN_SECRET')
        self.bearer_token = os.getenv('X_BEARER_TOKEN')
        
        if not all([self.api_key, self.api_secret, self.access_token, 
                    self.access_token_secret, self.bearer_token]):
            raise ValueError("Missing API credentials. Please set environment variables.")
        
        # Initialize Tweepy client with wait_on_rate_limit
        self.client = tweepy.Client(
            bearer_token=self.bearer_token,
            consumer_key=self.api_key,
            consumer_secret=self.api_secret,
            access_token=self.access_token,
            access_token_secret=self.access_token_secret,
            wait_on_rate_limit=True
        )
        
        self.state_file = 'bot_state.json'
        self.tips_file = 'tips.txt'
        
        # Load tips from file
        self.bash_tips = self.load_tips()
    
    def load_tips(self):
        """Load tips from the tips file"""
        if not os.path.exists(self.tips_file):
            raise FileNotFoundError(f"Tips file '{self.tips_file}' not found!")
        
        with open(self.tips_file, 'r', encoding='utf-8') as f:
            # Read non-empty lines, strip whitespace
            tips = [line.strip() for line in f if line.strip()]
        
        if not tips:
            raise ValueError(f"Tips file '{self.tips_file}' is empty!")

        return tips

    def get_hashtags(self, count=2):
        """Get random hashtags from the pool (1-2 recommended for optimal engagement)"""
        num_hashtags = min(count, len(self.HASHTAG_POOL))
        return random.sample(self.HASHTAG_POOL, num_hashtags)

    def load_state(self):
        """Load the bot's state from file"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            'last_post_date': None,
            'used_tips': []
        }
    
    def save_state(self, state):
        """Save the bot's state to file"""
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def should_post(self, state):
        """Check if it's time to post (every ~2 days, with 40 hour buffer)"""
        if state['last_post_date'] is None:
            return True

        last_post = datetime.fromisoformat(state['last_post_date'])
        now = datetime.now()
        hours_since_last_post = (now - last_post).total_seconds() / 3600

        return hours_since_last_post >= 40
    
    def get_next_tip(self, state):
        """Get the next tip in order that hasn't been used"""
        # Reset used tips if we've used them all
        if len(state['used_tips']) >= len(self.bash_tips):
            state['used_tips'] = []
        
        # Get the first unused tip (maintains order from tips.txt)
        for tip in self.bash_tips:
            if tip not in state['used_tips']:
                state['used_tips'].append(tip)
                return tip
        
        # Fallback (shouldn't happen due to reset above)
        return self.bash_tips[0]
    
    def post_tip(self):
        """Post a bash tip if it's time"""
        state = self.load_state()
        
        if not self.should_post(state):
            print("Not time to post yet. Waiting for the next scheduled day.")
            last_post = datetime.fromisoformat(state['last_post_date'])
            next_post = last_post + timedelta(days=2)
            print(f"Next post scheduled for: {next_post.strftime('%Y-%m-%d %H:%M:%S')}")
            return
        
        # Get the next tip in order
        tip = self.get_next_tip(state)

        # Add hashtags for better visibility (1-2 optimal for engagement)
        hashtags = self.get_hashtags(2)
        tweet_text = f"{tip}\n\n{' '.join(hashtags)}"

        # Post to X
        try:
            response = self.client.create_tweet(text=tweet_text)
            print(f"✅ Successfully posted: {tip}")
            print(f"   Hashtags: {' '.join(hashtags)}")
            print(f"Tweet ID: {response.data['id']}")
            
            # Update state
            state['last_post_date'] = datetime.now().isoformat()
            self.save_state(state)
            
        except tweepy.errors.Forbidden as e:
            print(f"❌ Error posting tweet: 403 Forbidden")
            print(f"Full error: {e}")
            print(f"API response: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            raise
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
            raise
    
    def run(self):
        """Main run method"""
        print("🤖 Bash Tip Bot Starting...")
        self.post_tip()


def main():
    try:
        bot = BashTipBot()
        bot.run()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    exit(main())
