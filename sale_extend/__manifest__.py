# -*- coding: utf-8 -*-
{
    'name': "Personaliser le module vente",
    'summary': """Personaliser le module vente""",
    'description': """Personaliser le module vente""",
    'author': "Moaad Bourhim",
    'category': 'Sales/Sales',
    'version': '15.0.0.1',
    'depends': ['base', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/sale_order.xml',
        'views/sale_order_line.xml',
        'views/stock_picking.xml',
        'report/sale_layout.xml',
        'report/sale_report_agora_template.xml',
        'report/picking_layout.xml',
        'report/picking_report_efcmd_template.xml',
        'wizard/calculate_formula_wizard.xml',
    ],
}
