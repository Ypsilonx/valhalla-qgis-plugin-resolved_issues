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


from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QColor

from qgis.core import (QgsPointXY,
                       QgsPolygon,
                       QgsFeature,
                       QgsField,
                       QgsFields,
                       QgsGeometry,
                       QgsSymbol,
                       QgsSimpleFillSymbolLayer,
                       QgsRendererCategory,
                       QgsCategorizedSymbolRenderer,
                       QgsProcessingUtils)
import processing

class Isochrones():
    """convenience class to build isochrones"""

    def __init__(self):

        # Will all be set in self.set_parameters(), bcs Processing Algo has to initialize this class before it
        # knows about its own parameters
        self.profile = None
        self.geometry = None
        self.id_field_type = None
        self.id_field_name = None

    def set_parameters(self, profile, geometry_param='LineString', id_field_type=QVariant.String, id_field_name='ID'):
        """
        Sets all parameters defined in __init__, because processing algorithm calls this class when it doesn't know its parameters yet.

        :param profile: Transportation mode being used
        :type profile: str

        :param geometry_param: geometry parameter for Valhalla isochrone service.
        :type geometry_param: str

        :param id_field_type: field type of ID field
        :type id_field_type: QVariant enum

        :param id_field_name: field name of ID field
        :type id_field_name: str
        """
        self.profile = profile
        self.geometry = geometry_param
        self.id_field_type = id_field_type
        self.id_field_name = id_field_name

    def get_fields(self):
        """
        Set all fields for output isochrone layer.

        :returns: Fields object of all output fields.
        :rtype: QgsFields
        """
        fields = QgsFields()
        fields.append(QgsField(self.id_field_name, self.id_field_type))  # ID field
        fields.append(QgsField('contour', QVariant.Int))  # Dimension field
        fields.append(QgsField("profile", QVariant.String))
        fields.append(QgsField('options', QVariant.String))

        return fields

    def get_features(self, response, id_field_value, options=''):
        """
        Generator to return output isochrone features from response.

        :param response: API response
        :type response: dict

        :param id_field_value: Value of ID field.
        :type id_field_value: any

        :param options: costing options
        :type options: str

        :returns: output feature
        :rtype: QgsFeature
        """

        # Sort features based on the isochrone value, so that longest isochrone
        # is added first. This will plot the isochrones on top of each other.
        l = lambda x: x['properties']['contour']
        for isochrone in sorted(response['features'], key=l, reverse=True):
            feat = QgsFeature()
            coordinates = isochrone['geometry']['coordinates']
            iso_value = isochrone['properties']['contour']
            if self.geometry == 'Polygon':
                qgis_coords = [[QgsPointXY(coord[0], coord[1]) for coord in coordinates[0]]]
                feat.setGeometry(QgsGeometry.fromPolygonXY(qgis_coords))
            if self.geometry == 'LineString':
                qgis_coords = [QgsPointXY(coord[0], coord[1]) for coord in coordinates]
                feat.setGeometry(QgsGeometry.fromPolylineXY(qgis_coords))
            feat.setAttributes([
                id_field_value,
                int(iso_value),
                self.profile,
                options
            ])

            yield feat

    def stylePoly(self, layer):
        """
        Style isochrone polygon layer.

        :param layer: Polygon layer to be styled.
        :type layer: QgsMapLayer
        """

        field = layer.fields().lookupField('contour')
        unique_values = sorted(layer.uniqueValues(field))

        colors = {0: QColor('#2b83ba'),
                  1: QColor('#64abb0'),
                  2: QColor('#9dd3a7'),
                  3: QColor('#c7e9ad'),
                  4: QColor('#edf8b9'),
                  5: QColor('#ffedaa'),
                  6: QColor('#fec980'),
                  7: QColor('#f99e59'),
                  8: QColor('#e85b3a'),
                  9: QColor('#d7191c')}

        categories = []

        for cid, unique_value in enumerate(unique_values):
            # initialize the default symbol for this geometry type
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())

            # configure a symbol layer
            symbol_layer = QgsSimpleFillSymbolLayer(color=colors[cid],
                                                    strokeColor=QColor('#000000'))

            # replace default symbol layer with the configured one
            if symbol_layer is not None:
                symbol.changeSymbolLayer(0, symbol_layer)

            # create renderer object
            category = QgsRendererCategory(unique_value, symbol, str(unique_value) + ' mins')
            # entry for the list of category items
            categories.append(category)

        # create renderer object
        renderer = QgsCategorizedSymbolRenderer('contour', categories)

        # assign the created renderer to the layer
        if renderer is not None:
            layer.setRenderer(renderer)
        layer.setOpacity(0.5)

        layer.triggerRepaint()