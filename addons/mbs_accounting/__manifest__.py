{
    "name": "MBS Comptabilite Maroc",
    "version": "18.0.1.1.0",
    "summary": "Comptabilite marocaine, controles et reporting",
    "category": "Accounting/Accounting",
    "license": "LGPL-3",
    "depends": ["mbs_core", "mbs_commercial", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "views/report_wizard_views.xml"
    ],
    "installable": True,
    "application": True
}
