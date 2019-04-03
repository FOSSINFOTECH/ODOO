# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': '''Company's Meeting Schedule Details''',
    'version': '12.0.0.0.0',
    'author': 'FOSS INFOTECH PVT LTD',
    'sequence': 10,
    'license': 'AGPL-3',
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
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/index.html',
    ],
    'installable': True,
    'application': True,
}
