# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Round Off Invoice Amount",

    'version': '12.0.0.0.0'
    ,
    'summary': """Rounding of Invoice Amount""",

    'description': """This module is to round the invoice (decimal amount) to the nearest value for Customer Invoice and Vendor Bills""",

    'license': 'AGPL-3',

    'author': "FOSS INFOTECH PVT LTD",

    'website': "www.fossinfotech.com",

    'category': 'Accounting',


    'depends': ['base','account'],

    'data': [
        'views/round_off_views.xml',
        'views/res_config_settings_views.xml',
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