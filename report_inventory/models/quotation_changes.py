
from odoo import api, models, fields
from num2words import num2words


class StockPicking(models.Model):
    _inherit = 'sale.order'

    def calculate_total(self):
        total = 0
        for records in self:
            for line in records.order_line:
                total = total + line.product_id.list_price
        return round((total),2)

    # def final_total_value(self):
    #     total=0



