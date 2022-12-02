
from odoo import api, models, fields
from num2words import num2words


class StockPicking(models.Model):
    _inherit = 'sale.order'

    customer_reference = fields.Char(string="Customer Reference")

    def calculations(self):
        for rec in self:
            # for lines in rec.order_lines:
            result = rec.tax_totals['formatted_amount_total']
            length = len(result)
            # print("lengthhhhhhh",length)
            slice_res = result[:length - 4]
            # print("sliced result",slice_res)
            # print("resulttttttttttttttttt",result)
            final = slice_res +" "+"AED"
            # print("finalllllllllll",final)
            return final




