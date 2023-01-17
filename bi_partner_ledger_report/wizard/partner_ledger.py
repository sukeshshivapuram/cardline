import base64
import io

import xlwt
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class Accounting_reportPartner_ledger(models.TransientModel):
    _name = "accounting_report.partner_ledger"
    _description="Accounting Report Partner Ledger"

    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    journal_ids = fields.Many2many('account.journal', string='Journals', required=True,
                                   default=lambda self: self.env['account.journal'].search([]))
    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')
    target_move = fields.Selection([('posted', 'All Posted Entries'),
                                    ('all', 'All Entries'),
                                    ], string='Target Moves', required=True, default='posted')
    amount_currency = fields.Boolean("With Currency",
                                     help="It adds the currency column on report if the currency differs from the company currency.")
    reconciled = fields.Boolean('Reconciled Entries')
    result_selection = fields.Selection([('customer', 'Receivable Accounts'),
                                         ('supplier', 'Payable Accounts'),
                                         ('customer_supplier', 'Receivable and Payable Accounts')
                                         ], string="Partner's", required=True, default='customer')
    customer_ids = fields.Many2one('res.partner', string='Customer')
    period_length = fields.Integer(string='Period Length (days)', required=True, default=30)


    def excel_header(self,worksheet):
        date_format = xlwt.XFStyle()
        date_format.num_format_str = 'dd/mm/yyyy'
        style_header = xlwt.easyxf(
            "font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center")
        style_table_header = xlwt.easyxf(
            "font: name Liberation Sans, bold on,color black; align: horiz center")

        worksheet.row(0).height_mismatch = True
        worksheet.row(0).height = 500
        worksheet.write_merge(0, 0, 0, 5, "Partner Ledger Report", style=style_header)
        worksheet.write(2, 0, 'Target Move')
        worksheet.write(2, 1, 'Start Date')
        worksheet.write(2, 2, 'End Date')
        worksheet.write(3, 0, 'All Posted Entries' if self.target_move == 'posted' else 'All Entries')
        worksheet.write(3, 1, self.date_from or '-', date_format)
        worksheet.write(3, 2, self.date_to or '-', date_format)
        worksheet.write(5, 0, 'Date')
        worksheet.write(5, 1, 'JRNL')
        worksheet.write(5, 2, 'Account')
        worksheet.write(5, 3, 'Ref')
        worksheet.write(5, 4, 'Debit')
        worksheet.write(5, 5, 'Credit')
        worksheet.write(5, 6, 'Balance')

    def print_partner_ledger(self):
        data = {}
        data['computed'] = {}
        obj_partner = self.env['res.partner']
        used_context = {'lang': 'en_US', 'strict_range': True, 'date_from': self.date_from,
                        'journal_ids': [a.id for a in self.journal_ids], 'date_to': self.date_to,
                        'state': self.target_move, 'reconciled': self.reconciled}
        print(used_context,"used_context")
        query_get_data = self.env['account.move.line'].with_context(used_context)._where_calc([
            ('company_id', '=', self.env.company.id)
        ]).get_sql()
        print(query_get_data,"query_get_data")
        data['computed']['move_state'] = ['draft', 'posted']
        if self.target_move == 'posted':
            data['computed']['move_state'] = ['posted']
        result_selection = self.result_selection
        if result_selection == 'supplier':
            data['computed']['ACCOUNT_TYPE'] = ['liability_payable']
        elif result_selection == 'customer':
            data['computed']['ACCOUNT_TYPE'] = ['asset_receivable']
        else:
            data['computed']['ACCOUNT_TYPE'] = ['liability_payable', 'asset_receivable']

        self.env.cr.execute("""
                    SELECT a.id
                    FROM account_account a
                    WHERE a.account_type IN %s
                    AND NOT a.deprecated""", (tuple(data['computed']['ACCOUNT_TYPE']),))
        data['computed']['account_ids'] = [a for (a,) in self.env.cr.fetchall()]
        params = [tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + query_get_data[2]
        reconcile_clause = "" if self.reconciled else ' AND "account_move_line".full_reconcile_id IS NULL '
        print(reconcile_clause,"AAAAAAAAAAAAAAAAAAAAAAAAAA reconcile_clause")
        query = """
                    SELECT DISTINCT "account_move_line".partner_id
                    FROM """ + query_get_data[0] + """, account_account AS account, account_move AS am
                    WHERE "account_move_line".partner_id IS NOT NULL
                        AND "account_move_line".account_id = account.id
                        AND am.id = "account_move_line".move_id
                        AND am.state IN %s
                        AND "account_move_line".account_id IN %s
                        AND NOT account.deprecated
                        AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))
        partner_ids = [res['partner_id'] for res in self.env.cr.dictfetchall()]
        partners = obj_partner.browse(partner_ids)
        partners = sorted(partners, key=lambda x: (x.ref or '', x.name or ''))
        docs = partners
        final_docs = [a.id for a in docs]
        final_dict = {
            'data': data,
            'docs': final_docs,
            'partner_ids': partner_ids,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'target_move': self.target_move,
            'amount_currency': self.amount_currency,
            'customer_ids': self.customer_ids.name,
            'period_length': self.period_length,
            'result_selection': self.result_selection,
        }
        print("Data dict of Parner ledger Report",final_dict)


        if self.period_length <= 0:
            raise UserError(_('You must set a period length greater than 0.'))
        if not self.date_from:
            raise UserError(_('You must set a start date.'))

        start_1 = self.date_from
        data_1 = {}
        res_1 = {}
        used_context_1 = {}
        for i in range(5)[::-1]:
            stop = start_1 - relativedelta(days=self.period_length - 1)
            res_1[str(i)] = {
                'name': (i != 0 and (
                        str((5 - (i + 1)) * self.period_length) + '-' + str((5 - i) * self.period_length)) or (
                                 '+' + str(4 * self.period_length))),
                'stop': start_1.strftime('%Y-%m-%d'),
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            # print("res str[i]///////////////", res_1[str(i)])
            start = stop - relativedelta(days=1)
        data_1['form'] = ({
            'target_move': self.target_move,
            'result_selection': self.result_selection,
            'period_length': self.period_length,
            'journal_ids': [a.id for a in self.env['account.journal'].search([])],
            'date_from': self.date_from,
            # 'partner_ids': self.partner_ids.name,
        })
        # print("data[form]/////", data_1['form'])
        used_context_1.update(
            {
                'state': self.target_move,
                'strict_range': True,
                'journal_ids': [a.id for a in self.env['account.journal'].search([])],
                'date_from': self.date_from

            }
        )
        # print("used context", used_context)
        data_1['form']['used_context_1'] = used_context_1
        # print("used context assigned to data[form]", data_1['form']['used_context'])
        data_1['form'].update(res_1)
        # print("data which is passed to report", data_1)

        final_dict['info'] = data_1
        print("finallllllllllllllllllllllllllllllllll",final_dict)
        print("infoooooooooooooooooooooo",final_dict['info']['form']['4']['name'])
        print("infoo3333333333333333333",final_dict['info']['form']['3']['name'])
        if self._context.get('report_type') != 'excel':
            return self.env.ref('bi_partner_ledger_report.bi_report_partnerledger_action').with_context(
                used_context).report_action(self, data=final_dict)
        else:
            filename = 'Partner Ledger.xls'
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('Sheet 1')
            self.excel_header(worksheet)

            date_format = xlwt.XFStyle()
            date_format.num_format_str = 'dd/mm/yyyy'
            style_header = xlwt.easyxf(
                "font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center")
            style_table_header = xlwt.easyxf(
                "font: name Liberation Sans, bold on,color black; align: horiz center")

            row = 6
            col = 0
            count = 1
            for partner in docs:
                if partner.ref:
                    worksheet.write(row, col, str(partner.ref) + " " + str(partner.name), style=style_table_header)
                else:
                    worksheet.write(row, col, str(partner.name), style=style_table_header)

                debit = self.env['report.bi_partner_ledger_report.bi_report_partnerledger'].with_context(
                    reconciled=self.reconciled, used_context=used_context)._sum_partner(final_dict['data'], partner,
                                                                                        'debit')
                credit = self.env['report.bi_partner_ledger_report.bi_report_partnerledger'].with_context(
                    reconciled=self.reconciled, used_context=used_context)._sum_partner(final_dict['data'], partner,
                                                                                        'credit')
                balance = self.env['report.bi_partner_ledger_report.bi_report_partnerledger'].with_context(
                    reconciled=self.reconciled, used_context=used_context)._sum_partner(final_dict['data'], partner,
                                                                                        'debit - credit')
                worksheet.write(row, col + 4, debit, style=style_table_header)
                worksheet.write(row, col + 5, credit, style=style_table_header)
                worksheet.write(row, col + 6, balance, style=style_table_header)
                row += 1
                for line in self.env['report.bi_partner_ledger_report.bi_report_partnerledger'].with_context(
                        reconciled=self.reconciled, used_context=used_context)._lines(final_dict['data'], partner):
                    if row > 50000:
                        count += 1
                        worksheet = workbook.add_sheet('Sheet ' + str(count))
                        self.excel_header(worksheet)
                        row=6
                        col=0

                    worksheet.write(row, col, line['date'], date_format)
                    worksheet.write(row, col + 1, line['code'])
                    worksheet.write(row, col + 2, line['a_code'])
                    worksheet.write(row, col + 3, line['displayed_name'])
                    worksheet.write(row, col + 4, line['debit'])
                    worksheet.write(row, col + 5, line['credit'])
                    worksheet.write(row, col + 6, line['progress'])
                    row += 1

            fp = io.BytesIO()
            workbook.save(fp)

            export_id = self.env['excel.report'].create(
                {'excel_file': base64.encodebytes(fp.getvalue()), 'file_name': filename})
            res = {
                'view_mode': 'form',
                'res_id': export_id.id,
                'res_model': 'excel.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'target': 'new'
            }
            return res

    # def print_report_aged_partner_1(self):
    #     if self.period_length <= 0:
    #         raise UserError(_('You must set a period length greater than 0.'))
    #     if not self.date_from:
    #         raise UserError(_('You must set a start date.'))
    #
    #     start_1 = self.date_from
    #     data_1 = {}
    #     res_1 = {}
    #     used_context = {}
    #     for i in range(5)[::-1]:
    #         stop = start - relativedelta(days=self.period_length - 1)
    #         res_1[str(i)] = {
    #             'name': (i != 0 and (
    #                     str((5 - (i + 1)) * self.period_length) + '-' + str((5 - i) * self.period_length)) or (
    #                              '+' + str(4 * self.period_length))),
    #             'stop': start.strftime('%Y-%m-%d'),
    #             'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
    #         }
    #         print("res str[i]///////////////", res_1[str(i)])
    #         start = stop - relativedelta(days=1)
    #     data_1['form'] = ({
    #         'target_move': self.target_move,
    #         'result_selection': self.result_selection,
    #         'period_length': self.period_length,
    #         'journal_ids': [a.id for a in self.env['account.journal'].search([])],
    #         'date_from': self.date_from,
    #         # 'partner_ids': self.partner_ids.name,
    #     })
    #     print("data[form]/////", data_1['form'])
    #     used_context.update(
    #         {
    #             'state': self.target_move,
    #             'strict_range': True,
    #             'journal_ids': [a.id for a in self.env['account.journal'].search([])],
    #             'date_from': self.date_from
    #
    #         }
    #     )
    #     print("used context", used_context)
    #     data_1['form']['used_context'] = used_context
    #     print("used context assigned to data[form]", data_1['form']['used_context'])
    #     data_1['form'].update(res_1)
    #     print("data which is passed to report", data_1)
    #     if not self._context.get('report_type') == 'excel':
    #         return self.env.ref('bi_partner_ledger_report.action_aged_partner_balance_report').with_context(
    #             landscape=True).report_action(self, data=data_1)
    #
    #     else:
    #         pass
            # filename = 'Aged Partner Balance.xls'
            # workbook = xlwt.Workbook()
            # worksheet = workbook.add_sheet('Sheet 1')
            # self.excel_header(worksheet, res)
            #
            # date_format = xlwt.XFStyle()
            # date_format.num_format_str = 'dd/mm/yyyy'
            # style_header = xlwt.easyxf(
            #     "font:height 300; font: name Liberation Sans, bold on,color black; align: horiz center")
            # style_table_header = xlwt.easyxf(
            #     "font: name Liberation Sans, bold on,color black; align: horiz center")
            #
            # row = 6
            # col = 0
            # count = 1
            # report_values = self.env['report.bi_partner_ledger_report.bi_report_agedpartnerbalance']._get_report_values(
            #     self, data=data)
            # if report_values['get_partner_lines']:
            #     worksheet.write(row, col, 'Account Total', style=style_table_header)
            #     worksheet.write(row, col + 1, report_values['get_direction'][6], style=style_table_header)
            #     worksheet.write(row, col + 2, report_values['get_direction'][4], style=style_table_header)
            #     worksheet.write(row, col + 3, report_values['get_direction'][3], style=style_table_header)
            #     worksheet.write(row, col + 4, report_values['get_direction'][2], style=style_table_header)
            #     worksheet.write(row, col + 5, report_values['get_direction'][1], style=style_table_header)
            #     worksheet.write(row, col + 6, report_values['get_direction'][0], style=style_table_header)
            #     worksheet.write(row, col + 7, report_values['get_direction'][5], style=style_table_header)
            # row += 1
            # for partner in report_values['get_partner_lines']:
            #     if row > 50000:
            #         count += 1
            #         worksheet = workbook.add_sheet('Sheet ' + str(count))
            #         self.excel_header(worksheet)
            #         row = 6
            #         col = 0
            #
            #     worksheet.write(row, col, partner['name'])
            #     worksheet.write(row, col + 1, partner['direction'])
            #     worksheet.write(row, col + 2, partner['4'])
            #     worksheet.write(row, col + 3, partner['3'])
            #     worksheet.write(row, col + 4, partner['2'])
            #     worksheet.write(row, col + 5, partner['1'])
            #     worksheet.write(row, col + 6, partner['0'])
            #     worksheet.write(row, col + 7, partner['total'])
            #     row += 1
            #
            # fp = io.BytesIO()
            # workbook.save(fp)
            #
            # export_id = self.env['excel.report'].create(
            #     {'excel_file': base64.encodebytes(fp.getvalue()), 'file_name': filename})
            # res = {
            #     'view_mode': 'form',
            #     'res_id': export_id.id,
            #     'res_model': 'excel.report',
            #     'view_type': 'form',
            #     'type': 'ir.actions.act_window',
            #     'target': 'new'
            # }
            # return res

