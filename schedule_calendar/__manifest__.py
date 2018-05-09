# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': '''Company's Meeting Schedule Details''',
    'version': '0.1',
    'author': 'FOSS INFOTECH PVT LTD',
    'sequence': 110,
    'category': 'Generic',
    'website': 'http://www.fossinfotech.com',
    'description': """This module contains the details of \n
* Individual person's Meetings details,\n
* Company Holidays \n
* Own Tasks Scheduled Details""",
    'depends': [
        'calendar',
        'base',
        'project',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/schedule_calendar_view.xml',
    ],

    'installable': True,
    'application': True,
}
