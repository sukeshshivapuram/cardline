import time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from odoo import api, models, _
from odoo.tools import float_is_zero, DEFAULT_SERVER_DATE_FORMAT, float_repr

class BiReportPartnerLedger(models.AbstractModel):
    _name = 'report.bi_partner_ledger_report.bi_report_partnerledger'
    _description="Report Partner Ledger"

    def _lines(self, data, partner):
        print("in lines function (partner legder)||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
        print("dataaaaaaaaaaaaaaaaaaaaaa^^^^^",data)
        print("partnerrrrrrrrrrrrrraaaaaaaaaaaaaaaa&&&&&&&&a",partner)
        full_account = []
        currency = self.env['res.currency']
        print("currency",currency)
        if self._context.get('used_context'):
            print("if            self._context.get('used_context')",self._context.get('used_context'))
            query_get_data = self.env['account.move.line'].with_context(self._context.get('used_context'))._where_calc([
            ('company_id', '=', self.env.company.id)
        ]).get_sql()
            print("query_get_data",query_get_data)
        else:
            print("else          self._context.get('used_context')", self._context.get('used_context'))
            query_get_data = self.env['account.move.line']._where_calc([
            ('company_id', '=', self.env.company.id)
        ]).get_sql()
            print("query_get_data", query_get_data)
        reconcile_clause = "" if self._context['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        print(reconcile_clause,"KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK")
        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + \
                 query_get_data[2]
        print("paramas  ",params)
        query = """
            SELECT "account_move_line".id, "account_move_line".date, j.code, acc.code as a_code, acc.name as a_name, "account_move_line".ref, m.name as move_name, "account_move_line".name, "account_move_line".debit, "account_move_line".credit, "account_move_line".amount_currency,"account_move_line".currency_id,"account_move_line".date_maturity,"account_move_line".partner_id, c.symbol AS currency_code
            FROM """ + query_get_data[0] + """
            LEFT JOIN account_journal j ON ("account_move_line".journal_id = j.id)
            LEFT JOIN account_account acc ON ("account_move_line".account_id = acc.id)
            LEFT JOIN res_currency c ON ("account_move_line".currency_id=c.id)
            LEFT JOIN account_move m ON (m.id="account_move_line".move_id)
            WHERE "account_move_line".partner_id = %s
                AND m.state IN %s
                AND "account_move_line".account_id IN %s AND """ + query_get_data[1] + reconcile_clause + """
                ORDER BY "account_move_line".date"""
        self.env.cr.execute(query, tuple(params))
        res = self.env.cr.dictfetchall()
        print(res,"resssssssssssssssssssssssssssssss")
        sum = 0.0
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        for r in res:
            r['date'] = r['date']
            r['displayed_name'] = '-'.join(
                r[field_name] for field_name in ('move_name', 'ref', 'name')
                if r[field_name] not in (None, '', '/')
            )
            sum += r['debit'] - r['credit']
            r['progress'] = sum
            r['currency_id'] = currency.browse(r.get('currency_id'))
            full_account.append(r)
        print("full account",full_account)
        return full_account

    def _sum_partner(self, data, partner, field):
        print("In sum partner (partner legder)||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
        print(self._context)
        print(data,"dataaaaa")
        print(partner,"partnerrrrr")
        print(field,"fielddddddddd")
        if field not in ['debit', 'credit', 'debit - credit']:
            return
        result = 0.0
        print(self._context.get('used_context'), " print(self._context.get('used_context'))")
        # print(self._context['reconciled'], "self._context['reconciled']////////// in else")
        if self._context.get('used_context'):
            query_get_data = self.env['account.move.line'].with_context(self._context.get('used_context'))._where_calc([
            ('company_id', '=', self.env.company.id)
        ]).get_sql()
            print(query_get_data, "query_get_data in if")
        else:
            query_get_data = self.env['account.move.line']._where_calc([
            ('company_id', '=', self.env.company.id)
        ]).get_sql()
            print(query_get_data,"query_get_data in else")
            # print(self._context['reconciled'],"self._context['reconciled']////////// in else")
        reconcile_clause = "" if self._context['reconciled'] else ' AND "account_move_line".full_reconcile_id IS NULL '
        print("reconcile_clause\\\\\\\\\\\\\\\\\\",reconcile_clause)

        params = [partner.id, tuple(data['computed']['move_state']), tuple(data['computed']['account_ids'])] + \
                 query_get_data[2]
        print("paramsssss",params)
        query = """SELECT sum(""" + field + """)
                FROM """ + query_get_data[0] + """, account_move AS m
                WHERE "account_move_line".partner_id = %s
                    AND m.id = "account_move_line".move_id
                    AND m.state IN %s
                    AND account_id IN %s
                    AND """ + query_get_data[1] + reconcile_clause
        self.env.cr.execute(query, tuple(params))

        contemp = self.env.cr.fetchone()
        print(contemp,'----------------------------------------------')
        if contemp is not None:
            result = contemp[0] or 0.0
        print("resulttttttt",result)
        return result


    @api.model
    def _get_report_values(self, docids, data=None):
        print("IN get report values (partner ledger)|||||||||||||||||||||||||||||")
        print(self,"sssssssseeeeeeeeeeelllllllllllllllllllfffffffffff")
        print(docids,"dddddddddddoooooooooociiiiiiiiiidsss")
        print(data,"dataaaaaaaaaaaa")
        docs = data.get('docs')
        print(docs,"ddddocs")
        temp = []
        for a in docs:
            temp.append((self.env['res.partner'].browse(int(a))))
            print((self.env['res.partner'].browse(int(a))), "self.env['res.partner']//////////////")
        print(temp,"tttttttttempppppppppppppppp")
        print((self.env['res.partner'].browse(int(a))),"self.env['res.partner']//////////////")
        # print("?????????????????????????????")
        total = []
        model = self.env.context.get('active_model')
        print("model:::::::::::::::::::",model)
        docs = self.env['bi.account.aged.partner.balance'].browse(self.env.context.get('active_id'))
        print("doooocsss",docs)
        target_move = data.get('target_move', 'all')
        print("target valueeeee",target_move)
        date_from = data.get('date_from', time.strftime('%Y-%m-%d'))

        if ['result_selection'] == 'customer':
            account_type = ['asset_receivable']
        elif ['result_selection'] == 'supplier':
            account_type = ['liability_payable']
        else:
            account_type = ['liability_payable', 'asset_receivable']
        movelines, total, dummy = self._get_partner_move_lines(account_type, date_from, target_move,
                                                                   data['period_length'])
        print(self.ids,"self idsss")
        print(model,"model::::::::::::::")
        print(docs,"docs")
        print(movelines,"movelines")
        print(total,"total")

        abc = {
            # 'doc_ids': self.ids,
            # 'doc_model': model,
            # 'data': data,
            # 'docs': docs,
            # 'time': time,
            'get_partner_lines': movelines,
            'get_direction': total,
            'date_from': data.get('date_from'),
            'doc_ids': data.get('partner_ids'),
            'doc_model': self.env['res.partner'],
            'data': data.get('data'),
            'docs': temp,
            'time': time,
            'lines': self._lines,
            'extra': data,
            'sum_partner': self._sum_partner,
        }
        print("data.get('partner_ids')//",data.get('partner_ids'))
        print("data.get('data')//",data.get('data'))
        print("abc dict",abc)
        print("?????????????????????????????")
        return abc

    def _get_partner_move_lines(self, account_type, date_from, target_move, period_length):
        print("self?????????????????????????????????",self)
        print("in get partner move lines")
        print("accountype in get psrtnermove lines",account_type)
        periods = {}
        if self._context.get('report_type') == 'excel':
            start = date_from
            print("start in if",start)
        else:
            start = datetime.strptime(date_from, "%Y-%m-%d")
            print("start in else", start)
        for i in range(5)[::-1]:
            print("IN  for")
            stop = start - relativedelta(days=period_length)
            period_name = str((5 - (i + 1)) * period_length + 1) + '-' + str((5 - i) * period_length)
            period_stop = (start - relativedelta(days=1)).strftime('%Y-%m-%d')
            if i == 0:
                period_name = '+' + str(4 * period_length)
            periods[str(i)] = {
                'name': period_name,
                'stop': period_stop,
                'start': (i != 0 and stop.strftime('%Y-%m-%d') or False),
            }
            start = stop

        res = []
        total = []
        cr = self.env.cr
        print(cr,"cccccccccccccrrrrrrrrrrr")
        company_ids = self.env.context.get('company_ids', (self.env.user.company_id.id,))
        print("cpmpany ids",company_ids)
        move_state = ['draft', 'posted']
        if target_move == 'posted':
            print("IN IF")
            move_state = ['posted']
        arg_list = (tuple(move_state), tuple(account_type))
        print("arg_list",arg_list)
        reconciliation_clause = '(l.reconciled IS FALSE)'
        cr.execute('SELECT debit_move_id, credit_move_id FROM account_partial_reconcile where create_date > %s',
                   (date_from,))
        print("reconciliation_clause",reconciliation_clause)
        print("cr.fetchalll",cr.fetchall())
        reconciled_after_date = []
        for row in cr.fetchall():
            print("in second for")
            reconciled_after_date += [row[0], row[1]]
        if reconciled_after_date:
            reconciliation_clause = '(l.reconciled IS FALSE OR l.id IN %s)'
            arg_list += (tuple(reconciled_after_date),)
        arg_list += (date_from, tuple(company_ids))
        query = '''
            SELECT DISTINCT l.partner_id, UPPER(res_partner.name)
            FROM account_move_line AS l left join res_partner on l.partner_id = res_partner.id, account_account, account_move am
            WHERE (l.account_id = account_account.id)
                AND (l.move_id = am.id)
                AND (am.state IN %s)
                AND (account_account.account_type IN %s)
                AND ''' + reconciliation_clause + '''
                AND (l.date <= %s)
                AND l.company_id IN %s
            ORDER BY UPPER(res_partner.name)'''
        cr.execute(query, arg_list)

        partners = cr.dictfetchall()

        for i in range(7):
            total.append(0)

        partner_ids = [partner['partner_id'] for partner in partners if partner['partner_id']]
        lines = dict((partner['partner_id'] or False, []) for partner in partners)
        if not partner_ids:
            return [], [], {}

        undue_amounts = {}
        query = '''SELECT l.id
                FROM account_move_line AS l, account_account, account_move am
                WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                    AND (am.state IN %s)
                    AND (account_account.account_type IN %s)
                    AND (COALESCE(l.date_maturity,l.date) >= %s)\
                    AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                AND (l.date <= %s)
                AND l.company_id IN %s'''
        cr.execute(query, (
            tuple(move_state), tuple(account_type), date_from, tuple(partner_ids), date_from, tuple(company_ids)))
        aml_ids = cr.fetchall()
        aml_ids = aml_ids and [x[0] for x in aml_ids] or []
        for line in self.env['account.move.line'].browse(aml_ids):
            partner_id = line.partner_id.id or False
            if partner_id not in undue_amounts:
                undue_amounts[partner_id] = 0.0
            line_amount = line.balance
            if line.balance == 0:
                continue
            for partial_line in line.matched_debit_ids:
                if isinstance(date_from, str):
                    _date_from = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT)
                else:
                    _date_from = date_from

                if isinstance(partial_line.max_date, str):
                    if partial_line.max_date <= date_from:
                        line_amount += partial_line.amount
                else:
                    if isinstance(date_from, date):
                        if partial_line.max_date <= _date_from:
                            line_amount += partial_line.amount
                    else:
                        if partial_line.max_date <= _date_from.date():
                            line_amount += partial_line.amount

            for partial_line in line.matched_credit_ids:
                line_amount -= partial_line.amount
            if not self.env.user.company_id.currency_id.is_zero(line_amount):
                undue_amounts[partner_id] += line_amount
                lines[partner_id].append({
                    'line': line,
                    'amount': line_amount,
                    'period': 6,
                })

        history = []
        for i in range(5):
            args_list = (tuple(move_state), tuple(account_type), tuple(partner_ids),)
            dates_query = '(COALESCE(l.date_maturity,l.date)'

            if periods[str(i)]['start'] and periods[str(i)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (periods[str(i)]['start'], periods[str(i)]['stop'])
            elif periods[str(i)]['start']:
                dates_query += ' >= %s)'
                args_list += (periods[str(i)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (periods[str(i)]['stop'],)
            args_list += (date_from, tuple(company_ids))

            query = '''SELECT l.id
                    FROM account_move_line AS l, account_account, account_move am
                    WHERE (l.account_id = account_account.id) AND (l.move_id = am.id)
                        AND (am.state IN %s)
                        AND (account_account.account_type IN %s)
                        AND ((l.partner_id IN %s) OR (l.partner_id IS NULL))
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    AND l.company_id IN %s'''
            cr.execute(query, args_list)
            partners_amount = {}
            aml_ids = cr.fetchall()
            aml_ids = aml_ids and [x[0] for x in aml_ids] or []
            for line in self.env['account.move.line'].browse(aml_ids):
                partner_id = line.partner_id.id or False
                if partner_id not in partners_amount:
                    partners_amount[partner_id] = 0.0
                line_amount = line.balance
                if line.balance == 0:
                    continue
                for partial_line in line.matched_debit_ids:
                    if isinstance(date_from, str):
                        _date_from = datetime.strptime(date_from, DEFAULT_SERVER_DATE_FORMAT)
                    else:
                        _date_from = date_from

                    if isinstance(partial_line.max_date, str):
                        if partial_line.max_date <= date_from:
                            line_amount += partial_line.amount
                    else:
                        if isinstance(date_from, date):
                            if partial_line.max_date <= _date_from:
                                line_amount += partial_line.amount
                        else:
                            if partial_line.max_date <= _date_from.date():
                                line_amount += partial_line.amount
                for partial_line in line.matched_credit_ids:
                    line_amount -= partial_line.amount

                if not self.env.user.company_id.currency_id.is_zero(line_amount):
                    partners_amount[partner_id] += line_amount
                    lines[partner_id].append({
                        'line': line,
                        'amount': line_amount,
                        'period': i + 1,
                    })
            history.append(partners_amount)

        for partner in partners:
            if partner['partner_id'] is None:
                partner['partner_id'] = False
            at_least_one_amount = False
            values = {}
            undue_amt = 0.0
            if partner['partner_id'] in undue_amounts:
                undue_amt = undue_amounts[partner['partner_id']]

            total[6] = total[6] + undue_amt
            values['direction'] = undue_amt
            if not float_is_zero(values['direction'], precision_rounding=self.env.user.company_id.currency_id.rounding):
                at_least_one_amount = True

            for i in range(5):
                during = False
                if partner['partner_id'] in history[i]:
                    during = [history[i][partner['partner_id']]]

                total[(i)] = total[(i)] + (during and during[0] or 0)
                values[str(i)] = during and during[0] or 0.0
                if not float_is_zero(values[str(i)], precision_rounding=self.env.user.company_id.currency_id.rounding):
                    at_least_one_amount = True
            values['total'] = sum([values['direction']] + [values[str(i)] for i in range(5)])

            total[(i + 1)] += values['total']
            values['partner_id'] = partner['partner_id']
            if partner['partner_id']:
                browsed_partner = self.env['res.partner'].browse(partner['partner_id'])
                values['name'] = browsed_partner.name and len(browsed_partner.name) >= 45 and browsed_partner.name[
                                                                                              0:40] + '...' or browsed_partner.name
                values['trust'] = browsed_partner.trust
            else:
                values['name'] = _('Unknown Partner')
                values['trust'] = False

            if at_least_one_amount or (self._context.get('include_nullified_amount') and lines[partner['partner_id']]):
                res.append(values)
        print(res,"res")
        print(total,"total")
        print(lines,"lines")
        return res, total, lines

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     print("self:::::::::::::::::", self)
    #     print("docids:::::::::::::::::", docids)
    #     print("data:::::::::::::::::", data)
    #     total = []
    #     model = self.env.context.get('active_model')
    #     print("model:::::::::::::::::::",model)
    #     docs = self.env['bi.account.aged.partner.balance'].browse(self.env.context.get('active_id'))
    #     print("doooocsss",docs)
    #     target_move = data.get('target_move', 'all')
    #     print("target valueeeee",target_move)
    #     date_from = data.get('date_from', time.strftime('%Y-%m-%d'))
    #
    #     if ['result_selection'] == 'customer':
    #         account_type = ['asset_receivable']
    #     elif ['result_selection'] == 'supplier':
    #         account_type = ['liability_payable']
    #     else:
    #         account_type = ['liability_payable', 'asset_receivable']
    #     movelines, total, dummy = self._get_partner_move_lines(account_type, date_from, target_move,
    #                                                            data['period_length'])
    #     print(self.ids,"self idsss")
    #     print(model,"model::::::::::::::")
    #     print(docs,"docs")
    #     print(movelines,"movelines")
    #     print(total,"total")
    #     return {
    #         'doc_ids': self.ids,
    #         'doc_model': model,
    #         'data': data,
    #         'docs': docs,
    #         'time': time,
    #         'get_partner_lines': movelines,
    #         'get_direction': total,
    #     }

    # def remove_character(self,income):
    #     print("hi")
    #     print("IIIIIIIncome",income)
    #     for rec in self:
    #         ans = rec._sum_partner()
    #         print("reulst value in remove character fun",ans)
