# -*- coding: utf-8 -*-
{
    'name': "Facture template",

    'summary': """
        Customisation Devis / Facture
        """,

    'description': """
        Customisation Devis / Facture
    """,

    'author': "KASIA SARL",
    'website': "https://kasia.mg",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': [
        'base',
        'contacts',
        'crm',
        'sale_management',
        'subscription_management',
        'om_account_accountant',
        'invoice_bulk_mailing',
    ],
    'data': [
        # views
        'views/res_partner_views.xml',
        'report/report_layout.xml',
        'report/report_sale_order.xml',
        'report/report_invoice_templates.xml',
    ],
}