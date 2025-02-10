# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Create REVIVE Residential Program."""

try:
    from ladybug_rhino.config import units_abbreviation
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee_energy.programtype import ProgramType
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from ph_units.converter import convert
    from ph_units.parser import parse_input
    from ph_units.unit_type import Unit
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io, validators
except ImportError:
    raise ImportError("\nFailed to import ph_gh_component_io")


def calc_mel_kWh_yr(_number_dwellings, _floor_area_ft2, _number_bedrooms, _phius_resnet_fraction=0.8):
    # type: (int, float, int, float) -> float
    """Calculate the Phius Misc. Electrical Loads (MEL) [kWh/year].

    ### Resnet 2014
    - https://codes.iccsafe.org/content/RESNET3012014P1/4-home-energy-rating-calculation-procedures-
    - Section 4.2.2.5(1): Energy Rating Reference Home
    - kWh = 413 + 0.91 * CFA + 69 * Nbr
    
    ### Phius Certification Guidebook v24.1.1 | Appendix N | N-7
    - https://www.phius.org/phius-certification-guidebook
    - "The basic protocol for lighting and miscellaneous electric loads is that they are calculated at 
    80% of RESNET (2013) levels for the 'Rated Home'."
    - kWh = num_units * (413 + 69 * Nbr + 0.91 * CFA) * 0.8
    """
    DWELLING_TV_KWH_YR = 413
    BEDROOM_TV_KWH_YR = 69
    MELS_KWH_YR_FT2 = 0.91

    a = DWELLING_TV_KWH_YR
    b = BEDROOM_TV_KWH_YR * _number_bedrooms
    c = MELS_KWH_YR_FT2 * _floor_area_ft2

    return _number_dwellings * (a + b + c) * _phius_resnet_fraction


def calc_lighting_int_kWh_yr(_number_dwellings, _floor_area_ft2, _lighting_int_HE_frac=1.0, _phius_resnet_fraction=0.8):
    # type: (int, float, float, float) -> float
    """Calculate the Phius MF Interior Lighting [kWh/year].

    ### Resnet 2014
    - https://codes.iccsafe.org/content/RESNET3012014P1/4-home-energy-rating-calculation-procedures-
    - Section 4.2.2.5.2.2: Interior Lighting
    - kWh/yr = 0.8 * [(4 - 3 * q_FFIL) / 3.7] * (455 + 0.8 * CFA) + 0.2 * (455 + 0.8 * CFA)
    
    ### Phius Certification Guidebook v24.1.1 | Appendix N | N-7
    - https://www.phius.org/phius-certification-guidebook
    - "The basic protocol for lighting and miscellaneous electric loads is that they are calculated at 
    80% of RESNET (2013) levels for the 'Rated Home'. ... The RESNET lighting formulas have been expressed more 
    compactly here but are algebraically equivalent to the published versions."
    - kWh/yr = n_unit * (0.2 + 0.8 * (4 - 3 * q_FFIL) / 3.7) * (455 + 0.8 * iCFA) * 0.8
    """
    INT_LIGHTING_W_PER_DWELLING = 455
    INT_LIGHTING_W_FT2 = 0.8

    a = 0.2 + 0.8 * (4 - 3 * _lighting_int_HE_frac) / 3.7
    b = INT_LIGHTING_W_PER_DWELLING + (INT_LIGHTING_W_FT2 * _floor_area_ft2)

    return _number_dwellings * a * b * _phius_resnet_fraction


def calc_lighting_ext_kWh_yr(_number_dwellings, _floor_area_ft2, _lighting_ext_HE_frac=1.0, _phius_resnet_fraction=0.8):
    # type: (int, float, float, float) -> float
    """Calculate the Phius MF Exterior Lighting [kWh/year].

    ### Resnet 2014
    - https://codes.iccsafe.org/content/RESNET3012014P1/4-home-energy-rating-calculation-procedures-
    - Section 4.2.2.5.2.3: Exterior Lighting
    - kWh = (100+0.05*FCA)*(1-FF_El)+0.25*(100+0.05*CFA)*FF_EL

    ### Phius Certification Guidebook v24.1.1 | Appendix N | N-7
    - https://www.phius.org/phius-certification-guidebook
    - "The basic protocol for lighting and miscellaneous electric loads is that they are calculated at 
    80% of RESNET (2013) levels for the 'Rated Home'. ... The RESNET lighting formulas have been expressed more 
    compactly here but are algebraically equivalent to the published versions."
    - kWh/yr = (1 - 0.75 * q_FFIL) * (100 + 0.05 * iCFA) * 0.8
    """
    EXT_LIGHTING_KWH_YR_PER_DWELLING = 100
    EXT_LIGHTING_KWH_YR_FT2 = 0.05

    a = EXT_LIGHTING_KWH_YR_PER_DWELLING * _number_dwellings
    b = EXT_LIGHTING_KWH_YR_FT2 * _floor_area_ft2
    e = 1 - 0.75 * _lighting_ext_HE_frac

    return e * (a + b) * _phius_resnet_fraction


