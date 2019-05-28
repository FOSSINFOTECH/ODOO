# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details. 

{
    'name': "Sale Revision",

    'summary': """Create and Apply Revision""",

    'description': """
        This module adds a functionality to manage different revisions and can be rolled back to any revision at anytime in Sales order.
    """,

    'author': "FOSS INFOTECH PVT LTD",

    'license': 'AGPL-3',

    'website': "http://www.fossinfotech.com",

    'category': 'Sale',

    'version': '12.0.0.0.0',

    'depends': ['sale', 'sale_management'],

    'data': [
        'security/ir.model.access.csv',
        'views/sale_revision_views.xml',
    ],
    
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/index.html'
    ],


    'installable': True,

    'auto_install': False,

    'application': True,
}