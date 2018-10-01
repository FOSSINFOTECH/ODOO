# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Sales Team Target Management',
    'version': '1.1',
    'summary': 'Sales Team Target Management',
    'author': 'FOSS INFOTECH PVT LTD',
    'category': 'Sales',
    'website': 'http://www.fossinfotech.com',
    'description': """This module helps in fixing a target to the sales team and also helps view the difference in the actual sales done and Planned target amount with a single click.""",
    'depends': [
        'base',
        'sale',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_engineer_target_view.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/index.html',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
