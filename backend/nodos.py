import requests
import json
import os
from datetime import datetime, timedelta
import random
from atproto import Client, models
from dotenv import load_dotenv
import re
from reskeets import fetch_reposts_data

# Load environment variables
load_dotenv()

class BlueSkyAnalyzer:
    def __init__(self):
        self.client = None
        self.authenticated = False
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Bluesky using credentials from .env file"""
        try:
            username = os.getenv('BLUESKY_USERNAME')
            password = os.getenv('BLUESKY_PASSWORD')
            
            if not username or not password:
                print("Warning: BLUESKY_USERNAME or BLUESKY_PASSWORD not found in .env file")
                return False
            
            self.client = Client()
            profile = self.client.login(username, password)
            self.authenticated = True
            print(f"Successfully authenticated as {profile.display_name or profile.handle}")
            return True
            
        except Exception as e:
            print(f"Authentication failed: {str(e)}")
            self.authenticated = False
            return False

# Global analyzer instance
analyzer = BlueSkyAnalyzer()

def analyze_post_propagation(post_url):
    """
    Analyze how a Bluesky post propagates through the network
    
    Args:
        post_url (str): URL of the Bluesky post to analyze
    
    Returns:
        dict: Graph data with nodes and edges for visualization
    """
    if not analyzer.authenticated:
        print("Not authenticated, returning mock data")
        return get_mock_data()
    
    try:
        # Extract post URI from URL
        print(f"Analyzing URL: {post_url}")
        post_uri = extract_post_uri(post_url)
        if not post_uri:
            print(f"Failed to extract post URI from {post_url}. Returning mock data.")
            return get_mock_data()
        
        print(f"Extracted Post URI: {post_uri}")
        # Get original post data
        original_post = get_post_data(post_uri)
        if not original_post:
            print(f"Failed to get original post data for {post_uri}. Returning mock data.")
            return get_mock_data()
        
        print(f"Successfully fetched original post by: {original_post.get('author')}")
        # Get interactions (replies, reposts, likes)
        interactions = get_post_interactions(post_uri, original_post, post_url)
        
        # Build graph structure
        graph_data = build_graph_data(original_post, interactions)
        
        return graph_data
    
    except Exception as e:
        print(f"Critical error in analyze_post_propagation for {post_url}: {str(e)}")
        return get_mock_data()

def extract_post_uri(post_url):
    """Extract AT Protocol URI from Bluesky URL"""
    try:
        # Example URL: https://bsky.app/profile/alice.bsky.social/post/3kb2c7qm4ts2s
        pattern = r'https://bsky\.app/profile/([^/]+)/post/([^/?]+)'
        match = re.match(pattern, post_url)
        
        if match:
            handle = match.group(1)
            post_id = match.group(2)
            
            print(f"Attempting to resolve handle: {handle}")
            # Convert handle to DID if needed
            try:
                profile_response = analyzer.client.get_profile(handle)
                did = profile_response.did
                # Construct AT Protocol URI
                post_uri = f"at://{did}/app.bsky.feed.post/{post_id}"
                return post_uri
            except Exception as e:
                print(f"Error resolving handle {handle} to DID: {e}")
                return None
        
        return None
    
    except Exception as e:
        print(f"Error extracting post URI: {e}")
        return None

def get_post_data(post_uri):
    """
    Get original post data from Bluesky API
    """
    try:
        # Get the post record
        print(f"Attempting to get post data for URI: {post_uri}")
        response = analyzer.client.get_posts([post_uri])
        
        if not response.posts:
            print(f"No posts found for URI: {post_uri}")
            return None
        
        post = response.posts[0]
        
        return {
            'id': post_uri,
            'author': post.author.handle,
            'author_display_name': post.author.display_name or post.author.handle,
            'text': post.record.text,
            'created_at': post.record.created_at,
            'metrics': {
                'replies': post.reply_count or 0,
                'reposts': post.repost_count or 0,
                'likes': post.like_count or 0
            },
            'uri': post.uri,
            'cid': post.cid
        }
    
    except Exception as e:
        print(f"Error getting post data for {post_uri}: {e}")
        return None

def get_post_interactions(post_uri, original_post, post_url):
    """
    Get all interactions for a post (replies, reposts)
    """
    interactions = []
    
    try:
        # Get replies to the post
        replies = get_post_replies(post_uri)
        interactions.extend(replies)
        
        # Get reposts of the post
        reposts = get_post_reposts(post_url)
        interactions.extend(reposts)
        
        # Limit to prevent overwhelming visualization
        return interactions[:1000]  # Limit to 50 interactions
    
    except Exception as e:
        print(f"Error getting interactions: {e}")
        return []

def get_post_replies(post_uri):
    """Get replies to a specific post"""
    replies = []
    
    try:
        # Search for replies to this post
        # Note: This is a simplified approach. In a full implementation,
        # you might need to use the feed API or search API more extensively
        
        # Get the post thread to find replies
        thread_response = analyzer.client.get_post_thread(post_uri)
        
        if hasattr(thread_response.thread, 'replies') and thread_response.thread.replies:
            for reply in thread_response.thread.replies[:1000]:  # Limit replies
                if hasattr(reply, 'post'):
                    reply_post = reply.post
                    replies.append({
                        'type': 'reply',
                        'id': reply_post.uri,
                        'author': reply_post.author.handle,
                        'author_display_name': reply_post.author.display_name or reply_post.author.handle,
                        'parent_id': post_uri,
                        'text': reply_post.record.text,
                        'created_at': reply_post.record.created_at,
                        'metrics': {
                            'replies': reply_post.reply_count or 0,
                            'reposts': reply_post.repost_count or 0,
                            'likes': reply_post.like_count or 0
                        }
                    })
                    
                    # Get nested replies (one level deep)
                    if hasattr(reply, 'replies') and reply.replies:
                        for nested_reply in reply.replies[:10]:  # Limit nested replies
                            if hasattr(nested_reply, 'post'):
                                nested_post = nested_reply.post
                                replies.append({
                                    'type': 'reply',
                                    'id': nested_post.uri,
                                    'author': nested_post.author.handle,
                                    'author_display_name': nested_post.author.display_name or nested_post.author.handle,
                                    'parent_id': reply_post.uri,
                                    'text': nested_post.record.text,
                                    'created_at': nested_post.record.created_at,
                                    'metrics': {
                                        'replies': nested_post.reply_count or 0,
                                        'reposts': nested_post.repost_count or 0,
                                        'likes': nested_post.like_count or 0
                                    }
                                })
    
    except Exception as e:
        print(f"Error getting replies: {e}")
    
    return replies

def get_post_reposts(post_url):
    """
    Replaces old get_post_reposts using direct HTTP logic from reskeets.
    Input: full Bluesky post URL
    Output: reposts_data[] matching legacy format
    """
    try:
        print(f"[get_post_reposts] Fetching reposts for: {post_url}")
        reposts_data = fetch_reposts_data(post_url)
        print(f"[get_post_reposts] Retrieved {len(reposts_data)} reposts.")
        return reposts_data
    except Exception as e:
        print(f"[get_post_reposts] Failed to fetch reposts: {e}")
        import traceback
        traceback.print_exc()
        return []

def build_graph_data(original_post, interactions):
    """
    Build graph data structure for D3.js visualization
    """
    nodes = []
    edges = []
    
    # Add original post as root node
    nodes.append({
        'id': original_post['id'],
        'label': original_post['author_display_name'],
        'handle': original_post['author'],
        'type': 'original',
        'text': original_post['text'][:150] + ('...' if len(original_post['text']) > 150 else ''),
        'full_text': original_post['text'],
        'metrics': original_post['metrics'],
        'size': max(20, min(40, 20 + (original_post['metrics']['reposts'] + original_post['metrics']['replies']) // 5)),
        'color': '#1DA1F2',
        'created_at': original_post['created_at']
    })
    
    # Add interaction nodes
    for interaction in interactions:
        node_size = 8
        node_color = '#17BF63'  # Green for replies
        
        if interaction['type'] == 'repost':
            node_color = '#E1306C'  # Pink for reposts
            node_size = 12
        
        # Adjust size based on engagement
        engagement = interaction['metrics']['replies'] + interaction['metrics']['reposts'] + interaction['metrics']['likes']
        node_size = max(node_size, min(25, node_size + engagement // 10))
        
        nodes.append({
            'id': interaction['id'],
            'label': interaction['author_display_name'],
            'handle': interaction['author'],
            'type': interaction['type'],
            'text': interaction.get('text', f"{interaction['type'].title()} by {interaction['author_display_name']}")[:150] + ('...' if interaction.get('text', '') and len(interaction.get('text', '')) > 150 else ''),
            'full_text': interaction.get('text', f"{interaction['type'].title()} by {interaction['author_display_name']}"),
            'metrics': interaction['metrics'],
            'size': node_size,
            'color': node_color,
            'created_at': interaction['created_at']
        })
        
        # Add edge from parent to this interaction
        edges.append({
            'source': interaction['parent_id'],
            'target': interaction['id'],
            'type': interaction['type']
        })
    
    # Calculate stats
    # For the summary stats panel, use the metrics from the original post itself,
    # as these reflect the total counts known by the Bluesky API for that post.
    # The 'interactions' list contains what will be visualized, which might be a limited subset.
    
    summary_reply_count = original_post['metrics'].get('replies', 0)
    summary_repost_count = original_post['metrics'].get('reposts', 0)
    
    # Total interactions for the panel can be the sum of total replies and reposts of the original post.
    summary_total_interactions = summary_reply_count + summary_repost_count
    
    return {
        'nodes': nodes,
        'edges': edges,
        'stats': {
            'total_nodes': len(nodes), # Total nodes actually visualized
            'total_interactions': summary_total_interactions, # Total interactions of the original post
            'replies': summary_reply_count, # Total replies to the original post
            'reposts': summary_repost_count # Total reposts of the original post
        },
        'original_post': {
            'author': original_post['author_display_name'],
            'text': original_post['text'],
            'created_at': original_post['created_at']
        }
    }

def get_mock_data():
    """
    Return mock data for demonstration purposes
    """
    now_iso = datetime.now().isoformat() + "Z"
    hour_ago_iso = (datetime.now() - timedelta(hours=1)).isoformat() + "Z"
    two_hours_ago_iso = (datetime.now() - timedelta(hours=2)).isoformat() + "Z"
    thirty_min_ago_iso = (datetime.now() - timedelta(minutes=30)).isoformat() + "Z"
    forty_five_min_ago_iso = (datetime.now() - timedelta(minutes=45)).isoformat() + "Z"
    fifteen_min_ago_iso = (datetime.now() - timedelta(minutes=15)).isoformat() + "Z"

    return {
        'nodes': [
            {
                'id': 'original',
                'label': 'alice.bsky.social',
                'handle': 'alice.bsky.social',
                'type': 'original',
                'text': 'Just launched my new project! Excited to share it with everyone.',
                'full_text': 'Just launched my new project! Excited to share it with everyone. This is the full text of the original post.',
                'metrics': {'replies': 2, 'reposts': 1, 'likes': 10},
                'size': 20,
                'color': '#1DA1F2',
                'created_at': two_hours_ago_iso
            },
            {
                'id': 'reply_1',
                'label': 'bob.bsky.social',
                'handle': 'bob.bsky.social',
                'type': 'reply',
                'text': 'Congratulations! This looks amazing.',
                'full_text': 'Congratulations! This looks amazing. Hope it goes well for you, Alice!',
                'metrics': {'replies': 1, 'reposts': 0, 'likes': 5},
                'size': 12,
                'color': '#17BF63',
                'created_at': hour_ago_iso
            },
            {
                'id': 'reply_2',
                'label': 'carol.bsky.social',
                'handle': 'carol.bsky.social',
                'type': 'reply',
                'text': 'Great work on this!',
                'full_text': 'Great work on this! Looking forward to trying it out.',
                'metrics': {'replies': 0, 'reposts': 0, 'likes': 3},
                'size': 10,
                'color': '#17BF63',
                'created_at': thirty_min_ago_iso
            },
            {
                'id': 'repost_1_dave.bsky.social', # More unique ID for reposts
                'label': 'dave.bsky.social',
                'handle': 'dave.bsky.social',
                'type': 'repost',
                'text': 'Repost by dave.bsky.social',
                'full_text': 'Repost by dave.bsky.social',
                'metrics': {'replies': 0, 'reposts': 0, 'likes': 0}, # Reposts don't have their own metrics
                'size': 10, # Standard size for repost
                'color': '#E1306C', # Repost color consistent with build_graph_data
                'created_at': forty_five_min_ago_iso
            },
            {
                'id': 'reply_1_1', # Reply to reply_1
                'label': 'eve.bsky.social',
                'handle': 'eve.bsky.social',
                'type': 'reply',
                'text': 'I agree, really impressive!',
                'full_text': 'I agree, really impressive! Bob, you are right.',
                'metrics': {'replies': 0, 'reposts': 0, 'likes': 2},
                'size': 8,
                'color': '#17BF63',
                'created_at': fifteen_min_ago_iso
            }
        ],
        'edges': [
            {'source': 'original', 'target': 'reply_1', 'type': 'reply'},
            {'source': 'original', 'target': 'reply_2', 'type': 'reply'},
            {'source': 'original', 'target': 'repost_1_dave.bsky.social', 'type': 'repost'},
            {'source': 'reply_1', 'target': 'reply_1_1', 'type': 'reply'}
        ],
        'stats': {
            'total_nodes': 5,
            'total_interactions': 4,
            'replies': 3,
            'reposts': 1
        },
        'original_post': {
            'author': 'alice.bsky.social',
            'text': 'Just launched my new project! Excited to share it with everyone. This is the full text of the original post.',
            'created_at': two_hours_ago_iso
        }
    }