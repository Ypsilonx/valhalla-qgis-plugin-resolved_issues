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

from valhalla.gui.common_gui import get_locations, get_costing_options
from valhalla.utils import transform


class Matrix:
    """Extended functionality for directions endpoint for GUI."""
    def __init__(self, dlg):
        """
        :param dlg: Main GUI dialog.
        :type dlg: QDialog
        """
        self.dlg = dlg

        self.locations = None
        self.costing_options = dict()

    def get_parameters(self):
        """
        Builds parameters across directions functionalities.

        :returns: All parameter mappings except for coordinates.
        :rtype: dict
        """

        # if self.dlg.optimization_group.isChecked():
        #     return self._get_optimize_parameters()

        # API parameters
        profile = self.dlg.routing_travel_combo.currentText()

        params = {
            'costing': profile,
            'id': 1,
        }

        self.locations = get_locations(self.dlg.routing_fromline_list)
        params['sources'] = self.locations
        params['targets'] = self.locations

        # Get Advanced parameters
        if self.dlg.routing_costing_options_group.isChecked():
            params['costing_options'] = dict()
            self.costing_options = params['costing_options'][profile] = get_costing_options(self.dlg.routing_costing_options_group, profile)

        return params