# -*- coding: utf-8 -*-
# Copyright (c) 2015-Present TidyWay Software Solution. (<https://tidyway.in/>)

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from reportlab.graphics import barcode


class tdzebrabarcodeProductLines(models.TransientModel):
    _name = "tdzebrabarcode.product.lines"

    product_id = fields.Many2one(
         'product.product',
         string='Product',
         required=True
         )
    qty = fields.Integer(
         'Barcode Labels Qty',
         default=1,
         required=True
         )
    wizard_id = fields.Many2one(
        'tdzebrabarcode.labels',
        string='Wizard'
        )


class tdzebrabarcodeLabels(models.TransientModel):
    _name = "tdzebrabarcode.labels"
    _description = 'Barcode Labels'

    @api.model
    def default_get(self, fields):
        product_get_ids = []
        if self._context.get('active_model') == 'product.product':
            record_ids = self._context.get('active_ids', []) or []
            products = self.env['product.product'].browse(record_ids)
            product_get_ids = [(0, 0, {
                                     'product_id': product.id,
                                     'qty': 1.0
                                     }) for product in products]
        elif self._context.get('active_model') == 'product.template':
            record_ids = self._context.get('active_ids', []) or []
            templates = self.env['product.template'].browse(record_ids)
            product_get_ids = []
            for template in templates:
                product_get_ids += [(0, 0, {
                             'product_id': product.id,
                             'qty': 1.0
                             }) for product in template.product_variant_ids]
        elif self._context.get('active_model') == 'purchase.order':
            record_ids = self._context.get('active_ids', []) or []
            purchase_recs = self.env['purchase.order'].browse(record_ids)
            product_get_ids = []
            for purchase in purchase_recs:
                for line in purchase.order_line:
                    if line.product_id and line.product_id.type != 'service':
                        product_get_ids += [(0, 0, {
                                 'product_id': line.product_id.id,
                                 'qty': int(abs(line.product_qty)) or 1.0
                                 })]
        elif self._context.get('active_model') == 'stock.picking':
            record_ids = self._context.get('active_ids', []) or []
            picking_recs = self.env['stock.picking'].browse(record_ids)
            product_get_ids = []
            for picking in picking_recs:
                for line in picking.move_lines:
                    if line.product_id and line.product_id.type != 'service':
                        product_get_ids += [(0, 0, {
                                 'product_id': line.product_id.id,
                                 'qty': int(abs(line.product_qty)) or 1.0
                                 })]
#         elif self._context.get('active_model') == 'mrp.production':
#             record_ids = self._context.get('active_ids', []) or []
#             mrp_recs = self.env['mrp.production'].browse(record_ids)
#             product_get_ids = []
#             for mrp in mrp_recs:
#                 for line in mrp.finished_move_line_ids:
#                     if line.product_id and line.product_id.type != 'service':
#                         product_get_ids += [(0, 0, {
#                                  'product_id': line.product_id.id,
#                                  'qty': int(abs(line.qty_done)) or 1.0
#                                  })]

        view_id = self.env['ir.ui.view'].search([('name', '=', 'report_product_tdzebrabarcode')])
        if not view_id.arch:
            raise Warning('Someone has deleted the reference '
                          'view of report, Please Update the module!')
        return {
                'product_get_ids': product_get_ids
                }

    product_get_ids = fields.One2many(
          'tdzebrabarcode.product.lines',
          'wizard_id',
          string='Products'
          )

    @api.multi
    def print_report(self):
        if not self.env.user.has_group('td_zebra_barcode_labels.group_zbarcode_labels'):
            raise Warning(_("You have not enough rights to access this "
                            "document.\n Please contact administrator to access "
                            "this document."))
        if not self.product_get_ids:
            raise Warning(_(""" There is no product lines to print."""))
        config_rec = self.env['tdzebrabarcode.configuration'].search([], limit=1)
        if not config_rec:
            raise Warning(_(" Please configure barcode data from "
                            "configuration menu"))
        datas = {
                 'ids': [x.product_id.id for x in self.product_get_ids],
                 'form': {
                    'barcode_height': config_rec.barcode_height or 300,
                    'barcode_width': config_rec.barcode_width or 1500,
                    'barcode_type': config_rec.barcode_type or 'EAN13',
                    'barcode_field': config_rec.barcode_field or '',
                    'display_width': config_rec.display_width,
                    'display_height': config_rec.display_height,
                    'humanreadable': config_rec.humanreadable,
                    'product_name': config_rec.product_name,
                    'product_variant': config_rec.product_variant,
                    'price_display': config_rec.price_display,
                    'product_code': config_rec.product_code or '',
                    'currency_position': config_rec.currency_position or 'after',
                    'currency': config_rec.currency and config_rec.currency.id or '',
                    'symbol': config_rec.currency and config_rec.currency.symbol or '',
                    'product_ids': [{
                         'product_id': line.product_id.id,
                         'qty': line.qty,
                         } for line in self.product_get_ids]
                      }
                 }
        browse_pro = self.env['product.product'].browse([x.product_id.id for x in self.product_get_ids])
        for product in browse_pro:
            barcode_value = product[config_rec.barcode_field]
            if not barcode_value:
                raise Warning(_('Please define barcode for %s!' % (product['name'])))
            try:
                barcode.createBarcodeDrawing(
                            config_rec.barcode_type,
                            value=barcode_value,
                            format='png',
                            width=int(config_rec.barcode_height),
                            height=int(config_rec.barcode_width),
                            humanReadable=config_rec.humanreadable or False
                            )
            except:
                raise Warning('Select valid barcode type according barcode '
                              'field value or check value in field!')

        return self.env.ref('td_zebra_barcode_labels.td_zebra_barcode_labels_11cm').report_action(self, data=datas)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
