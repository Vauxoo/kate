# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, api, models, _
from odoo.exceptions import UserError

STATE = ('open', 'paid')


class SaleSummaryReport(models.AbstractModel):
    _name = 'report.clearcorp_report.report_salessummary'

    def _get_products_with_qty(self, form_data):
        query = ("""
            SELECT
                sum(ail.quantity) AS qty,
                pt.name
            FROM account_invoice_line ail
                LEFT JOIN account_invoice ai ON ai.id = ail.invoice_id
                LEFT JOIN product_product pp ON pp.id = ail.product_id
                LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE ai.state IN %s AND date_invoice >= %s AND date_invoice <= %s
            GROUP BY pt.id

        """)
        params = (STATE, form_data['start_date'], form_data['end_date'])
        self.env.cr.execute(query, params)
        res = self.env.cr.dictfetchall()
        return res

    def _get_invoices_data(self, form_data, type):
        query = ("""
            SELECT
                ai.number,
                ai.date_invoice,
                p.name AS partner,
                cr.name as currency,
                cr.id as currency_id,
                cr.symbol as cr_symbol,
                ai.amount_untaxed,
                ai.residual,
                ai.amount_tax,
                ai.amount_total,
                ai.state

            FROM account_invoice ai
                LEFT JOIN res_partner p ON p.id = ai.partner_id
                LEFT JOIN res_currency cr ON cr.id = ai.currency_id
            WHERE
                ai.state IN %s
                AND date_invoice >= %s
                AND date_invoice <= %s
                AND ai.type IN %s

        """)
        params = (STATE, form_data['start_date'], form_data['end_date'], type)
        self.env.cr.execute(query, params)
        res = self.env.cr.dictfetchall()

        query = ("""
            SELECT
                cr.name as currency,
                cr.symbol as cr_symbol,
                sum(ai.amount_untaxed) AS amount_untaxed,
                sum(ai.residual) AS residual,
                sum(ai.amount_tax) AS amount_tax,
                sum(ai.amount_total) AS amount_total

            FROM account_invoice ai
                LEFT JOIN res_currency cr ON cr.id = ai.currency_id
            WHERE
                ai.state IN %s
                AND date_invoice >= %s
                AND date_invoice <= %s
                AND ai.type IN %s
            GROUP BY cr.id

        """)
        params = (STATE, form_data['start_date'], form_data['end_date'], type)
        self.env.cr.execute(query, params)
        res1 = self.env.cr.dictfetchall()

        return [res, res1]

    def _get_sales_summary_data(self, form_data):
        return {
            'products': self._get_products_with_qty(form_data),
            'invoices': self._get_invoices_data(form_data, ('out_invoice', 'in_invoice')),
            'credit_notes': self._get_invoices_data(form_data, ('out_refund', 'in_refund')),
            'start_date': form_data['start_date'],
            'end_date': form_data['end_date'],
            'user': self.env.user.name,
            'date': fields.Datetime.now()
        }

    @api.model
    def get_report_values(self, docids, data=None):
        if not data.get('form'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        salessummary_report = self.env['ir.actions.report']._get_report_from_name('clearcorp_report.report_salessummary')
        docargs = {
            'doc_ids': [],
            'doc_model': salessummary_report.model,
            'docs': [],
            'datas': self._get_sales_summary_data(form_data=data['form'])
        }
        return docargs
