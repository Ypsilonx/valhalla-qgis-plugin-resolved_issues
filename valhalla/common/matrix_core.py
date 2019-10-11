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

import json
from PyQt5.QtCore import QVariant

from qgis.core import (NULL,
                       QgsFeature,
                       QgsFields,
                       QgsField)

from valhalla.utils import convert


def get_fields(from_type=QVariant.String, to_type=QVariant.String, from_name="FROM_ID", to_name="TO_ID", line=False):
    """
    Builds output fields for directions response layer.

    :param from_type: field type for 'FROM_ID' field
    :type from_type: QVariant enum

    :param to_type: field type for 'TO_ID' field
    :type to_type: QVariant enum

    :param from_name: field name for 'FROM_ID' field
    :type from_name: str

    :param to_name: field name for 'TO_ID' field
    :type to_name: field name for 'TO_ID' field

    :param line: Specifies whether the output feature is a line or a point
    :type line: boolean

    :returns: fields object to set attributes of output layer
    :rtype: QgsFields
    """

    fields = QgsFields()
    fields.append(QgsField(from_name, from_type))
    fields.append(QgsField(to_name, to_type))
    fields.append(QgsField("DIST_KM", QVariant.Double))
    fields.append(QgsField("DURATION_H", QVariant.Double))
    fields.append(QgsField("PROFILE", QVariant.String))
    fields.append(QgsField("OPTIONS", QVariant.String))

    return fields


def get_output_features_matrix(locations, response, profile, options=None):
    """
    Build output feature based on response attributes for directions endpoint.

    :param locations: locations list from matrix params, i.e. [{"lon": x, "lat": y}, ...]

    :param response: API response object
    :type response: dict

    :param profile: Transportation mode being used
    :type profile: str

    :param options: Costing options being used.
    :type options: str

    :returns: Ouput feature with attributes and geometry set.
    :rtype: QgsFeature
    """

    feats = []
    sources = response['sources'][0]
    targets = response['targets'][0]
    for o, origin in enumerate(response['sources_to_targets']):
        from_id = "{}, {}".format(sources[o]['lon'], sources[o]["lat"])
        for d, destination in enumerate(origin):
            to_id = "{}, {}".format(targets[d]['lon'], targets[d]["lat"])
            time = destination['time']
            distance = destination['distance']

            if time:
                round(time / 3600, 3)

            feat = QgsFeature()
            feat.setAttributes([
                from_id,
                to_id,
                distance,
                time,
                profile,
                json.dumps(options),
                ]
            )
            feats.append(feat)

    return feats