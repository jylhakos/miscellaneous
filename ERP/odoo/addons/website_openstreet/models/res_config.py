# -*- coding: utf-8 -*-
from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def get_default_website_leaflet_enable(self):
        return self.env['ir.config_parameter'].get_param("website_leaflet_enable")

    @api.model
    def get_default_website_leaflet_lat(self):
        return self.env['ir.config_parameter'].get_param("website_leaflet_lat")

    @api.model
    def get_default_website_leaflet_lng(self):
        return self.env['ir.config_parameter'].get_param("website_leaflet_lng")

    @api.model
    def get_default_website_leaflet_size(self):
        return self.env['ir.config_parameter'].get_param("website_leaflet_size")

    @api.model
    def get_default_save_location(self):
        return self.env['ir.config_parameter'].get_param("save_location")

    website_leaflet_enable = fields.Boolean("Location Map", default=get_default_website_leaflet_enable)
    website_leaflet_lat = fields.Float('Lat:', default=get_default_website_leaflet_lat, digits=(8, 12))
    website_leaflet_lng = fields.Float('Lng:', default=get_default_website_leaflet_lng, digits=(8, 12))
    website_leaflet_size = fields.Integer("Size:", default=get_default_website_leaflet_size)
    save_location = fields.Boolean(default=get_default_save_location)

    #if (website_leaflet_enable == True):
    #    save_location = False

    def set_website_leaflet(self):
        config_parameters = self.env['ir.config_parameter']
        config_parameters.set_param("website_leaflet_enable", self.website_leaflet_enable)
        config_parameters.set_param("save_location", True)

        #config_parameters.set_param("website_leaflet_lat", self.website_leaflet_lat)
        #config_parameters.set_param("website_leaflet_lng", self.website_leaflet_lng)
        #config_parameters.set_param("website_leaflet_size", self.website_leaflet_size)
        #company=self.env[]
        #main_company = self.sudo().env.ref('base.main_company')

        #street=self.env.company.street
        #street=main_company.street
        #_zip=main_company.zip
        #city=main_company.city
        #state=main_company.state_id
        #country=main_company.country_id
        #result = self._geo_localize(street,_zip,city,state,country)

        result = self._geo_localize(self.env.company.street,
                                        self.env.company.zip,
                                        self.env.company.city,
                                        self.env.company.state_id.name,
                                        self.env.company.country_id.name)

        config_parameters.set_param("website_leaflet_lat", result[0])
        config_parameters.set_param("website_leaflet_lng", result[1])
        config_parameters.set_param("website_leaflet_size", 400)


    def write(self, values):
        #values["save_location"] = False
        #result = super(ResConfigSettings, self).write(values)
        self.set_website_leaflet()
        result = super(ResConfigSettings, self).write(values)
        return result

    # res.company
    # self.env.company.id
    # company = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company_id.id)
    # company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company_id.id) 
    # self.env['res.company']._company_default_get('your.module')
    # self.env['res.company']._company_default_get()
    # company_id = self.env.company.id

    street = fields.Char()
    _zip = fields.Char(change_default=True)
    city = fields.Char()
    state = fields.Char()
    country = fields.Char()

    partner_latitude = fields.Float(string='Geo Latitude', digits=(8, 10))
    partner_longitude = fields.Float(string='Geo Longitude', digits=(8, 10))
    #lat = fields.Float(string='Lat', digits=(8, 16))
    #lng = fields.Float(string='Lng', digits=(8, 16))

    # Check whether to show warning for geolocalization
    #warning_save_location = fields.Boolean(default=True)

    date_localization = fields.Date(string='Geolocation Date')

    geoloc_provider_id = fields.Many2one(
        'base.geo_provider',
        string='API',
        config_parameter='base_geolocalize.geo_provider',
        default=lambda x: x.env['base.geocoder']._get_provider()
    )

    geoloc_provider_techname = fields.Char(related='geoloc_provider_id.tech_name', readonly=1)

    geoloc_provider_googlemap_key = fields.Char(
        string='Google Map API Key',
        config_parameter='base_geolocalize.google_map_api_key',
        help="Visit https://developers.google.com/maps/documentation/geocoding/get-api-key for more information."
    )

    @api.model
    def _geo_localize(self, street, zip, city, state, country):
        geo_obj = self.env['base.geocoder']
        search = geo_obj.geo_query_address(street=street, zip=zip, city=city, state=state, country=country)
        result = geo_obj.geo_find(search, force_country=country)
        if result is None:
            search = geo_obj.geo_query_address(city=city, state=state, country=country)
            result = geo_obj.geo_find(search, force_country=country)
        return result

    def geo_localize(self):
        street=self.env.company.street
        _zip=self.env.company.zip
        city=self.env.company.city
        state=self.env.company.state_id.name
        country=self.env.company.country_id.name

        config_parameters = self.env['ir.config_parameter']

        result = self._geo_localize(street,_zip,city,state,country)

        config_parameters.set_param("website_leaflet_enable", True)
        config_parameters.set_param("website_leaflet_lat", result[0])
        config_parameters.set_param("website_leaflet_lng", result[1])
        config_parameters.set_param("website_leaflet_size", 400)
        #config_parameters.set_param("save_location", True)

        #if result:
        #   website_leaflet_lat = result[0]
        #   website_leaflet_lng = result[1]
            #for partner in self.with_context(lang='en_US'):
             #   partner.write({})

        # 'date_localization': fields.Date.context_today(partner),
        #'website_leaflet_lat': result[0],
        #'website_leaflet_lng': result[1],
        return True
