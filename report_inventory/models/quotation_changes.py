
from odoo import api, models, fields
from num2words import num2words
# from odoo.tools import amount_to_text_en



class StockPicking(models.Model):
    _inherit = 'sale.order'

    customer_reference = fields.Char(string="Customer Reference")
    currency_sale = fields.Char(string="Currency",default='AED')


    def calculation_amount(self,result):
        res = str(result)
        final = res +" "+"AED"
        sliced_amount = final[:len(final) - 4]
        amount_return = sliced_amount +" "
        return amount_return

    def discount_calculate_quotation(self):
        discount = 0
        discount1 = 0
        # discount2 = 0
        for rec in self:
            for line in rec.order_line:
                discount = (discount + line.taxable_amount)
                discount1 = (discount1 + line.price_subtotal)
                discount2 = discount - discount1
        return round(discount2,2)


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    taxable_amount = fields.Float(compute='compute_taxable_amount_sale',string="Taxable Amount")

    @api.depends('product_uom_qty', 'price_unit')
    def compute_taxable_amount_sale(self):
        for rec in self:
            print(rec.discount,"AAAAA")
            rec.taxable_amount = rec.product_uom_qty * rec.price_unit




class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    invoice_number_ref = fields.Char(string="Invoice No")
