# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'ClearCorp Sales Summary Reports',
    'summary': 'ClearCorp Sales Summary Reports',
    'sequence': 100,
    'description': """
Sales Summary Reports
=====================

    """,
    'category': 'Accounting',

    'depends': ['account'],

    'data': [

        'wizard/sales_summary_wizard_view.xml',

        'views/account_view.xml',

    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': False,
}
