""" -*- coding: utf-8 -*-
 Part of Odoo. See LICENSE file for full copyright and licensing details."""
# pylint: disable=E0401
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools.misc import get_lang, format_date

GOOGLE_CALENDAR_URL = 'https://www.google.com/calendar/render?'


class Event(models.Model):
    """ Class to contain functions regarding Events """
    # pylint: disable=too-few-public-methods
    _inherit = "event.event"

    @api.model
    def _search_build_dates(self):
        today = fields.Datetime.today()

        def sdn(date):
            return fields.Datetime.to_string(date.replace(hour=23, minute=59, second=59))

        def sd(date):
            return fields.Datetime.to_string(date)

        def get_month_filter_domain(filter_name, months_delta):
            first_day_of_the_month = today.replace(day=1)
            filter_string = _('This month') if months_delta == 0 \
                else format_date(self.env, value=today + relativedelta(months=months_delta),
                                 date_format='LLLL', lang_code=get_lang(self.env).code).capitalize()
            return [filter_name, filter_string, [
                ("date_end", ">=", sd(first_day_of_the_month + relativedelta(months=months_delta))),
                ("date_begin", "<", sd(first_day_of_the_month + relativedelta(months=months_delta+1)
                                       ))], 0]

        return [
            ['all', _('All Events'), [(1, '=', 1)], 0],
            ['today', _('Today'), [("date_end", ">", sd(today)), ("date_begin", "<", sdn(today))],
             0],
            get_month_filter_domain('month', 0),
            ['old', _('Past Events'), [("date_end", "<", sd(today))], 0],
        ]
