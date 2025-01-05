import re
import json
from typing import List, Dict, Optional

class RedditParser:
    def __init__(self, text: str):
        self.text = text
        self.posts = []

    def extract_comments(self, comment_section: str) -> List[Dict]:
        """
        Extract comments from a comment section.
        Returns a list of comment dictionaries with level, author, and content.
        """
        comments = []
        comment_pattern = r'\(level (\d+)\) Comment by (\w+): (.*?)(?=(?:\n  - \(level|\Z))'
        
        for match in re.finditer(comment_pattern, comment_section, re.DOTALL):
            level = int(match.group(1))
            author = match.group(2)
            content = self.clean_text(match.group(3))
            
            comment = {
                'level': level,
                'author': author,
                'content': content,
                'replies': []  # Will be populated for nested comments
            }
            comments.append(comment)

        # Organize comments into a tree structure
        comment_tree = []
        comment_stack = []
        
        for comment in comments:
            while comment_stack and comment['level'] <= comment_stack[-1]['level']:
                comment_stack.pop()
                
            if comment_stack:
                comment_stack[-1]['replies'].append(comment)
            else:
                comment_tree.append(comment)
                
            comment_stack.append(comment)

        return comment_tree

    def extract_posts(self) -> List[Dict]:
        """
        Extract posts and their comments from the text.
        Returns a list of dictionaries containing post information and comments.
        """
        # Split the text into sections based on "=== Post"
        post_sections = re.split(r'=== Post #\d+ ===', self.text)
        
        # Remove any empty sections
        post_sections = [section.strip() for section in post_sections if section.strip()]

        for section in post_sections:
            post_data = {}
            
            # Extract title
            title_match = re.search(r'Title: (.*?)(?:\nBody:|$)', section, re.DOTALL)
            if title_match:
                post_data['title'] = title_match.group(1).strip()

            # Extract body
            body_match = re.search(r'Body: (.*?)(?:---|\Z)', section, re.DOTALL)
            if body_match:
                post_data['body'] = body_match.group(1).strip()
            else:
                post_data['body'] = ""

            # Extract subreddit
            subreddit_match = re.search(r'(?:from|in) r/(\w+)', section)
            if subreddit_match:
                post_data['subreddit'] = subreddit_match.group(1)
            else:
                # If no subreddit found in the section, try to find it in the larger context
                subreddit_match = re.search(r'(?:from|in) r/(\w+)', self.text)
                if subreddit_match:
                    post_data['subreddit'] = subreddit_match.group(1)
                else:
                    post_data['subreddit'] = "unknown"

            # Extract comments
            comments_section_match = re.search(r'--- Comments \(Up to level \d+\) ---\n(.*?)(?=(?:\n===|\Z))', section, re.DOTALL)
            if comments_section_match:
                comments_text = comments_section_match.group(1)
                post_data['comments'] = self.extract_comments(comments_text)
            else:
                post_data['comments'] = []

            if post_data.get('title'):  # Only add if we at least have a title
                self.posts.append(post_data)

        return self.posts

    def clean_text(self, text: str) -> str:
        """Clean the text by removing extra whitespace and special characters."""
        if not text:
            return ""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove any special Reddit formatting
        text = re.sub(r'\[\w+\]|\(http[s]?://[^\)]+\)', '', text)
        return text.strip()

    def process_and_save(self) -> None:
        """
        Process the text and save the results to a JSON file.
        """
        # Extract and clean the posts
        posts = self.extract_posts()
        
        # Clean the text in each post
        for post in posts:
            post['title'] = self.clean_text(post['title'])
            post['body'] = self.clean_text(post['body'])

        return {
            'posts': posts
        }
