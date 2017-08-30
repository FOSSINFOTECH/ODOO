# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Product Bundle',
    'version': '1.0',
    'category': 'Sale',
    'sequence': 10,
    'summary': 'Product Bundle with offer Products',
    'description': """
            This Module allows you to add offer products at the time of sale order
            """,
    'author': 'FOSS INFOTECH PVT LTD',
    'website': 'https://www.fossinfotech.com',
    'depends': ['sale', 'stock'
                ],
    'data': [
            'security/ir.model.access.csv',
            'views/sale_views.xml',
    ],
    'demo': [
    ],
    'images': [
        'static/description/banner.png',
    ],
    'css': [],
    'installable': True,
    'auto_install': True,
    'application': True,
}
