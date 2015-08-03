# -*- coding: utf-8 -*-
# Copyright (c) 2015, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Graph utilities
===============

A module containing several graph utility functions
"""

import itertools

import numpy as np


def straight_line_vertices(adjacency_mat, node_coords, directed=False):
    if adjacency_mat.shape[0] != adjacency_mat.shape[1]:
        raise ValueError("Adjacency matrix should be square.")

    num_nodes = adjacency_mat.shape[0]

    line_vertices = []
    arrows = []
    for edge in itertools.combinations(range(num_nodes), 2):
        reverse = (edge[1], edge[0])

        if adjacency_mat[edge] == 1 or adjacency_mat[reverse] == 1:
            line_vertices.extend([node_coords[edge[0]],
                                  node_coords[edge[1]]])

        if directed:
            # TODO: This can probably be vectorized
            if adjacency_mat[edge] == 1 and adjacency_mat[reverse] == 0:
                arrows.extend([
                    node_coords[edge[0]],
                    node_coords[edge[1]]
                ])
            elif adjacency_mat[edge] == 0 and adjacency_mat[reverse] == 0:
                arrows.extend([
                    node_coords[reverse[0]],
                    node_coords[reverse[1]]
                ])

    line_vertices = np.array(line_vertices)
    arrows = np.array(arrows).reshape((len(arrows)/2, 4))

    return line_vertices, arrows
