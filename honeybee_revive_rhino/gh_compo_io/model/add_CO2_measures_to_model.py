# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GH-Component Interface: HB-REVIVE - Add CO2-Reduction-Measures to Model."""


try:
    from honeybee.model import Model
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_revive.CO2_measures import CO2ReductionMeasure
    from honeybee_revive.properties.model import ModelReviveProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_revive:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError:
    raise ImportError("\nFailed to import ph_gh_component_io")


class GHCompo_AddCO2ReductionMeasuresToModel(object):

    def __init__(self, _IGH, _measures, _hb_model, *args, **kwargs):
        # type: (gh_io.IGH, list[CO2ReductionMeasure], Model | None, list, dict) -> None
        self.IGH = _IGH
        self.measures = _measures
        self.hb_model = _hb_model

    def run(self):
        # type: () -> Model | None

        if not self.hb_model:
            return None

        new_model_ = self.hb_model.duplicate()
        new_model_prop = getattr(new_model_.properties, "revive")  # type: ModelReviveProperties
        for measure in self.measures:
            if not measure:
                continue

            try:
                new_model_prop.co2_measures.add_measure(measure)
            except Exception as e:
                msg = "There as an error adding the measure: '{}' to the model.".format(measure)
                self.IGH.error(msg)
                raise e

        return new_model_
