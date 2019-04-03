# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Quotation Price History',

    'summary': """
        Purchase Quotation Price History""",

    'version': '12.0.0.0.0',
    
    'license': 'AGPL-3',

    'category': 'Purchase',

    'description': """
        Additional Purchase Feature.
        The given module allows you to create a copy and store all line item from purchase quotation form to Purchase Revision Tab
        , which can be used for future comparision.
            """,

    'author': 'FOSS INFOTECH PVT LTD',

    'website': 'https://www.fossinfotech.com',

    'depends': ['purchase', 'purchase_requisition'],
    'data': [
            'views/purchase_views.xml',
            'views/price_history_views.xml',
            'security/ir.model.access.csv',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.jpg',
        'static/description/index.html',
    ],

    'installable': True,
    'auto_install': True,
    'application': True,
}
