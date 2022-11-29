from odoo import models,fields,api


class TaxInvoiceReport(models.Model):
    _name = 'cardline.report'

class TaxInvoiceReportInherit(models.Model):
    _inherit = 'account.move'

    exchange_rate = fields.Float(string="Exchange Rate")
    currency = fields.Char(string="Currency")

class InvoiceFormOrderLinesInherit(models.Model):
    _inherit = 'account.move.line'


    uom = fields.Float(string="UOM")
    taxable_amount = fields.Float(string="Taxable Amount")
