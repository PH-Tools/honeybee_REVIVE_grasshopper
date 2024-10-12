import math


# ----------------------------------------------------------------------------------------------------------------------
# -- Dayton ASHRAE Methods


def ashrae_saturation_vapor_pressure(t_kelvin: float):
    if t_kelvin <= 273.15:
        ln_p_ws = (
            -5674.5359 / t_kelvin
            - 5.1523058e-01
            - 9.6778430e-03 * t_kelvin
            + 6.2215701e-07 * math.pow(t_kelvin, 2)
            + 2.0747825e-09 * math.pow(t_kelvin, 3)
            - 9.4840240e-13 * math.pow(t_kelvin, 4)
            + 4.1635019 * math.log(t_kelvin)
        )
    else:
        ln_p_ws = (
            -5.8002206e03 / t_kelvin
            # + 1.3914993
            - 5.5162560
            - 4.8640239e-02 * t_kelvin
            + 4.1764768e-05 * math.pow(t_kelvin, 2)
            - 1.4452093e-08 * math.pow(t_kelvin, 3)
            + 6.5459673 * math.log(t_kelvin)
        )
    return math.exp(ln_p_ws) * 1000


def ashrae_relative_humidity(saturation: float, saturationPressure: float, _b_press=101325):
    return saturation / (1 - (1 - saturation) * (saturationPressure / _b_press)) * 100


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# -- LBT Methods


def lbt_saturation_vapor_pressure(t_kelvin: float):
    if t_kelvin <= 273.15:  # saturation vapor pressure below freezing
        ln_p_ws = (
            -5.6745359e03 / t_kelvin
            + 6.3925247
            - 9.677843e-03 * t_kelvin
            + 6.2215701e-07 * t_kelvin**2
            + 2.0747825e-09 * math.pow(t_kelvin, 3)
            - 9.484024e-13 * math.pow(t_kelvin, 4)
            + 4.1635019 * math.log(t_kelvin)
        )
    else:  # saturation vapor pressure above freezing
        ln_p_ws = (
            -5.8002206e03 / t_kelvin
            + 1.3914993
            - 4.8640239e-02 * t_kelvin
            + 4.1764768e-05 * t_kelvin**2
            - 1.4452093e-08 * math.pow(t_kelvin, 3)
            + 6.5459673 * math.log(t_kelvin)
        )
    return math.exp(ln_p_ws)


def lbt_partial_vapor_pressure(_lbt_svp_wb, _db_temp, _wet_bulb, _b_press=101325):
    return _lbt_svp_wb - (_b_press * 0.000662 * (_db_temp - _wet_bulb))


def lbt_rel_humidity(_p_w, _lbt_svp_db):
    return (_p_w / _lbt_svp_db) * 100


DRY_BULB = -15.2
WET_BULB = -16.3

# DRY_BULB = 39.0
# WET_BULB = 28.6

print("- " * 50)
ashrae_svp_db = ashrae_saturation_vapor_pressure(DRY_BULB + 273.15)
ashrae_svp_wb = ashrae_saturation_vapor_pressure(WET_BULB + 273.15)

wss = 0.62198 * ashrae_svp_wb / (101325 - ashrae_svp_wb)
w = ((2501 - 2.381 * WET_BULB) * wss - (DRY_BULB - WET_BULB)) / (2501 + 1.805 * DRY_BULB - 4.186 * WET_BULB)
ws = 0.62198 * ashrae_svp_db / (101325 - ashrae_svp_db)
saturation = w / ws

ashrae_rh = ashrae_relative_humidity(saturation, ashrae_svp_db)
print(f"{ashrae_svp_db= :,.2f}")
print(f"{ashrae_svp_wb= :,.2f}")
print(f"{ashrae_rh= :,.2f}")

print("- " * 50)
lbt_svp_db = lbt_saturation_vapor_pressure(DRY_BULB + 273.15)
lbt_svp_wb = lbt_saturation_vapor_pressure(WET_BULB + 273.15)
lbt_pw = lbt_partial_vapor_pressure(lbt_svp_wb, DRY_BULB, WET_BULB)
lbt_rh = lbt_rel_humidity(lbt_pw, lbt_svp_db)
print(f"{lbt_svp_db= :,.2f}")
print(f"{lbt_svp_wb= :,.2f}")
print(f"{lbt_pw= :,.2f}")
print(f"{lbt_rh= :,.2f}")
