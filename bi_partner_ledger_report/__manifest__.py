{
    'name': 'Prime Minds Consulting Pvt Ltd',
    'version': '16.0.0.0',
    'summary': 'Statement of account report',
    'author': 'Prime Minds',
    'website': 'https://www.primeminds.in',
    'category': 'Accounting',
    'description': """Statement of account report""",
    'license':'LGPL-3',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'reports/reports.xml',
        'reports/report_partnerledger.xml',
        'reports/report_aged_partner.xml',
        'wizard/partner_ledger.xml',
        'wizard/excel_report.xml',
        'wizard/account_aged_partner_balance.xml'

    ],
    'installable': True,
    'auto_install': False,
}


