# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Inward Quality',

    'summary': """
        Inward Quality""",

    'description': """
        Inward Quality is necessary to assess the received goods. 
        The goal is to check that the products correspond to the quality requirements agreed with the suppliers.
    """,

    'author': 'Foss Infotech Pvt Ltd',

    'website': 'www.fossinfotech.com',

    'category': 'Inventory',

    'version': '1.0',

    'depends': ['stock'],
    'data':
    [
        'wizard/quality_wiz_views.xml',
        'views/stock_views.xml',
        'views/res_config_settings_views.xml',
        'views/sequence_view.xml',
        'views/stock_quality_check_view.xml',
        'security/ir.model.access.csv',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.jpg',
        'static/description/index.html',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,


}
