from odoo import models,fields,api
from num2words import num2words
# from odoo.tools import amount_to_text_en



class TaxInvoiceReport(models.Model):
    _name = 'cardline.report'

class TaxInvoiceReportInherit(models.Model):
    _inherit = 'account.move'

    exchange_rate = fields.Float(string="Exchange Rate")
    currency = fields.Char(string="Currency" ,default='AED')


    def total(self):
        total = 0
        for rec in self:
            for line in rec.invoice_line_ids:
                total = total + (line.quantity * line.price_unit)
                print(total)
        return round(total,3)

    # def set_amt_in_worlds(self):
    #     amount, currency = self.amount_total, self.currency_id.name
    #     amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency=currency)
    #     if currency == 'INR':
    #         amount_in_words = str(amount_in_words).replace('INR', 'rupees')
    #         amount_in_words = str(amount_in_words).replace('Cents', 'paise')
    #         amount_in_words = str(amount_in_words).replace('Cent', 'paise')
    #     amount_in_words += '\tonly'
    #     self.amt_in_words = amount_in_words.capitalize()
    #
    # amt_in_words = fields.Char(compute='set_amt_in_worlds')

    # def amount_text(self, total_sum):
    #     # total_amount =
    #     amount_text = num2words(total_sum,lang='en_IN')
    #     print(amount_text,"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    #     return amount_text.title()

    def amount_text(self, total):
        for rec in self:
            if rec.currency_id.name == "AED":
                # print("SSSSSSSS", total)
                # preci = round(total,3)
                # print(preci,"KKKKKKKKKKKKKKKKHHHHHHHHHHHHH)))))))))")
                splited_value = str(total)
                print(round(total,2), "AAAAAAAA")
                res = splited_value.split('.')
                print("RRRRRRRRR", res)
                dihrams = rec.currency_id.currency_unit_label
                fills = rec.currency_id.currency_subunit_label
                print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLL",fills)
                amount_txt_1 = num2words(int(splited_value.split(".")[0]))
                amount_txt_3 = amount_txt_1.replace("and", '' ,2)
                amount_txt_4 = amount_txt_3.replace("thous", 'thousand')
                amount_txt_2 = num2words(int(splited_value.split(".")[1]))
                print(int(splited_value.split(".")[1]),"ddddddddddddddkyui")

                y = len(splited_value.split(".")[1])
                print(y, "ssssssssssssssssssssssss")
                if y == 1:
                    final_output = dihrams + " " + amount_txt_4 + " " + fills + " " + amount_txt_2 + " " + 'zero' + " " +"only"
                else:

                    final_output = dihrams +" "+ amount_txt_4 + " " + fills + " " + amount_txt_2 + " " + "only"
                print(final_output, "TTTTTTTTTTTT")
                print(amount_txt_1, "TTTTTTTTTTTTqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq")
                print(amount_txt_3, "dsgfhjkl;jhgfqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq")
                print(amount_txt_4, "hhhhhhhhhhhhhkkkkkkkkkkqqqqqqqqqqqqqqqqq")
                print("PPPPPPPPPP", num2words(int(splited_value.split(".")[0])))
                print("PPPPPPPPPP", num2words(int(splited_value.split(".")[1])))
                return final_output.title()
            else:
                # if rec.currency_id.name == "INR" or rec.currency_id.name == "USD":
                    splited_value = str(total)
                    # print(splited_value, "AAAAAAAA")
                    res = splited_value.split('.')
                    print("RRRRRRRRR", res)
                    dihrams = rec.currency_id.currency_unit_label
                    fills = rec.currency_id.currency_subunit_label
                    amount_txt_1 = num2words(int(splited_value.split(".")[0]))
                    # amount_txt_3 = amount_txt_1.replace("and","")
                    amount_txt_2 = num2words(int(splited_value.split(".")[1]))
                    final_output1 = amount_txt_1 + " " + dihrams + " " + amount_txt_2 + " " + fills + " "
                    print(final_output1, "TTTTTTTTTTTT")
                    print("PPPPPPPPPP1", num2words(int(splited_value.split(".")[0])))
                    print("PPPPPPPPPP2", num2words(int(splited_value.split(".")[1])))
                    return final_output1.title()



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


    def add_tax_amount(self):
        for rec in self:
            print(rec)
            price_sub2 = rec.price_subtotal + rec.l10n_ae_vat_amount
            rec.price_subtotal = price_sub2
            print(price_sub2,'price sub2')
            print(rec.price_subtotal,"price_subtotal")
        return rec.price_subtotal





