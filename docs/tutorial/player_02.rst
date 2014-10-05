Pygame and Video
----------------

To draw to the screen, we're going to use pygame. pygame is an excellent
and well known module which advertises itself as

::

    Pygame is a set of Python modules designed for writing games. Pygame adds functionality
    on top of the excellent SDL library. This allows you to create fully featured games and
    multimedia programs in the python language. Pygame is highly portable and runs on
    nearly every platform and operating system.

You can get the package at the `official
website <http://www.pygame.org>`__ or on PyPI.

Pygame has various methods for drawing images to the screen, and it has
one in particularly well suited for displaying movies on the screen -
what it calls a YUV overlay. YUV (technically not YUV but YCbCr:
generally speaking, YUV is an analog format and YCbCr is a digital
format. However, they are often -and incorrectly- used as synonims) is a
way of storing raw image data like RGB. Roughly speaking, Y is the
brightness (or "luma") component, and U and V are the color components.
pygame's YUV overlay takes in a triplet of bytes (strings in py2.x)
containing the YUV data and displays it. It accepts an handful of
different kinds of YUV formats, but YV12 is most often the fastest.
There is another YUV format called YUV420P that is the same as YV12,
except the U and V arrays are switched. The 420 means it is subsampled,
at a ratio of 4:2:0, basically meaning there is 1 color sample for every
4 luma samples, so the color information is quartered. This is a good
way of saving bandwidth, as the human eye does not percieve this change.
The "P" in the name means that the format is "planar" -- simply meaning
that the Y, U, and V components are in separate arrays. pyrana can
convert images to YUV420P, with the added bonus that many video streams
are in that format already, or are easily converted to that format.

So our current plan is to replace the ``ppm_write`` function from `part
1 <http://mojaves.github.io/pyrana-player-tutorial-part-1.html>`__, and
instead output our frame to the screen. But first we have to start by
seeing how to use the pygame package. First we have to import and to
initialize it, once again one time only:

::

    import pygame
    ...
    pygame.init()

Creating and using an Overlay
-----------------------------

Now we need a place on the screen to put stuff. The basic area for
displaying images with SDL is called an *overlay*:

::

    pygame.display.set_mode((width, height))
    self._ovl = pygame.Overlay(pygame.YV12_OVERLAY, (width, height))
    self._ovl.set_location(0, 0, wwidth, height)

As we said before, we are using YV12 to display the image:

::

    self._ovl.display((Y, U, V))
       

The overlay object takes care of locking, so we don't have to. The
``Y``, ``U`` and ``V`` objects are bytes() (strings in py2.x) filled
with the actual data to display. Of course since we are dealing with
YUV420P here, we only have 3 channels, and therefore only 3 sets of
data. Other formats might have a fourth pointer for an alpha channel or
something.

The code which draws using the pygame overlays can be packed in an handy
class:

::

    class PygameViewer(object):
    def __init__(self):
        self._ovl = None
        self._frames = 0

    @property
    def frames(self):
        return self._frames

    def setup(self, w, h):
        pygame.display.set_mode((w, h))
        self._ovl = pygame.Overlay(pygame.YV12_OVERLAY, (w, h))
        self._ovl.set_location(0, 0, w, h)

    def show(self, Y, U, V):
        self._ovl.display((Y, U, V))
        self._frames += 1

Drawing the Image
-----------------

What is stil left is to fetch the plane data and pass it to pygame's
overlay in order to actually display it. No worries, this is very simple
as well:

::

    while True:
        frame = vdec.decode(dmx.stream(sid))
        img = frame.image()
        view.show(img.plane(0), img.plane(1), img.plane(2))

Where ``view`` is of course an instance -already set up and ready- of a
``PygameViewer`` defined above. This is actually the whole decoding
loop! The Image objects provides an handy ``plane()`` method with just
returns the ``bytes()`` of the selected plane.

What happens when you run this program? The video is going crazy! In
fact, we're just displaying all the video frames as fast as we can
extract them from the movie file. We don't have any code right now for
figuring out *when* we need to display video. Eventually (in part 5),
we'll get around to syncing the video. But first we're missing something
even more important: sound!

The full working code (well, a slightly enhanced version of) used in
this post is `available
here <https://github.com/mojaves/pyrana/blob/master/examples/11_compat_video_pygame.py>`__.

.. raw:: html

   <script src="https://gist.github.com/mojaves/6980465.js"></script>
