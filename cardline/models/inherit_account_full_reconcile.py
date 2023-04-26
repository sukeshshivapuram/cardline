from odoo import models, fields



class AccountFullReconcileInherit(models.Model):
    _inherit = 'account.full.reconcile'

    name = fields.Char(string='Number', required=False, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('account.reconcile'))
