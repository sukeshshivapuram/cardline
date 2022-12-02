
from odoo import api, models, fields
from num2words import num2words


class StockPicking(models.Model):
    _inherit = 'sale.order'

    customer_reference = fields.Char(string="Customer Reference")

    def calculation_amount(self,format_amount):
            str_con = str(format_amount)
            print("string form",str_con)
            # print("Fffformat amount",format_amount)
            # length_amount = len(str_con)
            # print("DDDDDddd ", length_amount)
            # slice_res_amount = str_con[:length_amount - 4]
            # print("SSSSSSSSs ", slice_res_amount)
            final_untaxed_amount = str_con + " " + "AED"
            print("JJJJJJf ", final_untaxed_amount)
            return final_untaxed_amount

    def calculations_total(self,):
        for rec in self:
            format_total = rec.tax_totals['formatted_amount_total']
            length_total = len(format_total)
            sliced_res_total = format_total[:length_total - 4]
            final_total = sliced_res_total +" "+"AED"
            return final_total

    def calculations_vat(self):
        for rec in self:
            format_vat = rec.tax_totals['groups_by_subtotal']['Untaxed Amount'][0]['formatted_tax_group_amount']
            length_vat = len(format_vat)
            slice_res_vat = format_vat[:length_vat - 4]
            final_vat = slice_res_vat +" "+"AED"
            return final_vat

    def calculations_untaxed_amt(self):
        for rec in self:
            format_untaxed_amt = rec.tax_totals['formatted_amount_untaxed']
            length_untaxed_amt = len(format_untaxed_amt)
            slice_res_untaxed_amt = format_untaxed_amt[:length_untaxed_amt - 4]
            final_untaxed_amt = slice_res_untaxed_amt +" "+"AED"
            return final_untaxed_amt


