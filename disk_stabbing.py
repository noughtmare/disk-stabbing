from math import sqrt, asin
import skgeom as sg
from skgeom.draw import draw
from collections import deque
import matplotlib.pyplot as plt

def tangents(r, p1, p2):
    """
    Calculate tangents between two disks disks centered at 'p1' and 'p2' with
    radius 'r'.

    If 'p1' and 'p2' coincide then no tangents are returned.
    If 'p1' and 'p2' overlap then two outer tangents will be returned.
    Otherwise the two outer and the two inner tangents will be returned.
    """
    s = sg.Segment2(p1, p2)
    dd = s.squared_length()
    d = sqrt(dd)
    tangents = []
    if d > 0:
        # Vector from the middle of 'p1' to the outer tangent point
        v = s.to_vector().perpendicular(sg.COUNTERCLOCKWISE) / d * r
        #
        tangents += [
            s.transform(sg.Transformation2(sg.TRANSLATION, v)),
            s.transform(sg.Transformation2(sg.TRANSLATION, -v))
        ]
        if d > 2 * r:
            # Calculate inner tangent lines

            # the middle of the segment from 'p1' to 'p2'
            mid = p1.transform(
                sg.Transformation2(sg.TRANSLATION, 0.5 * (p2 - p1)))
            # distance between the inner tangent points
            innerDistance = sqrt((d - 2 * r) * (d + 2 * r))
            # angle between the inner tangent line and the segment from 'p1' to 'p2'
            innerAngle = - 2 * r / d

            # counterclockwise inner tangent line
            innerCCW = s.transform(
                sg.Transformation2(sg.TRANSLATION, mid - sg.Point2(0, 0)) *
                sg.Transformation2(sg.SCALING, innerDistance / d) *
                sg.Transformation2(sqrt(1 - innerAngle**2), innerAngle,
                                   -innerAngle, sqrt(1 - innerAngle**2), 1) *
                sg.Transformation2(sg.TRANSLATION,
                                   sg.Point2(0, 0) - mid))

            # now rotate the other way around
            innerAngle = -innerAngle

            # clockwise inner tangent line
            innerCW = s.transform(
                sg.Transformation2(sg.TRANSLATION, mid - sg.Point2(0, 0)) *
                sg.Transformation2(sg.SCALING, innerDistance / d) *
                sg.Transformation2(sqrt(1 - innerAngle**2), innerAngle,
                                   -innerAngle, sqrt(1 - innerAngle**2), 1) *
                sg.Transformation2(sg.TRANSLATION,
                                   sg.Point2(0, 0) - mid))

            tangents += [innerCCW, innerCW]

    return tangents

def circle_oriented_side(r, p, l):
    if sg.squared_distance(l, p) <= r * r:
        return sg.ZERO
    else:
        return l.oriented_side(p)

def circle_line_count_intersections(r, p, l):
    dd = sg.squared_distance(l, p)
    rr = r * r
    return (2 if dd < rr else
            1 if dd == rr else
            0)

def circle_circle_count_intersections(r, p1, p2):
    dd = sg.squared_distance(p1, p2)
    rr = 4 * r * r
    return (2 if dd < rr else
            1 if dd == rr else
            0)

def circle(p, r):
    return sg.Circle2(p, r * r, sg.POSITIVE)

class WedgeTunnel:
    
    def __init__(self, r, p1, p2):
        ts = tangents(r, p1, p2)
        if len(ts) < 4:
            raise ValueError("Overlapping disks not yet implemented")
        _, _, it1, it2 = ts
        self.r = r
        self.ccw = it1.supporting_line()
        self.cw = it2.supporting_line()
        self.disks = [p1, p2]
        self.top = deque([p1, p2])
        self.bot = deque([p1, p2])

    def visualize(self):
        top = list(self.top)
        bot = list(self.bot)
        for disk in self.disks:
            draw(circle(disk, self.r))
        for d1, d2 in zip(top, top[1:]):
            draw(tangents(self.r,d1,d2)[0])
        for d1, d2 in zip(bot, bot[1:]):
            draw(tangents(self.r,d1,d2)[1])
        draw(self.ccw)
        draw(self.cw)
        plt.show()

    def intersects_wedge(self, p):
        return (sg.POSITIVE != circle_oriented_side(self.r, p, self.ccw)
                and sg.NEGATIVE != circle_oriented_side(self.r, p, self.cw)
                and (0 < circle_circle_count_intersections(self.r, p, self.disks[-1])
                or sg.POSITIVE != circle_oriented_side(
                    self.r, p, self.ccw.perpendicular(self.disks[-1]))
                or sg.POSITIVE != circle_oriented_side(
                    self.r, p, self.cw.perpendicular(self.disks[-1]))))

    def step(self, p):
        """
        Add a single point (disk) to the wedge tunnel. Doing this for all points
        in a list is Algorithm 1 from the paper by Guibas et al.
        """

        if 0 < circle_circle_count_intersections(self.r, self.disks[-1], p):
            raise ValueError("Overlapping disks not yet implemented")

        if self.intersects_wedge(p):
            if 2 > circle_line_count_intersections(self.r, p, sg.Ray2(
                    sg.intersection(self.ccw, self.cw), self.ccw)):
                # update the right side of the top support hull
                while len(self.top) > 1 and sg.NEGATIVE != circle_oriented_side(
                        self.r, self.top[-1],
                        tangents(self.r, self.top[-2], p)[0].supporting_line()):
                    self.top.pop()
                self.top.append(p)
                # update the ccw limiting line t and the left side of the top support hull
                self.ccw = tangents(self.r, self.bot[0], p)[2].supporting_line()
                while len(self.bot) > 1 and sg.POSITIVE == circle_oriented_side(
                        self.r, self.bot[1], self.ccw):
                    self.bot.popleft()
                    self.ccw = tangents(self.r, self.bot[0], p)[2].supporting_line()
            if 2 > circle_line_count_intersections(self.r, p, sg.Ray2(
                    sg.intersection(self.ccw, self.cw), self.cw)):
                # update the right side of the bot support hull
                while len(self.bot) > 1 and sg.POSITIVE != circle_oriented_side(
                        self.r, self.bot[-1],
                        tangents(self.r, self.bot[-2], p)[1].supporting_line()):
                    self.bot.pop()
                self.bot.append(p)
                # update the cw limiting line t and the left side of the top support hull
                self.cw = tangents(self.r, self.top[0], p)[3].supporting_line()
                while len(self.top) > 1 and sg.NEGATIVE == circle_oriented_side(
                        self.r, self.top[1], self.cw):
                    self.top.popleft()
                    self.cw = tangents(self.r, self.top[0], p)[3].supporting_line()
            self.disks.append(p)
            return True
        else:
            return False
