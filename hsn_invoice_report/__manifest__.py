# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "HSN Invoice Report",

    'summary': """HSN based grouping of Products in Invoice""",

    'description': """
        This module adds a functionality for HSN based grouping of Products in Invoice.
    """,

    'live_test_url': 'https://www.youtube.com/watch?v=weZo2SaYuRU',

    'license': 'AGPL-3',

    'author': "FOSS INFOTECH PVT LTD",

    'website': "http://www.fossinfotech.com",

    'category': 'Accounting',
    
    'version': '12.0.0.0.0',

    'depends': ['account', 'l10n_in'],

    'data': [
        'report/reports.xml',
        'report/invoice_report_template.xml',
        'report/layout.xml',
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