def calc_lighting_garage_kWh_yr(_number_dwellings, _lighting_garage_HE_frac=1.0, _phius_resnet_fraction=0.8):
    # type: (int, float, float) -> float
    """Calculate the Phius MF Garage Lighting [kWh/year]."""
    GARAGE_LIGHTING_W = 100
    watts_per_dwelling = GARAGE_LIGHTING_W * (1 - _lighting_garage_HE_frac) + 25 * _lighting_garage_HE_frac

    return _number_dwellings * watts_per_dwelling * _phius_resnet_fraction


def calc_occupancy(_number_dwellings, _number_bedrooms):
    # type: (int, int) -> float
    return ((float(_number_bedrooms) / float(_number_dwellings)) + 1) * float(_number_dwellings)


class GHCompo_CreateReviveResidentialProgram(object):
    number_bedrooms = validators.IntegerPositiveValueOrZero("number_bedrooms", 0)
    number_dwellings = validators.IntegerPositiveValueOrZero("number_dwellings", 1)

    def __init__(self, _IGH, _icfa, _number_dwellings, _number_bedrooms, _base_program, *args, **kwargs):
        # type: (gh_io.IGH, float, int, int, ProgramType, list, dict) -> None
        self.IGH = _IGH
        self.number_dwellings = _number_dwellings
        self.number_bedrooms = _number_bedrooms
        self.base_program = _base_program

        # -- Figure out the input iCFA in M2
        _icfa_input_value, _icfa_input_unit = parse_input(self.value_with_area_unit(_icfa) or 0)
        _icfa_m2 = Unit(_icfa_input_value, (_icfa_input_unit or self.rh_doc_local_area_unit)).as_a("M2").value
        print("Converting: {} {} iCFA -> {} M2".format(_icfa_input_value, _icfa_input_unit, _icfa_m2))
        self.icfa_m2 = _icfa_m2

    @property
    def rh_doc_unit_type_abbreviation(self):
        # type: () -> str
        """Return the Rhino file's unit-type as a string abbreviation. ie: "Meter" -> "M", etc.."""
        return units_abbreviation().upper()

    @property
    def rh_doc_local_area_unit(self):
        # type: () -> str
        """Return the Rhino document unit-type for area as a string abbreviation. ie: "Meter" -> "M2", etc.."""
        return "{}2".format(self.rh_doc_unit_type_abbreviation)

    def value_with_area_unit(self, _value):
        # type: (str | float | None) -> str | None
        """ "Return a string of a value and a unit. If none is supplied, with use the Rhino-doc's unit type."""

        if _value is None:
            return None

        # -- If the user supplied an input unit, just use that
        input_value, input_unit = parse_input(_value)

        # -- otherwise use the Rhino document unit system as the input unit
        if not input_unit:
            input_unit = self.rh_doc_local_area_unit

        if input_value is None:
            raise ValueError("Failed to parse iCFA input: '{}'?".format(_value))

        return "{} {}".format(input_value, input_unit)

    @property
    def icfa_ft2(self):
        # type: () -> float
        """Return the iCFA in ft2."""
        return convert(self.icfa_m2, "M2", "FT2") or 0

    @property
    def ready(self):
        # type: () -> bool
        """Return True if the component is ready to run."""
        if not self.base_program or not self.icfa_m2 or not self.number_dwellings:
            return False
        if self.number_bedrooms == None:
            return False
        return True

    def run(self):
        # type: () -> None | ProgramType

        if not self.ready:
            return None

        new_program = self.base_program.duplicate()
        new_program.unlock()
        new_program.display_name = "REVIVE Residential Program [iCFA={}, DWL={}, BR={}]".format(
            self.icfa_m2, self.number_dwellings, self.number_bedrooms
        )

        # -- Set the program loads based on the building attributes
        # TODO: THIS IS WRONG.... GETTING KWH/YR, but WANT WATTS.... ? MAYBE?....
        mel_load = calc_mel_kWh_yr(self.number_dwellings, self.icfa_ft2, self.number_bedrooms)
        new_program.electric_equipment.watts_per_area = mel_load / self.icfa_m2

        lighting_load = calc_lighting_int_kWh_yr(self.number_dwellings, self.icfa_ft2)
        new_program.lighting.watts_per_area = lighting_load / self.icfa_m2

        total_occupancy = calc_occupancy(self.number_dwellings, self.number_bedrooms)
        new_program.people.area_per_person = self.icfa_m2 / total_occupancy
        new_program.lock()

        return new_program
