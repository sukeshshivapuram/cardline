
from odoo import api, models, fields
from num2words import num2words


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    exchange_rate = fields.Float(string='Exchange Rate')
    currency = fields.Char(string='Currency')



