# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class SalesSummaryWizard(models.TransientModel):
    _name = 'sales.summary.wizard'

    today = fields.Boolean(string='Today')
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)

    @api.onchange('today')
    def onchange_today(self):
        if self.today:
            self.start_date = self.end_date = fields.Date.today()

    @api.multi
    def action_print_report(self):
        self.ensure_one()
        [data] = self.read()
        datas = {
            'ids': [],
            'model': 'account.invoice',
            'form': data
        }
        return self.env.ref('clearcorp_report.action_report_sales_summary').with_context(from_transient_model=True).report_action(self.env['account.invoice'], data=datas)
