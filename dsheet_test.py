"""
    File name: dsheet_test.py
    Author: Rob Swart (Mobilis TBI)
    Date last modified: 14/09/2020

    Script to test D-Sheet Geolib API
    Construction type: construction pit with sheet pile walls and struts
    Calculation type: EC7-NL Verify sheet piling

"""

from geolib import DSheetPilingModel
from geolib.geometry import Point
from geolib.models.dsheetpiling.calculation_options import StandardCalculationOptions, VerifyCalculationOptions, \
    CalculationOptionsPerStage, OverallStabilityCalculationOptions, KranzAnchorStrengthCalculationOptions, \
    DesignSheetpilingLengthCalculationOptions
from geolib.models.dsheetpiling.constructions import SheetPileProperties, Sheet
from geolib.models.dsheetpiling.dsheetpiling_model import SheetModelType
from geolib.models.dsheetpiling.loads import HorizontalLineLoad, Moment, UniformLoad, SurchargeLoad, NormalForce, \
    VerificationLoadSettings
from geolib.models.dsheetpiling.profiles import SoilLayer, SoilProfile
from geolib.models.dsheetpiling.settings import SheetPilingElementMaterialType, PassiveSide, \
    LateralEarthPressureMethodStage, Side, CalculationType, VerifyType, PartialFactorCalculationType, \
    PartialFactorSetEC7NADNL, DesignType, DesignPartialFactorSet, LoadTypePermanentVariable, \
    VerifyEurocodePartialFactorSet, LoadTypeFavourableUnfavourableMoment
from geolib.models.dsheetpiling.supports import Anchor, Strut, SpringSupport, RigidSupport, SupportType
from geolib.models.dsheetpiling.surface import Surface
from geolib.models.dsheetpiling.water_level import WaterLevel
from geolib.soils import Soil, GrainType, LambdaType, SoilTypeSettlementByVibration
from pathlib import Path


