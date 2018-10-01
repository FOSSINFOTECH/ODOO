# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HSN Invoice Report',
    'version': '1.0',
    'summary': 'HSN based grouping of Products in Invoice',
    'author': 'FOSS INFOTECH PVT LTD',
    'category': 'Accounting',
    'website': 'http://www.fossinfotech.com',
    'description': """ 
                This module adds a functionality for HSN based grouping of Products in Invoice.
                """,
    'depends': [
        'account'
    ],
    'data': [
        "report/reports.xml",
        "report/invoice_report_template.xml",
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
