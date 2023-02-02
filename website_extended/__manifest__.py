# -*- coding: utf-8 -*-
{
    # Module information
    "name": "eCommerce Extended",
    'version': '15.0.0',
    "summary": "eCommerce Extended for Development",
    'license': 'OPL-1',
    "category": "eCommerce",
    "depends": ['website', 'website_event'],
    "data": [
        'templates/footer.xml',
        'templates/templates.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            "website_extended/static/src/scss/website.scss",
        ],
        'web._assets_common_styles': [
            "website_extended/static/src/scss/fonts.scss",
        ],
    },

    # Author
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'https://www.emiprotechnologies.com',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',

    "installable": True,
    'auto_install': False
}
