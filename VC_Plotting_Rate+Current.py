import xlrd
import VC_Plotting_Functions as VC
######
file_name = 'lastlast.xlsx'
xls = xlrd.open_workbook(r'{}'.format(file_name), on_demand=True)
print(xls.sheet_names())        # Remember: xlrd sheet_names is a function, not a property
######
print_option = 2    # 0 - print PR+MC, 1 - print sinkage, 2 - print both
######
for i in xls.sheet_names():
    moving_average_timestep = 15        # Timestep of MA applied in Excel (default = 15 in Excel!)
    degrees_PR = 100                    # Degrees of freedom in PR curve (default = 100)
    degrees_MC = 100                    # Degrees of freedom in MC curve (default = 100)

    lower_bound_PR = -0.05              # Minimum value of Penetration Rate (default = -0.05)
    lower_bound_MC = -1.00              # Minimum value of Motor Current (default = 5.00 or -1.00)
    rel_low_MC = 0.40                   # Multiplier for a minimum value of MC expressed as Median*Multiplier (0.40)
    rel_high_MC = 2.50                  # Multiplier for a maximum value of MC expressed as Median*Multiplier (2.50)
    abs_low_MC = 0.0                    # Absolute minimum value of MC to be included in the trendline (default = 0.0)
    abs_high_MC = 60                    # Absolute maximum value of MC to be included in the trendline (default = 60)

    d_p_MC = 0.05                       # Maximum relative (%) difference between consecutive points of the curve (0.05)
    d_v_MC = 0.05                       # Maximum absolute difference between consecutive points of the curve (0.05)
    d_p_PR = 0.25                       # Maximum relative (%) difference between consecutive points of the curve (0.25)
    d_v_PR = 0.75                       # Maximum absolute difference between consecutive points of the curve (0.75)

    if print_option == 0:
        penetration, current, penetration_rate = VC.derive_VC_data(file_name, i)
        penetration_MA_PR, penetration_rate_MA = VC.derive_for_interpolation_PR(file_name, i, moving_average_timestep,
                                                                                lower_bound_PR)
        penetration_MA_MC, current_MA = VC.derive_for_interpolation_MC(file_name, i, moving_average_timestep,
                                                                       lower_bound_MC, rel_low_MC, rel_high_MC,
                                                                       abs_low_MC, abs_high_MC)
        dane_penetration_rate_MA = VC.dawaj_linie(penetration_MA_PR, penetration_rate_MA, degrees_PR)
        dane_penetration_current_MA = VC.dawaj_linie(penetration_MA_MC, current_MA, degrees_MC)
        VC.print_MC_PR(i, penetration, current, penetration_rate, dane_penetration_rate_MA, dane_penetration_current_MA, d_p_MC, d_v_MC, d_p_PR, d_v_PR, abs_low_MC, abs_high_MC)
    if print_option == 1:
        sinkage_penetration, sinkage_echosounder = VC.derive_VC_sinkage(file_name, i)
        VC.print_sinkage(i, sinkage_penetration, sinkage_echosounder)
    if print_option == 2:
        penetration, current, penetration_rate = VC.derive_VC_data(file_name, i)
        penetration_MA_PR, penetration_rate_MA = VC.derive_for_interpolation_PR(file_name, i, moving_average_timestep,
                                                                                lower_bound_PR)
        penetration_MA_MC, current_MA = VC.derive_for_interpolation_MC(file_name, i, moving_average_timestep,
                                                                       lower_bound_MC, rel_low_MC, rel_high_MC,
                                                                       abs_low_MC, abs_high_MC)
        dane_penetration_rate_MA = VC.dawaj_linie(penetration_MA_PR, penetration_rate_MA, degrees_PR)
        dane_penetration_current_MA = VC.dawaj_linie(penetration_MA_MC, current_MA, degrees_MC)

        sinkage_penetration, sinkage_echosounder = VC.derive_VC_sinkage(file_name, i)

        VC.print_both(i, sinkage_penetration, sinkage_echosounder, penetration, current, penetration_rate, dane_penetration_rate_MA, dane_penetration_current_MA, d_p_MC, d_v_MC, d_p_PR, d_v_PR, abs_low_MC, abs_high_MC)
######