# -*- coding: utf-8 -*-
{
    'name': 'Mvola Payment Acquirer',
    'summary': 'MVOLA Payment Acquirer',
    'description': """MVOLA Payment Acquirer""",
    'category': 'Accounting',
    'version': '0.2',
    'depends': ['payment'],
    'website': 'https://www.kasia-itsolutions.com',
    'author': "KASIA SARL",
    'license': 'OPL-1',
    'data': [
        'views/payment_mvola_templates.xml',
        'data/payment_icon_data.xml',
        'data/payment_acquirer_data.xml',
        'views/payment_views.xml',
    ],
    'installable': True,
    'price': '100',
    'currency': 'EUR',
}
