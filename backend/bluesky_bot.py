import json
from datetime import datetime
import os, requests
from typing import List, Dict, Optional

class BlueskyBot:
    def __init__(self, username: str, password: str):
        """
        Initialize the Bluesky bot with credentials
        
        Args:
            username: Bluesky username (e.g., 'pp701bot.bsky.social')
            password: App password for the account
        """
        self.username = username
        self.password = password
        self.session = None
        self.base_url = "https://bsky.social/xrpc"
        
        # Default contact list - you can modify this or load from a file
        self.contact_list = [
            "did:plc:example1",  # Replace with actual DIDs
            "did:plc:example2",  # Replace with actual DIDs
            # Add more contacts as needed
        ]
    
    def authenticate(self) -> bool:
        """
        Authenticate with Bluesky and get session token
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            auth_url = f"{self.base_url}/com.atproto.server.createSession"
            auth_data = {
                "identifier": self.username,
                "password": self.password
            }
            
            response = requests.post(auth_url, json=auth_data)
            
            if response.status_code == 200:
                self.session = response.json()
                print(f"✅ Authentication successful for {self.username}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def get_user_did(self, handle: str) -> Optional[str]:
        """
        Get DID (Decentralized Identifier) for a given handle
        
        Args:
            handle: Bluesky handle (e.g., 'user.bsky.social')
            
        Returns:
            str: DID if found, None otherwise
        """
        try:
            resolve_url = f"{self.base_url}/com.atproto.identity.resolveHandle"
            params = {"handle": handle}
            
            response = requests.get(resolve_url, params=params)
            
            if response.status_code == 200:
                return response.json().get("did")
            else:
                print(f"❌ Failed to resolve handle {handle}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error resolving handle {handle}: {str(e)}")
            return None
    
    def get_handle_from_did(self, did: str) -> Optional[str]:
        """
        Get handle from DID (reverse lookup)
        
        Args:
            did: DID to resolve
            
        Returns:
            str: Handle if found, None otherwise
        """
        try:
            # This is a workaround since there's no direct reverse lookup API
            # We'll need to maintain a mapping or use the profile API
            describe_url = f"{self.base_url}/com.atproto.repo.describeRepo"
            params = {"repo": did}
            
            response = requests.get(describe_url, params=params)
            
            if response.status_code == 200:
                repo_data = response.json()
                return repo_data.get("handle")
            else:
                print(f"❌ Failed to get handle for DID {did}: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting handle for DID {did}: {str(e)}")
            return None
    
    def post_message_with_mentions(self, message: str, contact_dids: List[str]) -> bool:
        """
        Post a public message mentioning all contacts
        
        Args:
            message: Message content
            contact_dids: List of DIDs to mention
            
        Returns:
            bool: True if post successful, False otherwise
        """
        if not self.session:
            print("❌ Not authenticated. Please authenticate first.")
            return False
        
        try:
            # Get handles for all DIDs
            mentions = []
            mention_handles = []
            
            for did in contact_dids:
                handle = self.get_handle_from_did(did)
                if handle:
                    mentions.append(f"@{handle}")
                    mention_handles.append(handle)
                else:
                    print(f"⚠️ Could not resolve DID to handle: {did}")
            
            if not mentions:
                print("❌ No valid handles found for mentions")
                return False
            
            # Create the post text with mentions
            mentions_text = " ".join(mentions)
            full_message = f"{mentions_text}\n\n{message}"
            
            # Create facets for mentions
            facets = []
            byte_start = 0
            
            for i, handle in enumerate(mention_handles):
                mention_text = f"@{handle}"
                byte_end = byte_start + len(mention_text.encode('utf-8'))
                
                facets.append({
                    "index": {
                        "byteStart": byte_start,
                        "byteEnd": byte_end
                    },
                    "features": [{
                        "$type": "app.bsky.richtext.facet#mention",
                        "did": contact_dids[i]
                    }]
                })
                
                byte_start = byte_end + 1  # +1 for space
            
            # Post with mentions
            post_url = f"{self.base_url}/com.atproto.repo.createRecord"
            
            headers = {
                "Authorization": f"Bearer {self.session['accessJwt']}",
                "Content-Type": "application/json"
            }
            
            record = {
                "$type": "app.bsky.feed.post",
                "text": full_message,
                "facets": facets,
                "createdAt": datetime.now().isoformat() + "Z"
            }
            
            post_data = {
                "repo": self.session["did"],
                "collection": "app.bsky.feed.post",
                "record": record
            }
            
            response = requests.post(post_url, json=post_data, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ Post with mentions created successfully")
                return True
            else:
                print(f"❌ Failed to create post with mentions: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating post with mentions: {str(e)}")
            return False 
    
    def post_public_message(self, message: str) -> bool:
        """
        Post a public message (skeet) to Bluesky
        
        Args:
            message: Message content
            
        Returns:
            bool: True if post successful, False otherwise
        """
        if not self.session:
            print("❌ Not authenticated. Please authenticate first.")
            return False
        
        try:
            post_url = f"{self.base_url}/com.atproto.repo.createRecord"
            
            headers = {
                "Authorization": f"Bearer {self.session['accessJwt']}",
                "Content-Type": "application/json"
            }
            
            record = {
                "$type": "app.bsky.feed.post",
                "text": message,
                "createdAt": datetime.now().isoformat() + "Z"
            }
            
            post_data = {
                "repo": self.session["did"],
                "collection": "app.bsky.feed.post",
                "record": record
            }
            
            response = requests.post(post_url, json=post_data, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ Public post created successfully")
                return True
            else:
                print(f"❌ Failed to create post: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating post: {str(e)}")
            return False
    
    def broadcast_message(self, message: str, include_public_post: bool = False) -> Dict[str, int]:
        """
        Broadcast message by mentioning all contacts in a single post
        
        Args:
            message: Message content
            include_public_post: Whether to also post without mentions (separate post)
            
        Returns:
            dict: Results summary with success/failure counts
        """
        if not self.session:
            if not self.authenticate():
                return {"success": 0, "failed": 0, "total": 0}
        
        results = {"success": 0, "failed": 0, "total": len(self.contact_list)}
        
        if not self.contact_list:
            print("⚠️ No contacts in contact list")
            return results
        
        # Post message with mentions to all contacts
        if self.post_message_with_mentions(message, self.contact_list):
            results["success"] = len(self.contact_list)
            print(f"✅ Successfully mentioned {len(self.contact_list)} contacts in post")
        else:
            results["failed"] = len(self.contact_list)
            print(f"❌ Failed to create post with mentions")
        
        # Optionally post separately without mentions
        if include_public_post:
            if self.post_public_message(message):
                print("✅ Message also posted publicly (without mentions)")
            else:
                print("❌ Failed to post publicly")
        
        print(f"📊 Broadcast complete: {results['success']}/{results['total']} contacts mentioned successfully")
        return results
    
    def add_contact_by_handle(self, handle: str) -> bool:
        """
        Add a new contact to the contact list by handle (easier method)
        
        Args:
            handle: Bluesky handle to add
            
        Returns:
            bool: True if contact added successfully
        """
        did = self.get_user_did(handle)
        if did:
            if did not in self.contact_list:
                self.contact_list.append(did)
                print(f"✅ Added {handle} ({did}) to contact list")
                return True
            else:
                print(f"ℹ️ {handle} is already in the contact list")
                return True
        else:
            print(f"❌ Could not resolve handle {handle}")
            return False
    
    def add_contact_by_did(self, did: str) -> bool:
        """
        Add a new contact to the contact list by DID directly
        
        Args:
            did: DID to add
            
        Returns:
            bool: True if contact added successfully
        """
        if did not in self.contact_list:
            # Verify the DID exists
            handle = self.get_handle_from_did(did)
            if handle:
                self.contact_list.append(did)
                print(f"✅ Added {handle} ({did}) to contact list")
                return True
            else:
                print(f"❌ Could not verify DID {did}")
                return False
        else:
            print(f"ℹ️ DID {did} is already in the contact list")
            return True
    
    def remove_contact(self, handle: str) -> bool:
        """
        Remove a contact from the contact list by handle
        
        Args:
            handle: Bluesky handle to remove
            
        Returns:
            bool: True if contact removed successfully
        """
        did = self.get_user_did(handle)
        if did and did in self.contact_list:
            self.contact_list.remove(did)
            print(f"✅ Removed {handle} from contact list")
            return True
        else:
            print(f"❌ {handle} not found in contact list")
            return False
    
    def save_contact_list(self, filename: str = "contacts.json"):
        """
        Save contact list to a JSON file
        
        Args:
            filename: Name of the file to save contacts
        """
        try:
            with open(filename, 'w') as f:
                json.dump(self.contact_list, f, indent=2)
            print(f"✅ Contact list saved to {filename}")
        except Exception as e:
            print(f"❌ Error saving contact list: {str(e)}")
    
    def load_contact_list(self, filename: str = "contacts.json"):
        """
        Load contact list from a JSON file
        
        Args:
            filename: Name of the file to load contacts from
        """
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    self.contact_list = json.load(f)
                print(f"✅ Contact list loaded from {filename}")
            else:
                print(f"ℹ️ Contact file {filename} not found, using default list")
        except Exception as e:
            print(f"❌ Error loading contact list: {str(e)}")


# Example usage and testing
if __name__ == "__main__":
    # Initialize bot
    bot = BlueskyBot(
        username="pp701bot.bsky.social",
        password="your-app-password-here"  # Replace with your actual app password
    )
    
    # Add the contact you mentioned
    bot.contact_list = ["did:plc:d4ibgn5c7th5ah3rdmtsqqti"]
    
    # Authenticate
    if bot.authenticate():
        # Test message
        test_message = "🤖 Test message from Guardián IA bot! This is a test of the trazabilidad system."
        
        # Broadcast message (this will now mention the contact in a single post)
        results = bot.broadcast_message(test_message, include_public_post=False)
        
        print(f"Results: {results}")
    else:
        print("Authentication failed. Please check your credentials.")