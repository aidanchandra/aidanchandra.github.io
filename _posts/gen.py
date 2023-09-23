import os
import sys
from datetime import datetime

def generate_jekyll_blog_header(blog_name):
    # Get the current date and time
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    # Create a filename based on the blog name and current date
    # Replacing spaces with underscores
    sanitized_blog_name = blog_name.replace(' ', '_').lower()
    filename = f"{date_str}-{sanitized_blog_name}.md"

    # Create the Jekyll header content
    header = f"""---
layout: post
title:  "{blog_name}"
date:   {date_str} {time_str}
categories: [category]
---

"""

    # Write the header to the file
    with open(filename, "w") as f:
        f.write(header)

    print(f"Blog header generated in file: {filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <blog_name>")
    else:
        blog_name = sys.argv[1]
        generate_jekyll_blog_header(blog_name)