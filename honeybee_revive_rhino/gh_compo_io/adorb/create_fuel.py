# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - ADORB Fuel Type"""

try:
    from honeybee_revive.fuels import Fuel
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_revive:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io, validators
    from ph_gh_component_io.input_tools import input_to_int
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))


# -----------------------------------------------------------------------------
# -- Grasshopper Interface

fuel_types = {1: "ELECTRICITY", 2: "NATURAL_GAS"}


class GHCompo_CreateADORBFuelType(object):
    purchase_price_per_kWH = validators.UnitCost_KWH("purchase_price_per_kWH", default=0.0)
    sales_price_per_kWH = validators.UnitCost_KWH("sales_price_per_kWH", default=0.0)

    def __init__(
        self,
        _DEBUG,
        _IGH,
        _fuel_type,
        _purchase_price_per_kWH,
        _sales_price_per_kWH,
        _annual_base_cost,
        *args,
        **kwargs
    ):
        # type: (bool, gh_io.IGH, str, float, float, float, list, dict) -> None
        print(_purchase_price_per_kWH)
        self.DEBUG = _DEBUG
        self.IGH = _IGH
        self.fuel_type = fuel_types[input_to_int(_fuel_type) or 1]
        self.purchase_price_per_kWH = _purchase_price_per_kWH
        print(self.purchase_price_per_kWH)
        self.sales_price_per_kWH = _sales_price_per_kWH
        self.annual_base_cost = _annual_base_cost or 0.0

    def run(self):
        # type: () -> Fuel
        return Fuel(
            _fuel_type=self.fuel_type,
            _purchase_price_per_kwh=self.purchase_price_per_kWH,
            _sale_price_per_kwh=self.sales_price_per_kWH,
            _annual_base_price=self.annual_base_cost,
        )
