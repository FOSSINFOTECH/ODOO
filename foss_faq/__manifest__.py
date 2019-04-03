# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Frequently Asked Questions',
    'version': '12.0.0.0.0',
    'summary': 'Create FAQs',
    'author': 'FOSS INFOTECH PVT LTD',
    'license': 'AGPL-3',
    'category': 'FAQ',
    'website': 'http://www.fossinfotech.com',
    'description': """ 
        It enables the feature for FAQ.
        """,
    'depends': [
        'base', 'web', 'mail'
    ],
    'data': [
        'security/faq_security.xml',
        'security/ir.model.access.csv',
        'views/faq_view.xml',
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
