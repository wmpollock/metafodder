
# Bill Pollock
# 2019

import clean_filename, eyed3, feedparser, json, os, re, urllib.parse, urllib.request, sys
from pathlib import Path
from titlecase import titlecase


#eyed3.LOCAL_ENCODING= 'UTF-8'
#eyed3.LOCAL_FS_ENCODING= 'utf-8'


base_outdir = os.path.join(str(Path.home()), "Music", "MetaFilter")

def process_feed(feed_url):
    rss_playlist = feedparser.parse(feed_url)

    # Strip out the additional branding on our OG title.
    list_title = rss_playlist.feed.title.split(" | ")[0]
    print("Processing list", list_title)
    print(len(rss_playlist['entries']), "entries in the list.")
    print("=" * 79)
    for entry in rss_playlist['entries']:

        # This parse is biased towards titles and against people with by in their name.
        # If you favorite "Two if by sea" by Paul by the Horse, expect sorrow.
        m = re.match(r"^(.+) by (.+?)$", entry['title'])
        
        # Gonna normalize this too:  you cna uname like you want to but c'mon
        title = titlecase(m.group(1)) 
        artist = m.group(2)
        # I mean, literally I'm doing the same horrible thing here with my hyphen but
        # at least you'll have sensible MP3 tags there, kinda.

        # Also I thought maybe MeFi would be progressively using OGG but as of 2019
        # their submissions are still.  MP3 only ¯\_(ツ)_/¯  I mean, yeet, I guess.
        # Thought I was going to have go get all up into mimetypes.guess_extension :O
        filename = clean_filename.convert(artist + " - " + title) + ".mp3"
        
        # I'm going to the content in a per-playlist folder because I keep
        # my xmas music segregated and kind of don't want to load it on the 
        # accidental.  Tempting to lump 'em all together in oen subdir tho
        outdir = os.path.join(base_outdir, clean_filename.convert(list_title))
        if not os.path.exists(outdir):
            os.mkdir(outdir)

        outpath = os.path.join(outdir, filename)

        # Feedparser considers this an "unusual" element. 
        url = entry.enclosures[0]['href']
        urlparts = urllib.parse.urlparse(url)
        # IDK, this value is kind of quirky and cute
        url_filename  = urllib.parse.unquote(os.path.basename(urlparts.path))

        print("Title: ",  title)
        print("Artist: ", artist)
        
        # TODO: maybe nice to leverage entry[length]
        if os.path.exists(outpath):
            print(outpath, "already exists")
        else:
            # OK, Boom goes the dynamite, lets get the file and start to process it
            print("Downloading", outpath)
            urllib.request.urlretrieve(url, outpath)
        
        try:
            mp3 = eyed3.load(outpath)
            if mp3.tag:
                tags = mp3.tag 
            else:
                tags = mp3.initTag()

        # A file from the appropriately uname'd 'fuq'
        except eyed3.id3.tag.TagException:
            print("Whoops!  Guess we'll be losing that extended header...")
        

        # Normalize to metafilter naming -- we'll keep the original
        if tags.artist:
            tags.comments.set(tags.artist, "Source artist")

        if tags.title:
            tags.comments.set(tags.title,  "Source title")
        
        if tags.album:
            tags.comments.set(tags.album,  "Source album")
        
        tags.artist = artist
        tags.title =  title
        tags.album =  list_title
    
        # Some values just don't wash in an archive
        #-------------------------------------------------------------

        if tags.track_num:
            tags.comments.set(str(tags.track_num), "Source track_num")
            tags.track_num = None # we got no context now friend...

        # Some of these values are rather unlikely buuuut I'd prefer the
        # artists' values over mine should they exist
        if not tags.audio_file_url:
            # Why bytes?  IDK, seems inconsistent?
            tags.audio_file_url = bytes(url, "utf-8")
        
        if not tags.audio_source_url:
            tags.audio_source_url = bytes(entry.link, "utf-8")
            
        if not tags.release_date:
            rd = entry.published_parsed
            #tags.release_date = "%d-%d-%dT%d:%d:%dZ" % (entry.published_parsed[0:5])
            tags.release_date = "%d-%d-%dT%d:%d:%dZ" % (rd[0],rd[1],rd[2], rd[3],rd[4],rd[5])
            

        # Man, is this even a legal descriptor?  Many minutes in its hard to say.  iTunes
        # appears to be the greatest generator of tagged comments buuuuut theirs are all
        # way varnamy...
        tags.comments.set(url_filename, "Source filename")
        tags.save(version=(1,None,None))


        # These tag existed in earlier tag revisions (2.2 mostly) but eyed3 barfs converting
        # these.
        poorly_handled_tags = ['IPLS','RVAD', 'RGAD']
        for frame in poorly_handled_tags:
            frameB = bytes(frame, "latin-1")
            if frameB in tags.frame_set:
                del tags.frame_set[frameB]

        # Necessary to override I guess just if 2.2 'cos eyed3 won't write that :/
        tags.version = eyed3.id3.ID3_DEFAULT_VERSION;



        tags.save(encoding='utf-8')

        #exit()
        print("---------")

# PREAMBLE:  Lets get to feeling right
# ----------------------------------------------------------------------------
eyed3.log.setLevel("ERROR")

# Unfortunately necessary if you redirect STDOUT w/o barfing 
sys.stdout.reconfigure(encoding='utf-8')

# OFF TO THEM RACES!
# ----------------------------------------------------------------------------
if len(sys.argv) == 1:
    print("Usage:", sys.argv[0], "{RSS url|RSS filename}")

for arg in sys.argv[1:]:
    process_feed(arg)

