
# Bill Pollock
# 2019

import clean_filename, feedparser, os, re, urllib.parse, sys

# Unfortunately necessary if you redirect STDOUT w/o barfing 
sys.stdout.reconfigure(encoding='utf-8')

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

        # Also I thought maybe MeFi would be progressively using OGG but as of 2019
        # their submissions are still.  MP3 only ¯\_(ツ)_/¯  I mean, yeet, I guess.
        # Thought I was going to have go get all up into mimetypes.guess_extension :O
        filename = clean_filename.convert(artist + " - " + title) + ".mp3"

        # Feedparser considers this an "unusual" element. 
        url = entry.enclosures[0]['href'];
        urlparts = urllib.parse.urlparse(url)
        url_filename  = urllib.parse.unquote(os.path.basename(urlparts.path))

        print("Title: ",  title)
        print("Artist: ", artist)
        print("Filename: ", filename)
        print("Link: ", entry["link"])
        print("URL: ", url);
        print("URL filename: ", url_filename)
        print("---------")

for arg in sys.argv[1:]:
    process_feed(arg)

