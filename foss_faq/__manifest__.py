# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Frequently Asked Questions',
    'version': '13.0.0.0.0',
    'summary': 'Create FAQs',
    'author': 'FOSS INFOTECH PVT LTD',
    'live_test_url': 'https://www.youtube.com/watch?v=fk2kGe5nMRg',
    'license': 'AGPL-3',
    'category': 'FAQ',
    'website': 'http://www.fossinfotech.com',
    'depends': [
        'base', 'web', 'mail'
    ],
    'data': [
        'security/faq_security.xml',
        'security/ir.model.access.csv',
        'views/faq_view.xml',
        'views/category.xml',
        'views/tag.xml',
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
