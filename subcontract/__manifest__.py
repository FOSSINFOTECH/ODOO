# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'MRP Subcontract Management',

    'summary': """Subcontract based on Manufacturing""",

    'description': """Subcontract feature in manufacturing is used for delivery of raw materials 
                    to the stores for the supplier. And also it is used for the production order of the products 
                    at the supplier's location and receipt of the finished products in the stores.""",

    'author': 'FOSS INFOTECH PVT LTD',

    'website': 'www.fossinfotech.com',

    'category': 'Manufacturing',

    'version': '1.0',
    
    'depends': ['mrp', 'purchase'],

    'data':
    [
        'views/subcontract_views.xml',
        'security/ir.model.access.csv',
    ],

    'images': 
    [
        'static/description/banner.png',
        'static/description/icon.jpg',
        'static/description/index.html',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
