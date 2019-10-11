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
from .directions_points_layer_auto import ValhallaRoutePointsLayerCarAlgo
from ..costing_params import CostingPedestrian

class ValhallaRoutePointsLayerPedestrianAlgo(ValhallaRoutePointsLayerCarAlgo):

    ALGO_NAME = 'directions_from_point_layer_pedestrian'

    COSTING = CostingPedestrian
    PROFILE = 'pedestrian'

    def createInstance(self):
        return ValhallaRoutePointsLayerPedestrianAlgo()
