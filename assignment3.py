import argparse
import requests
import csv
import re
from collections import Counter
from datetime import datetime
from io import StringIO

def download_file(url):
    "Downloads the log file from the given URL"
    response = requests.get(url)
    response.raise_for_status()
    return response.text  # Return file content as a string

def process_file(file_content):
    "Parses the CSV log file and returns a list of records"
    logs = []
    csv_reader = csv.reader(StringIO(file_content))
    
    for row in csv_reader:
        if len(row) != 5:
            continue  # Skip malformed lines
        path, timestamp, user_agent, status, size = row
        logs.append({
            "path": path,
            "timestamp": timestamp,
            "user_agent": user_agent,
            "status": int(status),
            "size": int(size),
        })
    
    return logs

def count_image_requests(logs):
    "Counts image requests and calculates the percentage of total requests"
    image_pattern = re.compile(r'\.(jpg|gif|png)$', re.IGNORECASE)
    total_requests = len(logs)
    image_requests = sum(1 for log in logs if image_pattern.search(log["path"]))
    
    percentage = (image_requests / total_requests) * 100 if total_requests > 0 else 0
    print(f"Image requests account for {percentage:.1f}% of all requests")

def most_popular_browser(logs):
    "Determines the most used browser"
    browser_patterns = {
        "Firefox": re.compile(r"Firefox"),
        "Chrome": re.compile(r"Chrome"),
        "Internet Explorer": re.compile(r"MSIE|Trident"),
        "Safari": re.compile(r"Safari(?!.*Chrome)"),
    }

    browser_counts = Counter()

    for log in logs:
        user_agent = log["user_agent"]
        for browser, pattern in browser_patterns.items():
            if pattern.search(user_agent):
                browser_counts[browser] += 1
                break

    most_common = browser_counts.most_common(1)
    if most_common:
        print(f"The most popular browser is {most_common[0][0]} with {most_common[0][1]} requests")

def requests_by_hour(logs):
    "Counts requests by hour and prints them sorted"
    hour_counts = Counter()

    for log in logs:
        hour = datetime.strptime(log["timestamp"], "%Y-%m-%d %H:%M:%S").hour
        hour_counts[hour] += 1

    for hour, count in sorted(hour_counts.items()):
        print(f"Hour {hour:02d} has {count} hits")

def main(url):
    """Main function to execute all tasks."""
    print(f"Downloading file from {url}...")
    file_content = download_file(url)
    
    print("Processing file...")
    logs = process_file(file_content)
    
    print("Analyzing data...")
    count_image_requests(logs)
    most_popular_browser(logs)
    requests_by_hour(logs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="URL to the datafile", type=str, required=True)
    args = parser.parse_args()
    main(args.url)


    
