# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Project Tags',
    'version': '11.0',
    'website': 'http://www.fossinfotech.com',
    'category': 'Projects & Tasks',
    'sequence': 14,
    'summary': '',
    'description': """
Project Tags
==================
This module adds Projected end dates and Health Indicators to Tasks/Projects.
    """,
    'author':  'FOSS INFOTECH PVT LTD',
    'website': 'www.fossinfotech.com',
    'license': 'Other proprietary',
    'depends': [
        'project','hr_timesheet',
    ],
    'data': [
        'views/project_views.xml',
        'views/project_status.xml',
            ],
    'demo': [
    ],
     'images': [
        'static/description/index.html',
        'static/description/icon.png',
        'static/description/banner.png',
        'static/description/images/1.png',
        'static/description/images/2.png',
        'static/description/images/4.png',
        'static/description/images/5.png',
        'static/description/images/6.png',
        'static/description/images/7.png',
        'static/description/images/8.png',
        'static/description/images/10.png',
        'static/description/images/main_screenshot.png',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': False,
}