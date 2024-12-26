# -*- coding: utf-8 -*-
{
    'name': 'HR Relatives',
    'version': '17.0.1.0.0',
    'category': 'Human Resources',
    'summary': """It helps you to keep your employee's relatives information """,
    'author': 'Arash Homayounfar',
    'company': 'Giladoo',
    'maintainer': 'Giladoo',
    'website': "https://www.giladoo.com/sdhr",
    'installable': True,
    'auto_install': False,
    'application': False,
    'depends': ['base', 'hr', 'sd_hr', 'sd_hr_documents'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/hr_employee_views.xml',
        'data/relative_type_data.xml',
    ],
    'demo': [
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
}
