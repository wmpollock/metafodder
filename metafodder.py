
# Bill Pollock
# 2019

import clean_filename, eyed3, feedparser, json, os, re, urllib.parse, urllib.request, sys
from pathlib import Path
from titlecase import titlecase
from tqdm import tqdm
import eyed3.mp3

# libmagic incorrectly identifies this file (http://music.metafilter.com/1733) as x-dbt, a DBase file!
# A guy posted a fix to his entry (https://mailman.astron.com/pipermail/file/2019-June/000146.html)
# buuuut even if it were applied (which I'm not sure it has) we'd need to rebuild through
# the Windows Linux subsystem which IDK, seem a bit heavy-handed compared to lying to our
# friend here.
eyed3.mp3.OTHER_MIME_TYPES= ['application/octet-stream', 'audio/x-hx-aac-adts', 'audio/x-wav', 'application/x-dbt']
base_outdir = os.path.join(str(Path.home()), "Music", "MetaFilter")

pbar = None


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

        # Feedparser considers this an "unusual" element. 
        url = entry.enclosures[0]['href']


        # Gonna normalize this too:  you cna uname like you want to but c'mon
        file_info = {
            "title": titlecase(m.group(1)), 
            # You can be ee cummings if you want.
            "artist": m.group(2),
            # faux album for organization purposes
            "list_title": list_title,
            "published_parsed": entry.published_parsed,
            "path": get_outpath(file_info),
            "audio_file_url": url,
            "auto_source_url": entry.link
        }

        print("Title:",  file_info['title'], "\n",
              "Artist:", file_info['artist'])

        urlparts = urllib.parse.urlparse(url)
        # IDK, this value is kind of quirky and cute
        url_filename  = urllib.parse.unquote(os.path.basename(urlparts.path))
        
        # TODO: maybe nice to leverage enclosure[length]
        # Hells yes it would be nice:  the existence test doesn't help us
        # if we failed the d/l for some reason.
        # Unfortunately since we also jack with the tags the filesize
        # we have won't be the same as on the remote :[
        if os.path.exists(file_info['path']):
            print(file_info['path'], "already exists.")
        else:
            # OK, Boom goes the dynamite, lets get the file and start to process it
            print("Downloading", file_info['path'])
            urllib.request.urlretrieve(url, file_info['path'], update_progress)

            # Do some cleanup on the progress bar 
            global pbar
            pbar.close()
            pbar = None # Lets reset this mess

            retag_mp3(file_info)
            
        print("---------")


def retag_mp3(file_info):
        try:
            mp3 = eyed3.load(file_info['path'])
            if mp3:
                if mp3.tag:
                    tags = mp3.tag 
                else:
                    tags = mp3.initTag()
            else:
                print("WHAAAT?1?!")
                exit()

        # A file from the appropriately uname'd 'fuq'
        except eyed3.id3.tag.TagException:
            print("Whoops!  Guess we'll be losing that extended header...")
        except Exception as e:
         #   e = sys.exc_info()[0]
            print("Dang, exception city", e)
            exit()

        # Normalize to metafilter naming -- we'll keep the original
        if tags.artist:
            tags.comments.set(tags.artist, "Source artist")

        if tags.title:
            tags.comments.set(tags.title,  "Source title")
        
        if tags.album:
            tags.comments.set(tags.album,  "Source album")
        
        tags.artist = file_info['artist']
        tags.title =  file_info['title']
        tags.album =  file_info['list_title']
    
        # Some values just don't wash in an archive
        #---------------------------------------------------------------------
       
        if tags.track_num:
            tags.comments.set(str(tags.track_num), "Source track_num")
            tags.track_num = None # we got no context now friend...

        # Some of these values are rather unlikely buuuut I'd prefer the
        # artists' values over mine should they exist
        # --------------------------------------------------------------------
        if not tags.audio_file_url:
            # Why bytes?  IDK, seems inconsistent?
            tags.audio_file_url = bytes(file_info['url'], "utf-8")
        
        if not tags.audio_source_url:
            tags.audio_source_url = bytes(file_info['link'], "utf-8")
        
        # Syntactic sugar: reliance on published_parsed is an impediment
        # to feeds from other sources :/
        rd = file_info['published_parsed']

        # Year
        # Go with the published date.
        tory = bytes("TORY", "utf-8")
        if not tags.frame_set[tory]:
            print("TORY!")
            tags.frame_set[tory] = rd[0]
            
        if not tags.release_date:
            #tags.release_date = "%d-%d-%dT%d:%d:%dZ" % (entry.published_parsed[0:5])
            print("Setting release date")
            tags.release_date = "%d-%d-%dT%d:%d:%d" % (rd[0],rd[1],rd[2], rd[3],rd[4],rd[5])
        
        if 'url_filename' in file_info:
            tags.comments.set(file_info['url_filename'], "Source filename")
            tags.save(version=(1,None,None))

        # These tag existed in earlier tag revisions (2.2 mostly) but eyed3 barfs converting
        # these.
        poorly_handled_tags = ['IPLS','RVAD', 'RGAD']
        for frame in poorly_handled_tags:
            frameB = bytes(frame, "utf-8")
            if frameB in tags.frame_set:
                del tags.frame_set[frameB]

        # Necessary to override, I guess just if 2.2 'cos eyed3 won't write that :/
        # There's something to be said however for conisistendy
        tags.version = eyed3.id3.ID3_DEFAULT_VERSION

        tags.save(encoding='utf-8')

def get_outpath(file_info):
    # I thought maybe MeFi would be using OGG but as of 2019
    # their submissions are still.  MP3 only ¯\_(ツ)_/¯  I mean, yeet, I guess.
    # Thought I was going to have go get all up into mimetypes.guess_extension :O
    filename = clean_filename.convert(file_info['artist'] + " - " + file_info['title']) + ".mp3"
    
    # I'm going to the content in a per-playlist folder because I keep
    # my xmas music segregated and kind of don't want to load it on the 
    # accidental.  Tempting to lump 'em all together in oen subdir tho
    outdir = os.path.join(base_outdir, clean_filename.convert(file_info['list_title']))

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    outpath = os.path.join(outdir, filename)
    return(outpath)



def update_progress(chunkno, chunkmax, size):
    # I'm not sure why we wouldn't get this but if unknown we could get -1
    # and I guess zero might be a thing 
    global pbar
    if size > 0:
        global pbar
        if not pbar:
             pbar= tqdm(total=size,unit_scale=True,unit="bytes")

        pbar.update(chunkmax)

if __name__ == "__main__":
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

