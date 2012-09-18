#!/usr/bin/env python

import wsgiref.handlers
import random
from model import Tile, Avatar
from google.appengine.ext import db
import json

from google.appengine.ext import webapp

view_radius = 2


def make_maze(width, height):
    # Four basic direction vectors
    vectors = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    # Backtracking offset
    offset = 0
    # Set initial location
    x = y = 0
    # Define maze size
    x_max = width
    y_max = height
    x_min = y_min = 0
    # Setup tracking lists
    cleared = []
    blocked = []
    while 1:
        if (x, y) not in cleared:
            cleared.append((x, y))

        # Rectify surroundings
        # Look in each direction
        open = []
        for (x_d, y_d) in vectors:
            # adj is the x,y of the adjacent tile in chosen direction
            adj = (x + x_d, y + y_d)
            if adj[0] < x_min or adj[0] >= x_max:
                continue
            if adj[1] < y_min or adj[1] >= y_max:
                continue
            if adj in cleared or adj in blocked:
                # If the adjacent tile was already hit by an overlapping pass
                continue
            # Block the adjacent tile if two or more of it's neighbors is clear
            # Might want to tinker with this to stop 1x1 spurs
            for (x_d2, y_d2) in vectors:
                adj2 = (adj[0] + x_d2, adj[1] + y_d2)
                if adj2 == (x, y):
                    continue
                if adj2 in cleared:
                    blocked.append(adj)
                    break
            else:
                open.append(adj)

        # Pick a next move
        if open == []:
            offset += 1
            if offset > len(cleared):
                break
            x, y = cleared[-offset]
        else:
            offset = 0
            x, y = random.choice(open)
    return cleared


def get_shape(x, y, cleared):
    shape = 0
    if (x, y - 1) in cleared:
        shape |= 1
    if (x + 1, y) in cleared:
        shape |= 2
    if (x, y + 1) in cleared:
        shape |= 4
    if (x - 1, y) in cleared:
        shape |= 8
    return shape


class MainHandler(webapp.RequestHandler):

    def get(self):
        db.delete(Tile.all())
        db.delete(Avatar.all())
        cleared = make_maze(20, 20)
        for t in cleared:
            view = []
            for vy in range(t[1] - view_radius, t[1] + view_radius + 1):
                for vx in range(t[0] - view_radius, t[0] + view_radius + 1):
                    if (vx, vy) in cleared:
                        shape = get_shape(vx, vy, cleared)
                        view.append({'x': vx, 'y': vy, 'shape': shape})
            shape = get_shape(t[0], t[1], cleared)
            key = db.Key.from_path(
                'Maze', 'bogart',
                'Tile', '%d-%d' % (t[0], t[1])
            )
            Tile(
                key=key,
                x=t[0],
                y=t[1],
                shape=shape,
                view_blob=json.dumps(view)
            ).put()
        Avatar(x=0, y=0, name='jack').put()
        self.response.out.write('Generator %s' % cleared)


def main():
    application = webapp.WSGIApplication([('/gen', MainHandler)],
                                         debug=True)
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
    main()
