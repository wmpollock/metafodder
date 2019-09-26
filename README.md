# metafodder

A python script to rip MetaFilter playlists to the local disk.

## Background

I love the artists available on MetaFilter but I worry sometimes about the
permanent availability of the media and certainly would like to  listen to it
offline consume it in a variety of other ways.

MetaFilter makes available a RSS feed which is great for users of podcast
software but not so much for dirty scrapers such as ourselves to do the same
thing.  Podcast software tends to want to label everything as a "podcast" which
is most often then apart from the rest of one's music stash.

If you have a great piece of podcast ripping software with which one can normalize
and do this other mess, please HMU: I do this mostly out of impatience.

## Source issues

One of the bummers in the current RSS is that it's the most information-rich
source for content links but at the same time uses difficult content
representation; there are a few things that could have been done to make it
more data rich I think but meh, we're lucky to have what we have.

There's also a problem from a curation standpoint that the filenames MeFi
retains are as-uploaded by the artist and exhibit an expected disharmony in
styles.  The MP3 tag data runs the same way.

## Applying feed data

Part of me thinks that this variance is interesting and at times important.
While I want to associate these files data-wise the most with their username and
use the album for playlisting the original information is maybe of use in
tracking down more from the artist so is worth stashing and trying to do so in a
recoverable fashion.

### filenames

{artist} - {title}

### MP3 Tags

* title: {title}
* artist: {artist}
* album: {playlist title}
* comments: {original-comments}[artist: {original-artist}][title: {original-title}][album: {original-album}]
* year: {year entry.published}
* url: {entry.link}
