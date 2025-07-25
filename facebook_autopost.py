Automated Facebook Page poster for the Nomad Ov3rland brand.

This script uses the Facebook Graph API to post a photo and caption to a
Facebook Page on a recurring schedule.  Posts are created every Monday and
Thursday at 9:00 AM Pacific time (America/Los_Angeles).  The message
template includes hashtags and a mention to the Nomad Ov3rland account,
and attaches an image and link for the brand’s top‑selling product.

To use this script you need:

  • A Facebook Page access token with the permissions
    `pages_show_list`, `pages_read_engagement` and `pages_manage_posts`.
    The preceding steps in this task describe how to generate such
    a token via the Graph API Explorer.  Once you have the token,
    update the `PAGE_ACCESS_TOKEN` constant below.

  • The numeric ID of your Facebook Page.  You can find this in the
    Page’s About section or by visiting the page and noting the
    number at the end of the URL.  Update the `PAGE_ID` constant
    accordingly.

  • A publicly accessible image URL and a link to the product you
    want to promote.  Update `IMAGE_URL` and `PRODUCT_LINK` below
    to point to your content.

Save the updated script and run it continuously from a system that
remains online.  For example, you can start it in a background
terminal or use a process manager like systemd.  The script uses
the `schedule` library for scheduling and `requests` for HTTP calls.
Install dependencies via pip if needed:

    pip install requests schedule pytz

Note: The Facebook Page access token expires after about 60 days.
Regenerate a new token periodically and update `PAGE_ACCESS_TOKEN` to
avoid authentication errors.


import datetime
import os
import time

import pytz
import requests
import schedule


# -----------------------------------------------------------------------------
# Configuration – replace the placeholder values below with your own.

# Your Facebook Page ID (a numeric string).  Example: "123456789012345".
PAGE_ID = os.environ.get("FB_PAGE_ID", "YOUR_PAGE_ID_HERE")

# A Page access token generated from the Graph API Explorer.  It must
# include the pages_show_list, pages_read_engagement and pages_manage_posts
# permissions.  Keep this token secret.  You can also set it via the
# FB_PAGE_TOKEN environment variable to avoid hard‑coding secrets.
PAGE_ACCESS_TOKEN = os.environ.get("FB_PAGE_TOKEN", "YOUR_PAGE_ACCESS_TOKEN_HERE")

# URL of the product image.  The image must be publicly accessible.
IMAGE_URL = os.environ.get("PRODUCT_IMAGE_URL", "https://example.com/path/to/your-image.jpg")

# Link to the product page on your site.  This link will be appended to
# the caption so people can click through and purchase the product.
PRODUCT_LINK = os.environ.get("PRODUCT_LINK", "https://example.com/your-product-page")

# Base caption template.  You can customise the wording here.  The
# hashtags and mention are included as requested.  The product link is
# appended automatically when sending the post.
CAPTION_TEMPLATE = (
    "🔥 Ready to elevate your style? Check out our top‑selling product! "
    "#nomadoverland #streetwear #overlandstyle @nomadov3rland"
)


def post_photo_to_facebook(image_url: str, caption: str) -> None:
    """Upload a photo with a caption to the Facebook Page.

    Args:
        image_url: Publicly accessible URL of the image to post.
        caption: Text to accompany the photo.  This may include
                 hashtags and mentions.

    The function prints the response from Facebook for logging
    purposes.  In production you might want to send these logs to a
    file or monitoring system instead.
    """
    endpoint = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
    payload = {
        "url": image_url,
        "caption": caption,
        "access_token": PAGE_ACCESS_TOKEN,
    }
    try:
        response = requests.post(endpoint, data=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"[Error] Failed to post to Facebook: {exc}")
        return

    try:
        data = response.json()
    except Exception:
        data = response.text
    print(f"[Facebook] Response: {data}")


def create_scheduled_post() -> None:
    """Compose and send the scheduled post.

    The caption is built from the template and includes the
    PRODUCT_LINK on a separate line to encourage clicks.
    """
    caption = f"{CAPTION_TEMPLATE}\n{PRODUCT_LINK}"
    print(
        f"[Info] Posting scheduled content at {datetime.datetime.now().isoformat()}"
    )
    post_photo_to_facebook(IMAGE_URL, caption)


def schedule_posts() -> None:
    """Configure the schedule for Monday and Thursday at 09:00 PT."""
    # Use schedule.every().day.at() with a lambda that checks the weekday.
    # Python’s schedule library operates in the system’s local timezone.
    # Ensure the host running this script has its timezone set to
    # America/Los_Angeles, or adjust the time accordingly.
    def job_wrapper():
        tz = pytz.timezone("America/Los_Angeles")
        now = datetime.datetime.now(tz)
        if now.weekday() in (0, 3):  # 0=Monday, 3=Thursday
            create_scheduled_post()
        else:
            # Not a scheduled day; ignore.
            pass

    # Schedule to run every day at 09:00 local time.  The wrapper will
    # filter out days that are not Monday or Thursday.
    schedule.every().day.at("09:00").do(job_wrapper)


def main() -> None:
    """Entry point: set up the schedule and run indefinitely."""
    # Basic sanity checks for configuration.
    if not PAGE_ID or PAGE_ID == "YOUR_PAGE_ID_HERE":
        raise ValueError(
            "Facebook PAGE_ID is not set.  Update the PAGE_ID constant "
            "or set the FB_PAGE_ID environment variable."
        )
    if not PAGE_ACCESS_TOKEN or PAGE_ACCESS_TOKEN == "YOUR_PAGE_ACCESS_TOKEN_HERE":
        raise ValueError(
            "Facebook PAGE_ACCESS_TOKEN is not set.  Update the PAGE_ACCESS_TOKEN "
            "constant or set the FB_PAGE_TOKEN environment variable."
        )
    if not IMAGE_URL or IMAGE_URL.startswith("http") is False:
        raise ValueError(
            "IMAGE_URL must be a publicly accessible URL to your product image."
        )

    schedule_posts()
    print("[Info] Scheduler started. Waiting for scheduled times...")
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
