from odoo import models, fields, api



class AccountFullReconcileInherit(models.Model):
    _inherit = 'account.full.reconcile'

    name = fields.Char(string='Number', required=False, copy=False, default=lambda self: self.env['ir.sequence'].next_by_code('account.reconcile'))

class StockPickingInherit(models.Model):
    _inherit = 'purchase.order'


    due_date = fields.Date(string="Due Date")


    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            # order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
                self.date_approve = self.date_order

            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True







