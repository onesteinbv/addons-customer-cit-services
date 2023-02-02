"""
-*- coding: utf-8 -*-
"""
# pylint: disable=E0401
from werkzeug.datastructures import OrderedMultiDict
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.http import request
from odoo import http, _
from odoo.osv import expression
from odoo.addons.website.controllers.main import QueryURL


class WebsiteEventControllerExt(WebsiteEventController):
    """
    Contains functions regarding Website Events
    """

    def sitemap_event(env, rule, qs):
        """ :return: dict
        """
        if not qs or qs.lower() in '/events':
            yield {'loc': '/events'}

    @http.route(['/event', '/event/page/<int:page>', '/events', '/events/page/<int:page>'],
                type='http', auth="public", website=True, sitemap=sitemap_event)
    def events(self, page=1, **searches):
        """
        :return: template with values dict
        """
        Event = request.env['event.event']
        SudoEventType = request.env['event.type'].sudo()

        searches.setdefault('search', '')
        searches.setdefault('date', 'all')
        searches.setdefault('tags', '')
        searches.setdefault('type', 'all')
        searches.setdefault('country', 'all')

        website = request.website

        step = 12  # Number of events per page

        options = {
            'displayDescription': False,
            'displayDetail': False,
            'displayExtraDetail': False,
            'displayExtraLink': False,
            'displayImage': False,
            'allowFuzzy': not searches.get('noFuzzy'),
            'date': searches.get('date'),
            'tags': searches.get('tags'),
            'type': searches.get('type'),
            'country': searches.get('country'),
        }
        order = 'date_begin desc'
        if searches.get('date', 'all') == 'old':
            order = 'date_begin desc'
        order = 'is_published desc, ' + order
        search = searches.get('search')
        event_count, details, fuzzy_search_term = website._search_with_fuzzy(
            "events", search, limit=page * step, order=order, options=options)
        event_details = details[0]
        events = event_details.get('results', Event)
        events = events[(page - 1) * step:page * step]

        # count by domains without self search
        domain_search = [('name', 'ilike', fuzzy_search_term or searches['search'])
                         ] if searches['search'] else []

        no_date_domain = event_details['no_date_domain']
        dates = event_details['dates']
        for date in dates:
            if date[0] != 'old':
                date[3] = Event.search_count(
                    expression.AND(no_date_domain) + domain_search + date[2])

        no_country_domain = event_details['no_country_domain']
        countries = Event.read_group(expression.AND(no_country_domain) + domain_search,
                                     ["id", "country_id"], groupby="country_id",
                                     orderby="country_id")
        countries.insert(0, {
            'country_id_count': sum([int(country['country_id_count']) for country in countries]),
            'country_id': ("all", _("All Countries"))
        })

        search_tags = event_details['search_tags']
        current_date = event_details['current_date']
        current_type = None
        current_country = None

        if searches["type"] != 'all':
            current_type = SudoEventType.browse(int(searches['type']))

        if searches["country"] != 'all' and searches["country"] != 'online':
            current_country = request.env['res.country'].browse(int(searches['country']))

        pager = website.pager(
            url="/event",
            url_args=searches,
            total=event_count,
            page=page,
            step=step,
            scope=5)

        keep = QueryURL('/event', **{key: value for key, value in searches.items() if (
            key == 'search' or value != 'all')})

        searches['search'] = fuzzy_search_term or search

        values = {
            'current_date': current_date,
            'current_country': current_country,
            'current_type': current_type,
            'event_ids': events,  # event_ids used in website_event_track so we keep name as it is
            'dates': dates,
            'categories': request.env['event.tag.category'].search([('is_published', '=', True)]),
            'countries': countries,
            'pager': pager,
            'searches': searches,
            'search_tags': search_tags,
            'keep': keep,
            'search_count': event_count,
            'original_search': fuzzy_search_term and search,
        }

        if searches['date'] == 'old':
            # the only way to display this content is to set date=old so it must be canonical
            values['canonical_params'] = OrderedMultiDict([('date', 'old')])

        return request.render("website_event.index", values)
