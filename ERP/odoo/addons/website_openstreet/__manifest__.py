# -*- coding: utf-8 -*-
{
    'name': 'Website Location Map',
    'summary': '''Show the location on Contact us page.
    ''',
    'version': '14.9.0.0.1',
    'category': 'Website',
    'license': 'LGPL-3',
    'application': False,
    "auto_install": False,
    'installable': True,
    'depends': ['base', 'website', 'website_form', 'website_crm', 'website_partner', 'crm', 'base_setup'],
    'data': [
        'security/ir.model.access.csv',
        'views/website_openstreet_templates.xml',
        'data/data.xml',
    ],
    'images':[],
    "external_dependencies": {"python": [], "bin": []},

}