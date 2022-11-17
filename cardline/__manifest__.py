# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Cardline Reports',
    'version': '0.6',
    'summary': 'Stock, GRN, DC and related changes',
    'sequence': 10,
    'description': """    """,
    'category': 'Inventory',
    'depends': ['base', 'stock','sale','account',],
    'data': [
        # 'views/quatation_inherit.xml',
        # 'views/fifth.xml',

        'views/tax_invoice_menu.xml',
        'report/tax_invoice.xml',
        'report/header.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}