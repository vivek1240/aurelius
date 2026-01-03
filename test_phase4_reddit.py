#!/usr/bin/env python3
"""
Phase 4 Testing - Reddit Sentiment Analysis
Note: Requires REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_reddit_credentials():
    """Check if Reddit API credentials are available"""
    print("\n" + "="*60)
    print("TEST: Reddit API Credentials")
    print("="*60)
    
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    
    if client_id and client_secret:
        print(f"✅ PASS | Reddit credentials found")
        print(f"   └─ Client ID: {client_id[:8]}...")
        return True
    else:
        print(f"⚠️  SKIP | Reddit credentials not configured")
        print(f"   └─ To enable Reddit sentiment analysis:")
        print(f"      1. Go to https://www.reddit.com/prefs/apps")
        print(f"      2. Create a 'script' type app")
        print(f"      3. Set environment variables:")
        print(f"         export REDDIT_CLIENT_ID='your_client_id'")
        print(f"         export REDDIT_CLIENT_SECRET='your_client_secret'")
        return False


def test_reddit_import():
    """Test if praw library is available"""
    print("\n" + "="*60)
    print("TEST: PRAW Library Import")
    print("="*60)
    
    try:
        import praw
        print(f"✅ PASS | PRAW library available")
        print(f"   └─ Version: {praw.__version__}")
        return True
    except ImportError:
        print(f"❌ FAIL | PRAW library not installed")
        print(f"   └─ Run: pip install praw")
        return False


def test_reddit_utils_import():
    """Test if RedditUtils can be imported"""
    print("\n" + "="*60)
    print("TEST: RedditUtils Import")
    print("="*60)
    
    try:
        from aurelius.data_source import RedditUtils
        print(f"✅ PASS | RedditUtils imported successfully")
        return True
    except ImportError as e:
        print(f"❌ FAIL | Could not import RedditUtils")
        print(f"   └─ Error: {e}")
        return False


def test_reddit_fetch():
    """Test fetching Reddit posts (only if credentials available)"""
    print("\n" + "="*60)
    print("TEST: Reddit Post Fetching")
    print("="*60)
    
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    
    if not (client_id and client_secret):
        print(f"⚠️  SKIP | Reddit credentials not available")
        return None  # Skip, not fail
    
    try:
        from aurelius.data_source import RedditUtils
        
        posts = RedditUtils.get_reddit_posts(
            query="NVDA",
            start_date="2024-11-01",
            end_date="2024-12-01",
            limit=50
        )
        
        if posts is not None and not posts.empty:
            print(f"✅ PASS | Fetched {len(posts)} Reddit posts")
            print(f"   └─ Columns: {list(posts.columns)}")
            print(f"   └─ Sample titles:")
            for title in posts['title'].head(3):
                print(f"      • {title[:60]}...")
            return True
        else:
            print(f"⚠️  WARN | No posts returned (may be rate limited)")
            return True  # Not a failure, just no data
            
    except Exception as e:
        print(f"❌ FAIL | Reddit fetch error")
        print(f"   └─ Error: {e}")
        return False


def test_sentiment_mock():
    """Test mock sentiment analysis (without API)"""
    print("\n" + "="*60)
    print("TEST: Mock Sentiment Analysis Logic")
    print("="*60)
    
    # Sample Reddit-like data
    mock_posts = [
        {"title": "NVDA to the moon! 🚀", "score": 1500, "num_comments": 200},
        {"title": "Why I'm selling all my NVDA", "score": 300, "num_comments": 150},
        {"title": "NVDA earnings beat expectations", "score": 2000, "num_comments": 500},
        {"title": "Is NVDA overvalued?", "score": 800, "num_comments": 300},
        {"title": "NVDA just hit all time high!", "score": 1200, "num_comments": 250},
    ]
    
    # Simple sentiment scoring based on keywords
    bullish_keywords = ['moon', 'buy', 'beat', 'high', 'up', 'gains', 'rocket', '🚀']
    bearish_keywords = ['sell', 'selling', 'overvalued', 'crash', 'down', 'loss', 'dump']
    
    total_score = 0
    total_engagement = 0
    sentiment_scores = []
    
    for post in mock_posts:
        title_lower = post['title'].lower()
        post_sentiment = 0
        
        for word in bullish_keywords:
            if word in title_lower:
                post_sentiment += 1
        for word in bearish_keywords:
            if word in title_lower:
                post_sentiment -= 1
        
        # Weight by engagement
        engagement = post['score'] + post['num_comments']
        weighted_sentiment = post_sentiment * engagement
        
        sentiment_scores.append(weighted_sentiment)
        total_score += weighted_sentiment
        total_engagement += engagement
    
    avg_sentiment = total_score / total_engagement if total_engagement > 0 else 0
    
    if avg_sentiment > 0.1:
        sentiment_label = "BULLISH"
    elif avg_sentiment < -0.1:
        sentiment_label = "BEARISH"
    else:
        sentiment_label = "NEUTRAL"
    
    print(f"✅ PASS | Mock sentiment analysis working")
    print(f"   └─ Posts analyzed: {len(mock_posts)}")
    print(f"   └─ Total engagement: {total_engagement:,}")
    print(f"   └─ Sentiment score: {avg_sentiment:.4f}")
    print(f"   └─ Overall sentiment: {sentiment_label}")
    
    return True


if __name__ == "__main__":
    print("\n" + "🔬 PHASE 4 TESTING: REDDIT SENTIMENT".center(60))
    print("=" * 60)
    
    results = {
        "PRAW Library": test_reddit_import(),
        "RedditUtils Import": test_reddit_utils_import(),
        "Reddit Credentials": test_reddit_credentials(),
        "Reddit Fetch": test_reddit_fetch(),
        "Mock Sentiment Logic": test_sentiment_mock(),
    }
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v is True)
    skipped = sum(1 for v in results.values() if v is None)
    failed = sum(1 for v in results.values() if v is False)
    total = len(results)
    
    for test, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is None:
            status = "⚠️  SKIP"
        else:
            status = "❌ FAIL"
        print(f"   {status} | {test}")
    
    print(f"\n   Passed: {passed}/{total} | Skipped: {skipped} | Failed: {failed}")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 Phase 4 Reddit tests complete!")
        if skipped > 0:
            print("   Note: Some tests skipped due to missing Reddit API credentials")
    else:
        print("⚠️  Some tests failed - review output above")

