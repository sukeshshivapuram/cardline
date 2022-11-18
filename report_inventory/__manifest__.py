# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Inventory Reports',
    'version': '0.6',
    'summary': 'Stock, GRN, DC and related changes',
    'sequence': 10,
    'description': """    """,
    'category': 'Inventory',
    'depends': ['base', 'stock','sale','account',],
    'data': [
        'reports/delivery_challan.xml',
        'reports/delivery_challan_template.xml',
        'views/quatation_inherit.xml',
        'views/delivery_note_template.xml',
        'views/fifth.xml',
        'views/default_terms_condition_changes.xml',

    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}