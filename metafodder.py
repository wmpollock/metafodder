
# Bill Pollock
# 2019

import clean_filename, feedparser, re, sys


def process_feed(feed_url):
    rss_playlist = feedparser.parse(feed_url)

    # Strip out the additional branding on our OG title.
    list_title = rss_playlist.feed.title.split(" | ")[0]
    print("Processing list", list_title)
    
    for entry in rss_playlist['entries']:

        # This parse is biased towards titles and against people with by in their name.
        # If you favorite "Two if by sea" by Paul by the Horse, expect sorrow.
        m = re.match(r"^(.+) by (.+?)$", entry['title'])
        title = m.group(1)    
        artist = m.group(2)
        # I mean, literally I'm doing the same horrible thing here with my hyphen but
        # at least you'll have sensible MP3 tags there, kinda.
        filename = clean_filename.convert(artist + " - " + title)
       
        print("Title: ",  title)
        print("Artist: ", artist)
        print("Filename: ", filename)
        print("---------")

process_feed(sys.argv[1])

