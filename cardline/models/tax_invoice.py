from odoo import models,fields,api
from num2words import num2words


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

    def amount_text(self, total_sum):
        # total_amount =
        amount_text = num2words(total_sum)
        return amount_text.title()




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
        discount1 = 0
        # discount2 = 0
        for rec in self:
            for line in rec.invoice_line_ids:
                # print("LLLLLLLLLL",line)
                print("line dis",line.discount)
                discount = (discount + line.taxable_amount)
                discount1 = (discount1 + line.price_subtotal)
                discount2 = discount - discount1
                print(discount)
                print(discount1)
                print(discount2)
        return discount2

class InvoiceFormOrderLinesInherit(models.Model):
    _inherit = 'account.move.line'

    uom = fields.Float(string="UOM")
    taxable_amount = fields.Float(compute='compute_taxable_amount', string="Taxable Amount")


    def compute_taxable_amount(self):
        for list in self:
            print(list)
            list.taxable_amount = list.quantity * list.price_unit




