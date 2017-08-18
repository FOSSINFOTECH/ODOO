# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Assign/Unassign Followers',
    'version': '1.1',
    'summary': 'Assign and Unassign Followers',
    'sequence': 30,
    'description': """
Assign and Unassign Followers
====================
Odoo assign followers module. By using this module, we can assign bulk number of followers
to a particular record or N number of records. We can assign multiple followers to multiple of records using wizard.

Assign followers to a Record of any Model
++++++++++++++++++++++++++++++++++++++++
Step 1:  After installing the module go to Settings > Technical > Action > Assign followers

Step 2: Create a Model for assigning Followers to records with help of Name and choosing Model in the form. Save it and click “Add Action” button.

Step 3: It will shown in the Lead/Opportunity tree view more button. Now we can assign bulk number of followers to a particular record or N number of records.

Step 4: Now we can assign multiple followers to multiple of records using wizard.
    """,
    'author': 'Foss Infotech Pvt Ltd',
    'category': 'Tools',
    'website': 'https://www.fossinfotech.com/',
    'images': [],
    'depends': [],
    'data': [
        'view/assign_followers_view.xml'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
