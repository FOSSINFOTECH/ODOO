# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'CSS Support',
    'version': '11.0',
    'summary': '',
    'author': 'FOSS INFOTECH PVT LTD',
    'category': 'Generic Modules',
    'website': 'http://www.fossinfotech.com',
    'description': """CSS Support module for Odoo 11. This module fetches products from the Delivery Order for a particular 
                      customer using their mobile number or by their name. It helps create service tickets for each products 
                      and you can assign respective service enginners.""",
    'depends': ['base','product','sale', 'account','stock','project'],
    'data': [
        'security/css_security.xml',
        'security/ir.model.access.csv',
        'data/mail_support.xml',
        'data/css_sequence.xml',
        'views/css_views.xml',
            ],

    'images': [
    'static/description/images/banner.png',
    'static/description/images/icon.png',
    'static/description/index.html',
    ],
    
    'installable': True,
    'auto_install': False,
    'application': True,
}
