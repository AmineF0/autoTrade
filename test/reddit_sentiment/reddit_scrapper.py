import requests
import time
import sys
from typing import Union, List, Dict, Any, Optional


class RedditScraper:
    """
    A simple class to fetch subreddit posts and comments from Reddit's
    (mostly) public JSON endpoints. Suitable for small-scale or personal
    usage. For production or large-scale usage, switch to an OAuth-based
    approach (e.g., PRAW).
    """

    def __init__(
        self,
        user_agent: str = "MyRedditApp/1.0 (by u/my_username)",
        max_pages: int = 2,
        sleep_time: float = 2.0
    ):
        """
        Initialize the RedditScraper.

        :param user_agent: Custom User-Agent string to identify your client.
        :param max_pages: Default number of 'pages' to paginate for posts.
        :param sleep_time: Pause (in seconds) between page fetches to avoid rate-limits.
        """
        self.user_agent = user_agent
        self.headers = {"User-Agent": self.user_agent}
        self.max_pages = max_pages
        self.sleep_time = sleep_time

    # ---------------------------------------------------------------------
    # (A) Fetching Subreddit Posts
    # ---------------------------------------------------------------------
    def fetch_subreddit_posts(
        self,
        subreddits: Union[str, List[str]],
        sort: str = "new",
        limit: int = 25,
        max_pages: Optional[int] = None,
        time_filter: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch posts from one or more subreddits. Supports pagination and time filtering.

        :param subreddits: A single subreddit (string) or list of subreddit names.
        :param sort: Sorting criterion (e.g., "new", "hot", "top", "rising", "controversial").
        :param limit: Number of posts to fetch per request (max ~100).
        :param max_pages: How many pages to fetch. Defaults to self.max_pages if None.
        :param time_filter: Time filter (valid if sort="top" or "controversial"), 
                            e.g., "day", "week", "month", "year".
        :return: Dictionary where key=subreddit, value=list of post data dicts.
        """
        if isinstance(subreddits, str):
            subreddits = [subreddits]  # Wrap in a list for uniform processing

        if max_pages is None:
            max_pages = self.max_pages

        results = {}
        for subreddit in subreddits:
            all_posts = []
            after = None

            for page in range(max_pages):
                print(f"Fetching page {page + 1} from r/{subreddit} ({sort}), time_filter={time_filter} ...")
                page_data = self._fetch_subreddit_page(
                    subreddit=subreddit,
                    sort=sort,
                    limit=limit,
                    after=after,
                    time_filter=time_filter
                )

                if not page_data:
                    # Something went wrong, or no posts returned
                    break

                all_posts.extend(page_data["posts"])
                after = page_data["after"]

                if not after:
                    # No more pagination
                    break

                # Sleep to respect rate limits
                time.sleep(self.sleep_time)

            results[subreddit] = all_posts

        return results

    # ---------------------------------------------------------------------
    # (B) Fetching Comments for a Specific Post
    # ---------------------------------------------------------------------
    def fetch_comments_for_post(
        self,
        subreddit: str,
        post_id: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch comments for a specific post in a subreddit.
        (Does not apply comment depth limitation here; see 'posts_and_comments_to_text'
         or your own logic to limit levels if needed.)

        :param subreddit: Subreddit name (e.g., "python").
        :param post_id: The base-36 ID of the post (e.g. "abc123").
        :return: List of parsed comments, including nested replies.
                 Note: Includes *all* comment levels. You may filter later if desired.
        """
        url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
        print(f"Fetching comments for post {post_id} in r/{subreddit} ...")

        try:
            response = requests.get(url, headers=self.headers)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []

        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code} for {url}")
            return []

        try:
            data = response.json()
        except ValueError:
            print("Error parsing JSON response.")
            return []

        # data[0] is post info, data[1] is the comment listing
        if len(data) < 2:
            return []

        comments_root = data[1]
        comments_list = comments_root.get("data", {}).get("children", [])
        parsed_comments = []

        for comment in comments_list:
            if comment.get("kind") == "t1":  # 't1' = comment
                parsed_comments.append(self._parse_comment(comment))

        return parsed_comments

    # ---------------------------------------------------------------------
    # (C) Fetching Both Posts and Comments (Subreddit-level)
    # ---------------------------------------------------------------------
    def fetch_posts_and_comments(
        self,
        subreddits: Union[str, List[str]],
        sort: str = "new",
        limit: int = 25,
        max_pages: Optional[int] = None,
        time_filter: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Convenience method to fetch posts from one or multiple subreddits,
        and then fetch comments for each post. Returns a fully nested structure.

        :param subreddits: A single subreddit (string) or list of subreddit names.
        :param sort: Sorting criterion (e.g., "new", "hot", "top", "rising", "controversial").
        :param limit: Number of posts to fetch per request.
        :param max_pages: How many pages to fetch (for each subreddit).
        :param time_filter: Time filter (valid if sort="top" or "controversial"), e.g., "day", "week", etc.
        :return: {
            "<subreddit>": [
                {
                    "id": <post_id>,
                    "title": "...",
                    "selftext": "...",
                    "comments": [ ... list of comments ... ],
                    ...
                },
                ...
            ],
            ...
        }
        """
        posts_dict = self.fetch_subreddit_posts(
            subreddits=subreddits,
            sort=sort,
            limit=limit,
            max_pages=max_pages,
            time_filter=time_filter
        )

        # Now, fetch comments for each post
        for subreddit, posts_list in posts_dict.items():
            for post_data in posts_list:
                post_id = post_data.get("id")
                if post_id:
                    comments = self.fetch_comments_for_post(subreddit, post_id)
                    post_data["comments"] = comments
                else:
                    post_data["comments"] = []

        return posts_dict

    # ---------------------------------------------------------------------
    # (D) Searching Within a Single Subreddit
    # ---------------------------------------------------------------------
    def search_subreddit_posts(
        self,
        subreddit: str,
        query: str,
        sort: str = "relevance",
        time_filter: Optional[str] = None,
        limit: int = 25
    ) -> List[Dict[str, Any]]:
        """
        Search a specific subreddit for posts matching a given query.

        :param subreddit: The name of the subreddit (e.g., "python").
        :param query: The search query string (e.g., "web scraping").
        :param sort: One of ['relevance', 'hot', 'top', 'new', 'comments'].
        :param time_filter: Filter posts by time ('hour', 'day', 'week', 'month', 'year', 'all').
        :param limit: Number of posts to fetch in one request (up to ~100).
        :return: A list of post data dicts.
        """
        base_url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            "q": query,
            "restrict_sr": "1",   # search only in this subreddit
            "sort": sort,
            "limit": limit
        }
        if time_filter:
            params["t"] = time_filter

        try:
            response = requests.get(base_url, headers=self.headers, params=params)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return []

        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code} for {base_url}")
            return []

        try:
            data = response.json()
        except ValueError:
            print("Error parsing JSON.")
            return []

        posts = []
        children = data.get("data", {}).get("children", [])
        for child in children:
            if child.get("kind") == "t3":
                post_info = child.get("data", {})
                posts.append(post_info)

        return posts

    # ---------------------------------------------------------------------
    # (E) Global (All-Reddit) Keyword Search
    # ---------------------------------------------------------------------
    def global_reddit_search(
        self,
        query: str,
        limit: int = 25,
        sort: str = "relevance",
        time_filter: str = "all",
        after: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Perform a keyword search across ALL of Reddit (unauthenticated).

        :param query: The search query (string).
        :param limit: Number of search results to fetch (max ~100 per request).
        :param sort: Sorting criterion: "relevance", "hot", "top", "new", "comments".
        :param time_filter: Time filter: "hour", "day", "week", "month", "year", "all".
        :param after: Pagination token for the next set of results.
        :return: A dict with 'results' (list of posts) and 'after' (token to get next page),
                 or None if an error occurs.
        """
        base_url = "https://www.reddit.com/search.json"
        params = {
            "q": query,
            "limit": limit,
            "sort": sort,
            "t": time_filter
        }
        if after:
            params["after"] = after

        try:
            response = requests.get(base_url, headers=self.headers, params=params)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None

        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            return None

        try:
            data = response.json()
        except ValueError:
            print("Error parsing JSON.")
            return None

        children = data.get("data", {}).get("children", [])
        results = []

        for child in children:
            if child.get("kind") == "t3":  # 't3' means it's a post
                post_data = child.get("data", {})
                results.append(post_data)

        after_token = data.get("data", {}).get("after", None)
        return {"results": results, "after": after_token}

    # ---------------------------------------------------------------------
    # (F) Search by Keywords, Fetch Comments, Return in Single Structure
    # ---------------------------------------------------------------------
    def search_keywords_and_get_posts_comments(
        self,
        query: str,
        limit: int = 25,
        sort: str = "relevance",
        time_filter: str = "all"
    ) -> List[Dict[str, Any]]:
        """
        Global search by keywords, then fetch comments for each post. 
        Returns a list of post dicts, each including "comments".

        :param query: The search query.
        :param limit: Max results (per fetch). For large numbers, consider paging.
        :param sort: "relevance", "hot", "top", "new", "comments".
        :param time_filter: "hour", "day", "week", "month", "year", "all".
        :return: A list of posts, each with a nested "comments" field.
        """
        print(f"Performing global search for '{query}', limit={limit}, sort={sort}, time_filter={time_filter}")
        # 1) Perform a single global search call (no pagination here; you can extend if needed).
        search_result = self.global_reddit_search(
            query=query,
            limit=limit,
            sort=sort,
            time_filter=time_filter
        )
        if not search_result:
            return []

        posts = search_result.get("results", [])
        # 2) For each post, fetch comments by subreddit/post_id
        for post in posts:
            subr = post.get("subreddit")
            pid = post.get("id")
            if subr and pid:
                # Fetch comments for each post
                comments = self.fetch_comments_for_post(subr, pid)
                post["comments"] = comments
            else:
                post["comments"] = []

        return posts

    # ---------------------------------------------------------------------
    # (G) Convert Posts (and Nested Comments) to a Single Text String
    # ---------------------------------------------------------------------
    def posts_and_comments_to_text(
        self,
        posts_data: List[Dict[str, Any]],
        max_comment_level: int = 999
    ) -> str:
        """
        Flatten/serialize a list of post dicts (each with nested comments)
        into a single large text string for easier saving or processing.

        :param posts_data: A list of post dicts, each with optional "comments" array.
        :param max_comment_level: The maximum depth of comment nesting to include.
                                  0 means no comments, 1 = only top-level, etc.
        :return: A single text string containing posts & comments.
        """
        lines = []
        for i, post in enumerate(posts_data, start=1):
            title = post.get("title", "[No Title]")
            selftext = post.get("selftext", "")
            lines.append(f"=== Post #{i} ===")
            lines.append(f"Title: {title}")
            lines.append(f"Body: {selftext}")

            # Convert comments to text, respecting max_comment_level
            comments_list = post.get("comments", [])
            if max_comment_level > 0 and comments_list:
                lines.append(f"--- Comments (Up to level {max_comment_level}) ---")
                for comment_str in self._flatten_comment_text(
                        comments_list, 
                        current_level=1, 
                        max_level=max_comment_level):
                    lines.append(comment_str)
            else:
                lines.append("--- No Comments (or Comments Suppressed) ---")

            lines.append("\n")  # Blank line after each post

        return "\n".join(lines)

    def _flatten_comment_text(
        self,
        comments: List[Dict[str, Any]],
        current_level: int,
        max_level: int
    ) -> List[str]:
        """
        Recursively flatten comment trees into a list of strings, respecting max_level.
        Skips comments where author="[deleted]" or body="[removed]".

        :param comments: List of comment dicts (each may have 'replies').
        :param current_level: Current nesting level in the comment tree.
        :param max_level: The maximum nesting level to include.
        :return: A list of comment lines (strings).
        """
        lines = []
        if current_level > max_level:
            return lines  # stop if we've exceeded desired depth

        indent = "  " * current_level  # Indentation for readability
        for c in comments:
            body = c.get("body", "[No text]")
            author = c.get("author", "[unknown]")
            if author == "[deleted]" or body == "[removed]":
                # Skip comments that are effectively removed or deleted
                continue

            # Include this comment
            lines.append(f"{indent}- (level {current_level}) Comment by {author}: {body}")

            replies = c.get("replies", [])
            if replies:
                # Recurse deeper if we haven't exceeded max_level
                lines.extend(
                    self._flatten_comment_text(
                        replies, 
                        current_level=current_level + 1, 
                        max_level=max_level
                    )
                )
        return lines

    # ---------------------------------------------------------------------
    #   Internal Helper Methods for Subreddit Pages & Parsing Comments
    # ---------------------------------------------------------------------
    def _fetch_subreddit_page(
        self,
        subreddit: str,
        sort: str,
        limit: int,
        after: Optional[str],
        time_filter: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single "page" (one HTTP request) of subreddit posts.
        Returns None if an error occurs or no data.

        :param subreddit: Name of the subreddit (e.g., "python").
        :param sort: Sorting criterion (e.g., "new", "hot", "top", "rising").
        :param limit: Number of posts per request (max ~100).
        :param after: Pagination token for next page.
        :param time_filter: Time filter if sort="top" or "controversial" (e.g. "day", "week", "month").
        """
        base_url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
        params = {"limit": limit}
        if after:
            params["after"] = after

        if time_filter:
            params["t"] = time_filter

        try:
            response = requests.get(base_url, headers=self.headers, params=params)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None

        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code} for {base_url}")
            return None

        try:
            data = response.json()
        except ValueError:
            print("Error parsing JSON response.")
            return None

        children = data.get("data", {}).get("children", [])
        posts = []

        for child in children:
            if child.get("kind") == "t3":  # 't3' = post
                post_info = child.get("data", {})
                posts.append(post_info)

        after_token = data.get("data", {}).get("after", None)
        return {
            "posts": posts,
            "after": after_token
        }

    def _parse_comment(self, comment_obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively parse a comment (and its replies) into a dictionary.
        (Does not skip "[deleted]" or "[removed]" here; skipping logic 
         is applied later in _flatten_comment_text.)
        """
        comment_data = comment_obj.get("data", {})
        comment_id = comment_data.get("id")
        comment_author = comment_data.get("author")
        comment_body = comment_data.get("body", "")
        created_utc = comment_data.get("created_utc", 0)

        # Recursively parse any replies
        replies_obj = comment_data.get("replies")
        nested_comments = []
        if isinstance(replies_obj, dict):  # sometimes 'replies' can be an empty string
            children = replies_obj.get("data", {}).get("children", [])
            for child in children:
                if child.get("kind") == "t1":
                    nested_comments.append(self._parse_comment(child))

        return {
            "comment_id": comment_id,
            "author": comment_author,
            "body": comment_body,
            "created_utc": created_utc,
            "replies": nested_comments,
        }


# ---------------------------------------------------------------------
# Example Usage / Test Cases
# ---------------------------------------------------------------------
if __name__ == "__main__":
    try:
        scraper = RedditScraper(
            user_agent="MyRedditApp/1.0 (by u/my_username)",
            max_pages=1,
            sleep_time=1.5
        )

        ##########
        print("=== Test 1: Single Subreddit (Fetch Posts Only) ===")
        single_sub_data = scraper.fetch_subreddit_posts(
            subreddits="NVDA_Stock",
            sort="top",
            time_filter="day",
            limit=3,
        )
        print(f"Fetched {len(single_sub_data['NVDA_Stock'])} posts from r/NVDA_Stock")
        for post in single_sub_data["NVDA_Stock"]:
            print(f" - {post.get('title')} (ID: {post.get('id')})")
        
        ##########
        print("\n=== Test 2: Multiple Subreddits (Fetch Posts + Comments) ===")
        multi_sub_data = scraper.fetch_posts_and_comments(
            subreddits=["nvidia", "NVDA_Stock"],
            sort="top",
            time_filter="day",
            limit=2,
            max_pages=1  # just 1 page each for brevity
        )
        for subr, posts in multi_sub_data.items():
            print(f"\nr/{subr}: {len(posts)} posts fetched.")
            for p in posts:
                print(f"  Title: {p.get('title')} => {len(p.get('comments', []))} comments")

        # ------------------------------------------
        # CORRECTION:
        # To generate combined text for ALL subreddits, first collect all posts in one list.
        # ------------------------------------------
        all_posts = []
        for subr, posts in multi_sub_data.items():
            all_posts.extend(posts)

        combined_text = scraper.posts_and_comments_to_text(all_posts, max_comment_level=2)
        print("\n--- Combined Text (Truncated for Demo) ---")
        print(combined_text[:1000], "... [TRUNCATED]")


        ##########
        print("\n=== Test 3: Single Subreddit Search ===")
        srch_results = scraper.search_subreddit_posts(
            subreddit="stocks",
            query="NVDA",
            sort="top",
            time_filter="week",
            limit=2
        )
        print(f"Found {len(srch_results)} posts in r/stocks about 'NVDA'")
        for i, post in enumerate(srch_results, start=1):
            print(f"   {i}. {post.get('title')} (score: {post.get('score')})")

        # You can flatten these search results into a single text as well:
        srch_text = scraper.posts_and_comments_to_text(srch_results, max_comment_level=2)
        print("\n--- Searched Posts Combined Text (Truncated) ---")
        print(srch_text[:1000], "... [TRUNCATED]")      


        ##########
        print("\n=== Test 4: Global Search ===")
        global_res = scraper.global_reddit_search(
            query="NVIDIA",
            limit=2,
            sort="relevance",
            time_filter="day"
        )
        if global_res:
            print(f"Fetched {len(global_res['results'])} global results about 'NVIDIA'")

        print("\n=== Test 5: Global Search, Fetch Comments, Flatten to Text (max_comment_level=2) ===")
        posts_with_comments = scraper.search_keywords_and_get_posts_comments(
            query="NVDA",
            limit=2,
            sort="relevance",
            time_filter="day"
        )
        
        # Now parse into a single text string, limiting to 2 levels of nested comments.
        final_text = scraper.posts_and_comments_to_text(posts_with_comments, max_comment_level=2)
        print("\n--- Final Combined Text (Truncated for Demo) ---")
        print(final_text[:1000], "... [TRUNCATED]")

    except KeyboardInterrupt:
        print("\nScript interrupted by user.")
        sys.exit(0)

