# -*- coding: utf-8 -*-
{
    'name': "Purchase Customization",
    'summary': """Purchase Customization""",
    'description': """Purchase Customization""",
    'category': 'Purchase',
    'version': '15.0.0.1',
    'depends': ['base', 'purchase', 'sale'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_order.xml',
        'report/purchase_order_layout.xml',
        'report/purchase_order_efcmd_template.xml',
        'data/sequence.xml',
    ],
}
