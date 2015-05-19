# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.


def generate_paths(paths, filename):
    return (paths and
        map(lambda path: '/'.join([path, filename]), paths.split(','))
        or [filename])