def calculate_sheet_pile():
    # Initialize model
    model = DSheetPilingModel()
    modeltype = SheetModelType(check_vertical_balance=False, method=LateralEarthPressureMethodStage.KA_KO_KP,
                               trildens_calculation=False, verification=True)
    # For check_vertical_balance a value for max point resistance is necessary, where to add it?
    model.set_model(modeltype)

    # Define sheet piles
    sheet_pile_properties_AZ18_700_S355 = SheetPileProperties(
        material_type=SheetPilingElementMaterialType.Steel,
        section_bottom_level=-20,
        elastic_stiffness_ei=7.938E+04,
        acting_width=1,
        mr_char_el=639,
        modification_factor_k_mod=1,
        material_factor_gamma_m=1,
        reduction_factor_on_maximum_moment=1,
        reduction_factor_on_ei=1,
        section_area=139,
        elastic_section_modulus_w_el=1800,
        coating_area=1.33,
        height=420.0
    )

    sheet_pile_properties_AZ20_700_S355 = SheetPileProperties(
        material_type=SheetPilingElementMaterialType.Steel,
        section_bottom_level=-20,
        elastic_stiffness_ei=8.6016E+04,
        acting_width=1,
        mr_char_el=690,
        modification_factor_k_mod=1,
        material_factor_gamma_m=1,
        reduction_factor_on_maximum_moment=1,
        reduction_factor_on_ei=1,
        section_area=152,
        elastic_section_modulus_w_el=1945,
        coating_area=1.33,
        height=421.0
    )

    sheet_pile_properties_AZ26_700_S355 = SheetPileProperties(
        material_type=SheetPilingElementMaterialType.Steel,
        section_bottom_level=-20,
        elastic_stiffness_ei=1.254120E+05,
        acting_width=1,
        mr_char_el=923,
        modification_factor_k_mod=1,
        material_factor_gamma_m=1,
        reduction_factor_on_maximum_moment=1,
        reduction_factor_on_ei=1,
        section_area=187,
        elastic_section_modulus_w_el=2600,
        coating_area=1.38,
        height=460.0
    )

    sheet_element = Sheet(name="AZ 20-700 S355", sheet_pile_properties=sheet_pile_properties_AZ20_700_S355)
    level_top = 0
    model.set_construction(top_level=level_top, elements=[sheet_element])

    # Define stages
    stage_initial = model.add_stage(
        name="Initial stage",
        passive_side=PassiveSide.DSHEETPILING_DETERMINED,
        method_left=LateralEarthPressureMethodStage.KA_KO_KP,
        method_right=LateralEarthPressureMethodStage.KA_KO_KP
    )

    stage_first_excavation = model.add_stage(
        name="First excavation",
        passive_side=PassiveSide.DSHEETPILING_DETERMINED,
        method_left=LateralEarthPressureMethodStage.KA_KO_KP,
        method_right=LateralEarthPressureMethodStage.KA_KO_KP
    )

    stage_strut = model.add_stage(
        name="Place struts",
        passive_side=PassiveSide.DSHEETPILING_DETERMINED,
        method_left=LateralEarthPressureMethodStage.KA_KO_KP,
        method_right=LateralEarthPressureMethodStage.KA_KO_KP
    )

    stage_wet_excavation = model.add_stage(
        name="Wet excavation",
        passive_side=PassiveSide.DSHEETPILING_DETERMINED,
        method_left=LateralEarthPressureMethodStage.KA_KO_KP,
        method_right=LateralEarthPressureMethodStage.KA_KO_KP
    )

    stage_pit_dry = model.add_stage(
        name="Pit dry",
        passive_side=PassiveSide.DSHEETPILING_DETERMINED,
        method_left=LateralEarthPressureMethodStage.KA_KO_KP,
        method_right=LateralEarthPressureMethodStage.KA_KO_KP
    )

    # Define soils

    # Set clay material
    soil_clay = Soil(name="Clay")
    soil_clay.soil_weight_parameters.unsaturated_weight = 10
    soil_clay.soil_weight_parameters.saturated_weight = 11
    soil_clay.mohr_coulomb_parameters.cohesion = 10
    soil_clay.mohr_coulomb_parameters.friction_angle = 17
    soil_clay.mohr_coulomb_parameters.friction_angle_interface = 11
    soil_clay.shell_factor = 1
    soil_clay.soil_state.ocr_layer = 1
    soil_clay.soil_classification_parameters.grain_type = GrainType.FINE
    soil_clay.subgrade_reaction_parameters.lambda_type = LambdaType.KOTTER
    soil_clay.subgrade_reaction_parameters.k_1_top_side = 4000
    soil_clay.subgrade_reaction_parameters.k_1_bottom_side = 4000
    soil_clay.subgrade_reaction_parameters.k_2_top_side = 2000
    soil_clay.subgrade_reaction_parameters.k_2_bottom_side = 2000
    soil_clay.subgrade_reaction_parameters.k_3_top_side = 800
    soil_clay.subgrade_reaction_parameters.k_3_bottom_side = 800

    # Set peat material
    soil_peat = Soil(name="Peat")
    soil_peat.soil_weight_parameters.unsaturated_weight = 10
    soil_peat.soil_weight_parameters.saturated_weight = 11
    soil_peat.mohr_coulomb_parameters.cohesion = 2
    soil_peat.mohr_coulomb_parameters.friction_angle = 20
    soil_peat.mohr_coulomb_parameters.friction_angle_interface = 0
    soil_peat.shell_factor = 1
    soil_peat.soil_state.ocr_layer = 1
    soil_peat.soil_classification_parameters.grain_type = GrainType.FINE
    soil_peat.subgrade_reaction_parameters.lambda_type = LambdaType.KOTTER
    soil_peat.subgrade_reaction_parameters.k_1_top_side = 2000
    soil_peat.subgrade_reaction_parameters.k_1_bottom_side = 2000
    soil_peat.subgrade_reaction_parameters.k_2_top_side = 800
    soil_peat.subgrade_reaction_parameters.k_2_bottom_side = 800
    soil_peat.subgrade_reaction_parameters.k_3_top_side = 500
    soil_peat.subgrade_reaction_parameters.k_3_bottom_side = 500

    # Set sand moderate material
    soil_sand_moderate = Soil(name="Sand moderate")
    soil_sand_moderate.soil_weight_parameters.unsaturated_weight = 17
    soil_sand_moderate.soil_weight_parameters.saturated_weight = 19
    soil_sand_moderate.mohr_coulomb_parameters.cohesion = 0
    soil_sand_moderate.mohr_coulomb_parameters.friction_angle = 32.5
    soil_sand_moderate.mohr_coulomb_parameters.friction_angle_interface = 21.7
    soil_sand_moderate.shell_factor = 1
    soil_sand_moderate.soil_state.ocr_layer = 1
    soil_sand_moderate.soil_classification_parameters.grain_type = GrainType.COARSE
    soil_sand_moderate.subgrade_reaction_parameters.lambda_type = LambdaType.KOTTER
    soil_sand_moderate.subgrade_reaction_parameters.k_1_top_side = 20000
    soil_sand_moderate.subgrade_reaction_parameters.k_1_bottom_side = 20000
    soil_sand_moderate.subgrade_reaction_parameters.k_2_top_side = 10000
    soil_sand_moderate.subgrade_reaction_parameters.k_2_bottom_side = 10000
    soil_sand_moderate.subgrade_reaction_parameters.k_3_top_side = 5000
    soil_sand_moderate.subgrade_reaction_parameters.k_3_bottom_side = 5000

    # Set sand dense material
    soil_sand_dense = Soil(name="Sand dense")
    soil_sand_dense.soil_weight_parameters.unsaturated_weight = 19
    soil_sand_dense.soil_weight_parameters.saturated_weight = 21
    soil_sand_dense.mohr_coulomb_parameters.cohesion = 0
    soil_sand_dense.mohr_coulomb_parameters.friction_angle = 35
    soil_sand_dense.mohr_coulomb_parameters.friction_angle_interface = 23.3
    soil_sand_dense.shell_factor = 1
    soil_sand_dense.soil_state.ocr_layer = 1
    soil_sand_dense.soil_classification_parameters.grain_type = GrainType.COARSE
    soil_sand_dense.subgrade_reaction_parameters.lambda_type = LambdaType.KOTTER
    soil_sand_dense.subgrade_reaction_parameters.k_1_top_side = 40000
    soil_sand_dense.subgrade_reaction_parameters.k_1_bottom_side = 40000
    soil_sand_dense.subgrade_reaction_parameters.k_2_top_side = 20000
    soil_sand_dense.subgrade_reaction_parameters.k_2_bottom_side = 20000
    soil_sand_dense.subgrade_reaction_parameters.k_3_top_side = 10000
    soil_sand_dense.subgrade_reaction_parameters.k_3_bottom_side = 10000

    # Add soils in model
    for soil in (soil_clay, soil_peat, soil_sand_moderate, soil_sand_dense):
        model.add_soil(soil)

    # Define soil profile
    profile_initial = SoilProfile(
        name="Profile initial",
        layers=[
            SoilLayer(top_of_layer=0, soil=soil_clay.name),
            SoilLayer(top_of_layer=-3, soil=soil_peat.name),
            SoilLayer(top_of_layer=-4, soil=soil_sand_moderate.name),
            SoilLayer(top_of_layer=-8, soil=soil_clay.name),
            SoilLayer(top_of_layer=-13, soil=soil_sand_moderate.name),
            SoilLayer(top_of_layer=-18, soil=soil_sand_dense.name)
        ]
    )

    profile_first_excavation = SoilProfile(
        name="Profile first excavation",
        layers=[
            SoilLayer(top_of_layer=0, soil=soil_clay.name),
            SoilLayer(top_of_layer=-3, soil=soil_peat.name),
            SoilLayer(top_of_layer=-4, soil=soil_sand_moderate.name),
            SoilLayer(top_of_layer=-8, soil=soil_clay.name, water_pressure_bottom=15),
            SoilLayer(top_of_layer=-13, soil=soil_sand_moderate.name, water_pressure_top=15, water_pressure_bottom=15),
            SoilLayer(top_of_layer=-18, soil=soil_sand_dense.name, water_pressure_top=15, water_pressure_bottom=15)
        ]
    )

    profile_pit_dry = SoilProfile(
        name="Profile pit dry",
        layers=[
            SoilLayer(top_of_layer=0, soil=soil_clay.name),
            SoilLayer(top_of_layer=-3, soil=soil_peat.name),
            SoilLayer(top_of_layer=-4, soil=soil_sand_moderate.name),
            SoilLayer(top_of_layer=-8, soil=soil_clay.name, water_pressure_bottom=70),
            SoilLayer(top_of_layer=-13, soil=soil_sand_moderate.name, water_pressure_top=70, water_pressure_bottom=70),
            SoilLayer(top_of_layer=-18, soil=soil_sand_dense.name, water_pressure_top=70, water_pressure_bottom=70)
        ]
    )

    for stage in [stage_initial, stage_first_excavation, stage_strut, stage_wet_excavation, stage_pit_dry]:
        model.add_profile(profile=profile_initial, side=Side.BOTH, stage_id=stage)

    for stage in [stage_first_excavation, stage_strut]:
        model.add_profile(profile=profile_first_excavation, side=Side.LEFT, stage_id=stage)

    for stage in [stage_pit_dry]:
        model.add_profile(profile=profile_pit_dry, side=Side.LEFT, stage_id=stage)

    # Define surfaces
    surface_ground_level = Surface(name="Initial surface level", points=[Point(x=0, z=0)])
    surface_first_excavation = Surface(name="Excavated NAP-2 m", points=[Point(x=0, z=-2)])
    surface_full_excavation = Surface(name="Excavated NAP-8 m", points=[Point(x=0, z=-8)])

    for stage in [stage_initial, stage_first_excavation, stage_strut, stage_wet_excavation, stage_pit_dry]:
        model.add_surface(surface=surface_ground_level, side=Side.RIGHT, stage_id=stage)

    for stage in [stage_first_excavation, stage_strut]:
        model.add_surface(surface=surface_first_excavation, side=Side.LEFT, stage_id=stage)

    for stage in [stage_wet_excavation, stage_pit_dry]:
        model.add_surface(surface=surface_full_excavation, side=Side.LEFT, stage_id=stage)

    # Define water level
    water_level_initial = WaterLevel(name="Water level NAP-1.0 m", level=-1.0)
    water_level_min2_5 = WaterLevel(name="Water level NAP-2.5 m", level=-2.5)
    water_level_min_8 = WaterLevel(name="Water level NAP-8.0 m", level=-8.0)

    for stage in [stage_initial, stage_first_excavation, stage_strut, stage_wet_excavation, stage_pit_dry]:
        model.add_head_line(water_level=water_level_initial, side=Side.BOTH, stage_id=stage)

    for stage in [stage_first_excavation, stage_strut]:
        model.add_head_line(water_level=water_level_min2_5, side=Side.LEFT, stage_id=stage)

    for stage in [stage_pit_dry]:
        model.add_head_line(water_level=water_level_min_8, side=Side.LEFT, stage_id=stage)

    # Set calculation options

    calc_options = VerifyCalculationOptions(
        input_calculation_type=CalculationType.VERIFY_SHEETPILING,
        # Type of calculation (standard, design sheet piling length, verify, Kranz, overall stability)
        verify_type=VerifyType.EC7NL,  # Type of verification (EC7 general, EC7 NL, CUR, EC7 BE)
        ec7_nl_method=PartialFactorCalculationType.METHODB,  # If EC7 NL/CUR/EC7 BE is used, choose CUR method A or B
        # ec7_nl_overall_partial_factor_set=PartialFactorSetEC7NADNL.RC2,  # Only necessary for method A
        # calc_first_stage_initial=True, # Only with c-phi-delta
        calc_reduce_deltas=True # Only with c-phi-delta
    )

    model.set_calculation_options(calculation_options=calc_options)

    calc_options_per_stage = CalculationOptionsPerStage(partial_factor_set=PartialFactorSetEC7NADNL.RC2) # Necessary for method B

    for stage in [stage_first_excavation, stage_strut, stage_wet_excavation, stage_pit_dry]:
        model.add_calculation_options_per_stage(
            calculation_options_per_stage=calc_options_per_stage, stage_id=stage
        )

    # todo Test other calculation types
    # calc_options = StandardCalculationOptions()
    # model.set_calculation_options(calculation_options=calc_options)
    #

    # calc_options = OverallStabilityCalculationOptions(
    #     cur_stability_stage=1,
    #     overall_stability_type=DesignType.CUR,
    #     stability_cur_partial_factor_set=DesignPartialFactorSet.CLASSII,
    # )

    # model.set_calculation_options(calculation_options=calc_options)
    #
    # calc_options =KranzAnchorStrengthCalculationOptions(cur_anchor_force_stage=1)
    # model.set_calculation_options(calculation_options=calc_options)
    #
    # calc_options = DesignSheetpilingLengthCalculationOptions(
    #     design_stage=1,
    #     design_pile_length_from=10,
    #     design_pile_length_to=1,
    #     design_pile_length_decrement=0.1,
    #     design_type=DesignType.EC7NL,
    #     design_partial_factor_set_ec7_nad_nl=PartialFactorSetEC7NADNL.RC1,
    #     design_ec7_nl_method=PartialFactorCalculationType.METHODA,
    # )

    # model.set_calculation_options(calculation_options=calc_options)

    # Add strut
    strut1 = Strut(
        name="Strut",
        level=-1.5,
        side=Side.LEFT,
        e_modulus=2.1e8,
        cross_section=4.0e-3,
        length=10,
        angle=0.001,  # horizontal, angle=0 doesn't work
        buckling_force=10000,
        pre_compression=10
    )

    for stage in [stage_strut, stage_wet_excavation, stage_pit_dry]:
        model.add_anchor_or_strut(support=strut1, stage_id=stage)

    # # Add anchor
    # anchor = Anchor(
    #     name="Grout anchor",
    #     level=-2,
    #     side=Side.RIGHT,
    #     e_modulus=100000,
    #     cross_section=4.0e-5,
    #     C=10,
    #     wall_height_kranz=1,
    #     length=20,
    #     angle=40,                       # Positive=upwards! Negative now allowed by API
    #     yield_force=1000,
    # )
    #
    # for stage in [stage_strut, stage_wet_excavation]:
    #     model.add_anchor_or_strut(support=anchor, stage_id=stage)

    # Add uniform load
    uniform_load_20kPa = UniformLoad(name="Surface load 20 kPa", left_load=0, right_load=20,
                                     verification_load_settings=VerificationLoadSettings(
                                         duration_type=LoadTypePermanentVariable.VARIABLE,
                                         load_type=LoadTypeFavourableUnfavourableMoment.UNFAVOURABLE))  # default=favourable

    for stage in [stage_first_excavation, stage_strut, stage_wet_excavation,
                  stage_pit_dry]:  # Load is added 3 times in every stage!?!
        model.add_load(load=uniform_load_20kPa, stage_id=stage)

    uniform_load_pit_dry = UniformLoad(name="Surface load 70 kPa", left_load=70, right_load=0,
                                     verification_load_settings=VerificationLoadSettings(
                                         duration_type=LoadTypePermanentVariable.PERMANENT,
                                         load_type=LoadTypeFavourableUnfavourableMoment.FAVOURABLE))  # default=favourable

    for stage in [stage_pit_dry]:  # Load is added 3 times in every stage!?!
        model.add_load(load=uniform_load_pit_dry, stage_id=stage)

    # todo Test other types of loads and supports

    # # Add horizontal line load
    # load = HorizontalLineLoad(name="New HorizontalLineLoad", level=-1, load=10)
    # model.add_load(load=load, stage_id=0)
    #
    # # Add spring support
    # spring_support = SpringSupport(
    #     name="Jerry", level=-15, rotational_stiffness=50, translational_stiffness=50
    # )
    #
    # model.add_support(spring_support, stage_id)
    #
    # # Add rigid support
    # rigid_support = RigidSupport(
    #     name="Redgy", level=-13, support_type=SupportType.ROTATION,
    # )
    #
    # model.add_support(rigid_support, stage_id)
    #
    # # Add moment load
    # moment_load = Moment(name="New Moment", level=-4, load=10,)
    # model.add_load(load=moment_load, stage_id=0)

    # # Add surcharge load
    # surcharge_load = SurchargeLoad(
    #     name="New SurchargeLoad",
    #     points=[Point(x=0, z=5), Point(x=5, z=10), Point(x=10, z=0)],
    # )
    #
    # model.add_surcharge_load(surcharge_load, side=Side.LEFT, stage_id=stage_id)

    # # Add normal force
    # normal_force = NormalForce(
    #     name="New normal force",
    #     force_at_sheet_pile_top=5,
    #     force_at_surface_level_left_side=5,
    #     force_at_surface_level_right_side=5,
    #     force_at_sheet_pile_toe=5,
    # )
    #
    # model.add_load(load=normal_force, stage_id=0)

    # Make .shi file and calculate
    dsheet_file = Path("dsheet_test.shi")
    model.serialize(dsheet_file)
    model.execute()

    output_dict = model.output.dict()
    print(output_dict)  # todo Extract data from dictionary


calculate_sheet_pile()  # todo Some testing

# Note: run fix_d-sheet_output.py to be able to read with GUI program
