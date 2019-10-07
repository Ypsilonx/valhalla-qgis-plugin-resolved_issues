# -*- coding: utf-8 -*-
"""
/***************************************************************************
 valhalla
                                 A QGIS plugin
 QGIS client to query openrouteservice
                              -------------------
        begin                : 2017-02-01
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Nils Nolde
        email                : nils.nolde@gmail.com
 ***************************************************************************/

 This plugin provides access to the various APIs from OpenRouteService
 (https://openrouteservice.org), developed and
 maintained by GIScience team at University of Heidelberg, Germany. By using
 this plugin you agree to the ORS terms of service
 (https://openrouteservice.org/terms-of-service/).

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""


def pipe_list(arg):
    """Convert list of values to pipe-delimited string"""
    if not _is_list(arg):
        raise TypeError(
            "Expected a list or tuple, "
            "but got {}".format(type(arg).__name__))
    return "|".join(map(str, arg))


def comma_list(arg):
    """Convert list to comma-separated string"""
    if not _is_list(arg):
        raise TypeError(
            "Expected a list or tuple, "
            "but got {}".format(type(arg).__name__))
    return ",".join(map(str, arg))


def _checkBool(boolean):
    """Check whether passed boolean is a string"""
    if boolean not in ["true", "false"]:
        raise ValueError("Give boolean as string 'true' or 'false'.")
        
    return


def _format_float(arg):
    """Formats a float value to be as short as possible.

    Trims extraneous trailing zeros and period to give API
    args the best possible chance of fitting within 2000 char
    URL length restrictions.

    For example:

    format_float(40) -> "40"
    format_float(40.0) -> "40"
    format_float(40.1) -> "40.1"
    format_float(40.001) -> "40.001"
    format_float(40.0010) -> "40.001"

    :param arg: The lat or lng float.
    :type arg: float

    :rtype: string
    """
    return ("{}".format(round(float(arg), 6)).rstrip("0").rstrip("."))


def build_coords(arg):
    """Converts one or many lng/lat pair(s) to a comma-separated, pipe 
    delimited string. Coordinates will be rounded to 5 digits.

    For example:

    convert.build_coords([(151.2069902,-33.8674869),(2.352315,48.513158)])
    # '151.20699,-33.86749|2.35232,48.51316'

    :param arg: The lat/lon pair(s).
    :type arg: list or tuple
    
    :rtype: str
    """
    if _is_list(arg):
        return pipe_list(_concat_coords(arg))
    else:
        raise TypeError(
            "Expected a list or tuple of lng/lat tuples or lists, "
            "but got {}".format(type(arg).__name__))


def _trans(value, index):
    """
    Copyright (c) 2014 Bruno M. Custódio
    Copyright (c) 2016 Frederick Jansen

    https://github.com/hicsail/polyline/commit/ddd12e85c53d394404952754e39c91f63a808656
    """
    byte, result, shift = None, 0, 0

    while byte is None or byte >= 0x20:
        byte = ord(value[index]) - 63
        index += 1
        result |= (byte & 0x1f) << shift
        shift += 5
        comp = result & 1

    return ~(result >> 1) if comp else (result >> 1), index


def decode_polyline6(expression, precision=6, is3d=False):
    """
    Copyright (c) 2014 Bruno M. Custódio
    Copyright (c) 2016 Frederick Jansen

    https://github.com/hicsail/polyline/commit/ddd12e85c53d394404952754e39c91f63a808656
    """
    coordinates, index, lat, lng, z, length, factor = [], 0, 0, 0, 0, len(
        expression), float(10**precision)

    while index < length:
        lat_change, index = _trans(expression, index)
        lng_change, index = _trans(expression, index)
        lat += lat_change
        lng += lng_change
        if not is3d:
            coordinates.append((lat / factor, lng / factor))
        else:
            z_change, index = _trans(expression, index)
            z += z_change
            coordinates.append((lat / factor, lng / factor, z / 100))

    return coordinates


def _concat_coords(arg):
    """Turn the passed coordinate tuple(s) in comma separated coordinate tuple(s).
    
    :param arg: coordinate pair(s)
    :type arg: list or tuple
    
    :rtype: list of strings
    """
    if all(_is_list(tup) for tup in arg):
        # Check if arg is a list/tuple of lists/tuples
        return [comma_list(map(_format_float, tup)) for tup in arg]
    else:
        return [comma_list(_format_float(coord) for coord in arg)]


def _is_list(arg):
    """Checks if arg is list-like."""    
    if isinstance(arg, dict):
        return False
    if isinstance(arg, str): # Python 3-only, as str has __iter__
        return False
    return (not _has_method(arg, "strip")
            and _has_method(arg, "__getitem__")
            or _has_method(arg, "__iter__"))


def _has_method(arg, method):
    """Returns true if the given object has a method with the given name.

    :param arg: the object

    :param method: the method name
    :type method: string

    :rtype: bool
    """
    return hasattr(arg, method) and callable(getattr(arg, method))
