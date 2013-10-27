Title: Pyrana player tutorial part 1
Date: 2013-10-08 21:27
Tags: english, programming, projects, python, ffmpeg, tutorial
Category: pyrana
Slug: pyrana-player-tutorial-part-1
Author: Francesco Romani
Summary: How to write a media player using Pyrana. Inspired by the FFmpeg tutorial.


Intro
-----

This is a multi-part tutorial about how to write a simple yet complete and fully functional
media player using [pyrana](http://bitbucket.org/mojaves/pyrana).
The structure of the tutorial intentionally resemples as closely as possible
the [FFmpeg tutorial](http://dranger.com/ffmpeg/tutorial01.html).

As for the original work, to which this one pays heavy debt, this document is released under
the terms of the [Creative Commons Attribution-Share Alike 2.5 License](http://creativecommons.org/licenses/by-sa/2.5/).

<!-- more -->


Overview
--------

Movie files have a few basic components. First, the file itself is called a
*container*, and the type of container determines where the information in
the file goes. Examples of containers are AVI, Quicktime, Matroska (MKV) or ogg.
Next, you have a bunch of *streams*; for example, you usually have an audio stream
and a video stream. (A "stream" is just a fancy word for "a succession of data
elements made available over time".) The data elements in a stream are called
*frames*. Each stream is encoded by a different kind of **codec**. The codec
defines how the actual data is COded and DECoded - hence the name CODEC.
Examples of codecs are WEBM, H.264, MP3 or Vorbis. *Packets* are then read from the
stream. Packets are pieces of data that can contain bits of data that are
decoded into raw frames that we can finally manipulate for our application.
For our purposes, each packet contains complete frames, or multiple frames in
the case of audio. 

At its very basic level, dealing with video and audio streams is very easy: 
    
        
    with open_stream("video.ogg") as video:
        frame = video.read_packet()
	if not frame.complete:
            continue
        do_something(frame)
    

We will see soon enough that in real python code, thanks to pyrana, the real code
is not very different from this pseudo code above. However, some programs might
have a very complex `do_something` step. So in
this tutorial, we're going to open a file, read from the video stream inside
it, and our `do_something` is going to be writing the frame to a PPM file. 


Opening the File
----------------

First, let's see how we open a file in the first place. With pyrana, you have
to first initialize the library.
    
    
    import pyrana

    # somewhere, once per run
    
    pyrana.setup()
        

This registers all available file formats and codecs with the library so they
will be used automatically when a file with the corresponding format/codec is
opened. Note that you only need to call pyrana.setup() once, but it is safe
to do it multiple times, if you cannot avoid it.

Now we can actually open the media file: 
    
    
    with open(sys.argv[1], "rb") as src:
        dmx = pyrana.Demuxer(src)    
        

Here `dmx` is one of the most common shortcut names for `demuxer`.
We get our filename from the first argument. The Demuxer instance needs a
valid, already open, binary data provider to be used as underlying source of
data.
Now you can access the stream informations using the `streams` attribute.
`demuxer.streams` is just a collections of data structures,
so let's find the zero-th (aka the first) video stream in the collection.


    from pyrana.formats import find_stream, MediaType
    # ...
    sid = find_stream(demuxer.streams,
                      0,
                      MediaType.AVMEDIA_TYPE_VIDEO)
    # sid: Stream ID
    vstream = dmx.streams[sid]
        

Now we can have all the available metadata about the stream (e.g. width
and height for a video stream, channel count and bytes per sample for an audio stream). 
However, we still need a decoder for that video stream. Simple enough:   

    
    vdec = dmx.open_decoder(sid)
        

Simple as that! now `codec` is ready to roll and decode the frames that will
be sent to it.



Reading the Data
----------------

What we're going to do is read through the entire video stream by reading in
the packet, decoding it into our frame, and once our frame is complete, we
will convert and save it. 

Since we're planning to output PPM files, which are stored in 24-bit RGB,
we're going to have to convert our frame from its native format to RGB. pyrana
will do these conversions for us. For most projects (including ours) we're
going to want to convert our initial frame to a specific format.
It's enough to ask an Image from a (video) Frame using the image() method
and specifying the desired pixel format. The default value for image() is
the same as the video stream.

     with open(sys.argv[1], "rb") as src:
        dmx = pyrana.formats.Demuxer(src)
        sid = pyrana.formats.find_stream(dmx.streams,
                                         0,
                                         MediaType.AVMEDIA_TYPE_VIDEO)
        num = 0
        vdec = dmx.open_decoder(sid)
        frame = vdec.decode(dmx.stream(sid))
        image = frame.image(pyrana.video.PixelFormat.AV_PIX_FMT_RGB24)
    


A note on packets
-----------------

Technically a packet can contain partial frames or other bits of data, but
pyrana's Demuxers (thanks to the ffmpeg libraries) ensures that the packets we
get contain either complete or multiple frames. 

The process, again, is simple: Demuxer.read_frame() reads in a packet and stores it
in a Packet object. Decoder.decode() converts
the packet to a frame for us. However, we might not have all the information
we need for a frame after decoding a packet, so Decoder.decode() raises NeedFeedError
if it is not able to decode the next frame. Finally, we use Image.convert()
to convert from the native format (Image.pixel_format) to RGB.

Now all we need to do is make the save_frame function to write the RGB
information to a file in PPM format. We're going to be kind of sketchy on the
PPM format itself; trust us, it works. 

    
    def ppm_write(frame, seqno):
        """
        saves a raw frame in a PPM image. See man ppm for details.
        the `seqno` parameter is just to avoid to overwrite them without
        getting too fancy with the filename generation.
        """
        image = frame.image(pyrana.video.PixelFormat.AV_PIX_FMT_RGB24)
        with open("frame%d.ppm" % (seqno), "wb") as dst:
            header = "P6\n%i %i\n255\n" % (image.width, image.height)
            dst.write(header.encode("utf-8"))
            dst.write(bytes(image))
    

In this case we require the full frame (not just the image) to be passed
to be sure to get an image with the conformant Pixel Format.
We do a bit of standard file opening, etc., and then write the RGB data. We
write the file one line at a time. A PPM file is simply a file that has RGB
information laid out in a long string. If you know HTML colors, it would be
like laying out the color of each pixel end to end like #ff0000#ff0000....
would be a red screen. (It's stored in binary and without the separator, but
you get the idea.) The header indicated how wide and tall the image is, and
the max size of the RGB values. 

Most image programs should be able to open PPM files. Test it on some movie
files. 

The full working code used in this post is
[available here](https://github.com/mojaves/pyrana/blob/master/examples/03_decode_video.py).

<script src="https://gist.github.com/mojaves/6949801.js"></script>

### EOF

