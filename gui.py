import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject

import math

from disk_stabbing import WedgeTunnel, tangents
import skgeom as sg


r = 40
disks = []
wt = None


def add_disk(x, y):
    global disks, wt
    p = sg.Point2(x, y)
    disks.append(p)
    try:
        if len(disks) == 2:
            wt = WedgeTunnel(r, disks[0], disks[1])
        elif wt:
            success = wt.step(p)
            if not success:
                disks = []
                wt = None
    except ValueError as e:
        print(e)
        disks = []
        wt = None


class Screen(Gtk.DrawingArea):
    """ This class is a Drawing Area"""
    def __init__(self):
        super(Screen,self).__init__()
        ## Connect to the "draw" signal
        self.connect("draw", self.on_draw)

    ## When the "draw" event fires, this is run
    def on_draw(self, widget, event):
        self.cr = self.get_window().cairo_create()
        ## Call our draw function to do stuff.
        geom = self.get_window().get_geometry()

        width = geom.width
        height = geom.height
        cr = self.cr

        for disk in disks:
            cr.arc(disk.x(), disk.y(), r, 0, 2 * math.pi)
            cr.stroke()

        if type(wt) == WedgeTunnel:
            draw_line(cr, width, height, wt.ccw)
            draw_line(cr, width, height, wt.cw)
            
            top = list(wt.top)
            for d1, d2 in zip(top, top[1:]):
                draw_segment(cr, tangents(r, d1, d2)[0])
            
            bot = list(wt.bot)
            for d1, d2 in zip(bot, bot[1:]):
                draw_segment(cr, tangents(r, d1, d2)[1])


# TODO: add colors
def draw_line(cr, width, height, l):
    """
    To draw an infinite line we draw only the segment of the line that is inside
    the screen borders.
    """

    # corners
    tl = sg.Point2(0,0)
    tr = sg.Point2(width, 0)
    br = sg.Point2(width, height)
    bl = sg.Point2(0, height)

    # sides
    st = sg.Segment2(tl, tr)
    sr = sg.Segment2(tr, br)
    sb = sg.Segment2(br, bl)
    sl = sg.Segment2(bl, tl)

    # (possible) intersection points
    pl = sg.intersection(l, sl)
    pt = sg.intersection(l, st)
    pr = sg.intersection(l, sr)
    pb = sg.intersection(l, sb)

    # There are some annoying edge cases where the line goes through the corners

    # If the line intersects a corner exactly then it must intersect at least
    # three sides and hence it must intersect at least two opposing sides.
    if pl and pr:
        start = pl
        end = pr
    elif pt and pb:
        start = pt
        end = pb
    else:
        # Otherwise we know that only two sides are intersected
        start, end = tuple([x for x in [pl, pr, pt, pb] if x])

    draw_segment(cr, sg.Segment2(start, end))


def draw_segment(cr, s):
    start = s.source()
    end = s.target()
    cr.move_to(start.x(), start.y())
    cr.line_to(end.x(), end.y())
    cr.stroke()


def click(area, x, y):
    add_disk(x, y)
    area.queue_draw()


def run(Widget):
    window = Gtk.Window()
    window.connect("destroy", Gtk.main_quit)
    window.set_size_request(400, 400)
    widget = Widget()
    widget.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
    widget.show()
    widget.connect('button-press-event', lambda area, event: click(area, event.x, event.y))
    window.add(widget)
    window.present()
    Gtk.main()


def main():
    run(Screen)
