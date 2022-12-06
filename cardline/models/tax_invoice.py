from odoo import models,fields,api


class TaxInvoiceReport(models.Model):
    _name = 'cardline.report'

class TaxInvoiceReportInherit(models.Model):
    _inherit = 'account.move'

    exchange_rate = fields.Float(string="Exchange Rate")
    currency = fields.Char(string="Currency")

    def total(self):
        total = 0
        for rec in self:
            for line in rec.invoice_line_ids:
                total = total + (line.quantity * line.price_unit)
                print(total)
        return total





    # def taxed_amount(self):
    #     for rec in self:
    #         for line in rec.invoice_line_ids:
    #             tax_amount = (line.quantity * line.price_unit)
    #             print(tax_amount)
    #     return tax_amount

    # def taxed_amount(self):
    #     for rec in self:
    #         for line in rec.invoice_line_ids:
    #             line.taxable_amount = (line.quantity * line.price_unit)
    #             print(line.taxable_amount)
    #     return line.taxable_amount


    def discount_calculate(self):
        discount = 0
        for rec in self:
            for line in rec.invoice_line_ids:
                # print("LLLLLLLLLL",line)
                print("line dis",line.discount)
                discount = discount + line.discount
                # print(discount)
        return discount

class InvoiceFormOrderLinesInherit(models.Model):
    _inherit = 'account.move.line'

    uom = fields.Float(string="UOM")
    taxable_amount = fields.Float(compute='compute_taxable_amount', string="Taxable Amount")


    def compute_taxable_amount(self):
        for list in self:
            print(list)
            list.taxable_amount = list.quantity * list.price_unit




