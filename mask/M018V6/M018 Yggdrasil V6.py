# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 16:51:11 2016
@author: Ge Yang
"""

from MaskMaker import MaskMaker as MaskMaker, Utilities as mask_utils, sdxf
from components import shunted_launcher, girl_with_bonding_tatoo, bend_and_touch_down

import os, numpy as np
import subprocess
from time import sleep
from termcolor import colored, cprint

### Close DWG Viewer
# try:
#     subprocess.Popen(r'taskkill /F /im "dwgviewr.exe"')
# except:
#     try:
#         output = subprocess.check_output('ps aux | pgrep AutoCAD', shell=True)
#         print('kill -9 {}'.format(int(output.strip())))
#         subprocess.call('kill -9 {}'.format(int(output.strip())), shell=True)
#     except:
#         pass
### initialization

"""
    first try to calculate the proper gapw for a certain impedance.
    then calculate gapw for the resonator, which has a different centerpin
    width
    """

"""regex used to parse definition below:
^([A-z]*)\t([0-9]*)\t([^\t]*)\t(.*)$
$1 = $2 # $3 :=> $4


"""
nm = 1e-3
# Name	Value	Unit	"Evaluated Value"	Type
substrate_T = 800 * nm  # nm :=> 800nm	Design
metal_T = 80 * nm  # nm :=> 80nm	Design
box_H = 20  # um :=> 20um	Design
helium_level = 730 * nm  # nm :=> 730nm	Design
box_W = 20  # um :=> 20um	Design
box_L = 60  # um :=> 60um	Design
end_cap_L = 1  # um :=> 1um	Design
guard_extra_W = 500 * nm  # nm :=> 0nm	Design
trap_guard_L = 0.5  # :=> um	1.5um	Design
res_pin_W = 900 * nm  # nm :=> 720nm	Design
res_center_gap_W = 700 * nm  # nm :=> 500nm	Design
res_gp_gap_W = 500 * nm  # nm :=> 500nm	Design
trap_W = 8  # um :=> 8um	Design
trap_L = 1.5  # um :=> 3um	Design
trap_ratio = trap_L / trap_W  # :=> 0.375	Design
trap_gap = 250 * nm  # nm :=> 250nm	Design
trap_pin_W = 200 * nm  # nm :=> 200nm	Design
guard_res_gap = trap_gap + 100 * nm  # :=> 350 nm	Design
center_guard_L = trap_L + 500 * nm  # :=> 3um	Design
guard_gap = 250 * nm  # nm :=> 250nm	Design
channel_W = res_pin_W * 2 + res_center_gap_W + res_gp_gap_W * 2  # :=> 2940nm	Design
guard_W = box_W / 2 - channel_W / 2 + guard_extra_W  # :=> 8.53um	Design
ground_Y0 = center_guard_L / 2 + guard_gap * 2 + trap_guard_L  # :=> 3.5um	Design
trap_pin_Y0 = -(center_guard_L / 2 + guard_gap + trap_guard_L)  # :=> -3.25um	Design
res_pin_Y0 = -trap_pin_Y0  # :=> 3.25e-006	Design
res_pin_trap_outer_A = trap_W / 2 - trap_gap - 1000 * nm  # nm # :=> 3.35um	Design
res_pin_trap_outer_ratio = (trap_L / 2 - trap_gap + 100 * nm) / res_pin_trap_outer_A  # :=> 0.3134328358209	Design
res_pin_trap_inner_A = res_pin_trap_outer_A - trap_gap - 800 * nm  # :=> 1.9um	Design
res_pin_trap_inner_ratio = (
                               res_pin_trap_outer_A * res_pin_trap_outer_ratio - trap_gap - 20 * nm) / res_pin_trap_inner_A  # :=> 0.26315789473684	Design
trap_pin_A = res_pin_trap_inner_A - trap_gap - 200 * nm  # :=> 1.45um	Design
trap_pin_ratio = (
                     res_pin_trap_inner_A * res_pin_trap_inner_ratio - trap_gap + 80 * nm) / trap_pin_A  # :=> 0.10344827586207	Design


### Userful Classes
class half_res():
    def __init__(self, s, freq, cap1, cap2, defaults={}):
        self.interior_length = calculate_interior_length(self.freq,
                                                         defaults['phase_velocity'],
                                                         defaults['impedance'],
                                                         resonator_type=0.5,
                                                         harmonic=0,
                                                         Ckin=cap1, Ckout=cap2)
        print("Interior length is: %f" % (self.interior_length))
        CPWWiggles(s, 5, self.interior_length / 2.)

    # for c in [c1, c2, c3]:
    ##TODO: Need to clean up the descriptions
    # c.short_description = lambda: "a"
    # c.long_description = lambda: "b"


    ### initialization
    """
    first try to calculate the proper gapw for a certain impedance.
    then calculate gapw for the resonator, which has a different centerpin
    width
    """


### Userful Classes

def set_mask_init():
    ### Setting defaults
    d = mask_utils.ChipDefaults()
    d.Q = 1000
    d.radius = 50
    d.segments = 6
    d.pinw_rsn = 2.  # this is the resonator pinwitdth that we are goign to use.
    d.gapw_rsn = 8.5

    d.pinw = 1.5  # d.pinw
    d.gapw = 1.
    d.center_gapw = 1
    ### Now calculate impedance
    d.imp_rsn = 80.  # calculate_impedance(d.pinw_rsn,d.gapw_rsn,d.eps_eff)
    d.solid = False
    return d


def chipInit(c, defaults):
    ### Components

    ### left and right launch points
    # experiment with different naming schemes for the launch points.
    left_and_right_launcher_spacing = 750

    launch_pt = MaskMaker.translate_pt(c.left_midpt, (0, left_and_right_launcher_spacing / 2.))
    setattr(c, 'sl1', MaskMaker.Structure(c, start=launch_pt, direction=0, defaults=defaults))
    launch_pt = MaskMaker.translate_pt(c.left_midpt, (0, - left_and_right_launcher_spacing / 2.))
    setattr(c, 'sl2', MaskMaker.Structure(c, start=launch_pt, direction=0, defaults=defaults))
    launch_pt = MaskMaker.translate_pt(c.right_midpt, (0, left_and_right_launcher_spacing / 2.))
    setattr(c, 'sr1', MaskMaker.Structure(c, start=launch_pt, direction=180, defaults=defaults))
    launch_pt = MaskMaker.translate_pt(c.right_midpt, (0, - left_and_right_launcher_spacing / 2.))
    setattr(c, 'sr2', MaskMaker.Structure(c, start=launch_pt, direction=180, defaults=defaults))

    ### Launchpoints
    # setattr(c, "d", defaults)
    setattr(c, 's1', MaskMaker.Structure(c, start=c.top_midpt, direction=270, defaults=defaults))
    setattr(c, 's2', MaskMaker.Structure(c, start=c.bottom_midpt, direction=90, defaults=defaults))
    setattr(c, 's3', MaskMaker.Structure(c, start=c.left_midpt, direction=0, defaults=defaults))
    setattr(c, 's4', MaskMaker.Structure(c, start=c.right_midpt, direction=180, defaults=defaults))
    setattr(c, 's5', MaskMaker.Structure(c, start=c.top_left, direction=270, defaults=defaults))
    setattr(c, 's6', MaskMaker.Structure(c, start=c.top_right, direction=270, defaults=defaults))
    setattr(c, 's7', MaskMaker.Structure(c, start=c.bottom_left, direction=90, defaults=defaults))
    setattr(c, 's8', MaskMaker.Structure(c, start=c.bottom_right, direction=90, defaults=defaults))
    # new anchor points
    setattr(c, 's9', MaskMaker.Structure(c, start=c.top_left_midpt, direction=270, defaults=defaults))
    setattr(c, 's10', MaskMaker.Structure(c, start=c.top_right_midpt, direction=270, defaults=defaults))
    setattr(c, 's11', MaskMaker.Structure(c, start=c.bottom_left_midpt, direction=90, defaults=defaults))
    setattr(c, 's12', MaskMaker.Structure(c, start=c.bottom_right_midpt, direction=90, defaults=defaults))
    # new anchor points
    setattr(c, 's13', MaskMaker.Structure(c, start=c.top_left_mid_left, direction=270, defaults=defaults))
    setattr(c, 's14', MaskMaker.Structure(c, start=c.top_left_mid_right, direction=270, defaults=defaults))
    setattr(c, 's15', MaskMaker.Structure(c, start=c.top_right_mid_left, direction=270, defaults=defaults))
    setattr(c, 's16', MaskMaker.Structure(c, start=c.top_right_mid_right, direction=270, defaults=defaults))
    setattr(c, 's17', MaskMaker.Structure(c, start=c.bottom_left_mid_left, direction=90, defaults=defaults))
    setattr(c, 's18', MaskMaker.Structure(c, start=c.bottom_left_mid_right, direction=90, defaults=defaults))
    setattr(c, 's19', MaskMaker.Structure(c, start=c.bottom_right_mid_left, direction=90, defaults=defaults))
    setattr(c, 's20', MaskMaker.Structure(c, start=c.bottom_right_mid_right, direction=90, defaults=defaults))
    MaskMaker.FineAlign(c, al=50, wid=50, mark_type='box', solid=defaults.solid)

    alignment1 = MaskMaker.Structure(c, start=(c.top_midpt[0] - 1400, c.top_midpt[1] - 60), layer='gap')
    alignment2 = MaskMaker.Structure(c, start=(c.bottom_midpt[0] - 1400, c.bottom_midpt[1] + 60), layer='gap')
    alignment3 = MaskMaker.Structure(c, start=(c.bottom_midpt[0] + 1400, c.bottom_midpt[1] + 60), layer='gap')
    alignment4 = MaskMaker.Structure(c, start=(c.top_midpt[0] + 1400, c.top_midpt[1] - 60), layer='gap')
    MaskMaker.Box(alignment1, 50, 50, offset=(0, 0), solid=defaults.solid)
    MaskMaker.Box(alignment2, 50, 50, offset=(0, 0), solid=defaults.solid)
    MaskMaker.Box(alignment3, 50, 50, offset=(0, 0), solid=defaults.solid)
    MaskMaker.Box(alignment4, 50, 50, offset=(0, 0), solid=defaults.solid)

    # Via Layer (Two Layer only)
    if hasattr(c, "via_layer"):
        c.via_layer.last_direction = 0

        c.via_layer.last = c.left_midpt
        MaskMaker.Box(c.via_layer, 100, 100, offset=(2600, 150), solid=defaults.solid)
        c.via_layer.last = c.left_midpt
        MaskMaker.Box(c.via_layer, 100, 100, offset=(2600, -150), solid=defaults.solid)

        c.via_layer.last = c.left_midpt
        MaskMaker.Box(c.via_layer, 100, 100, offset=(3700, 150), solid=defaults.solid)
        c.via_layer.last = c.left_midpt
        MaskMaker.Box(c.via_layer, 100, 100, offset=(3700, -150), solid=defaults.solid)

        c.via_layer.last = c.right_midpt
        MaskMaker.Box(c.via_layer, 100, 100, offset=(-1600, 150), solid=defaults.solid)
        c.via_layer.last = c.right_midpt
        MaskMaker.Box(c.via_layer, 100, 100, offset=(-1600, -150), solid=defaults.solid)

        c.via_layer.last = c.right_midpt
        MaskMaker.Box(c.via_layer, 100, 100, offset=(-2800, 150), solid=defaults.solid)
        c.via_layer.last = c.right_midpt
        MaskMaker.Box(c.via_layer, 100, 100, offset=(-2800, -150), solid=defaults.solid)


def chipDrw_1(c, chip_resonator_length, chip_coupler_length, wiggle_length, d=None, inductive_launcher=False):
    ### Chip Init
    # gapw=calculate_gap_width(eps_eff,50,pinw)


    print(d.__dict__.keys())
    if d == None: d = MaskMaker.ChipDefaults()
    gap_ratio = d.gapw / d.pinw
    c.frequency = 10
    c.pinw = 1.5  # d.pinw
    c.gapw = 1.
    c.center_gapw = 1
    c.radius = 40
    c.frequency = 5  # GHz
    # c.Q = 1000000 #one of the couplers
    c.imp_rsn = 80
    launch_pin_width = 150
    launcher_width = (1 + 2 * gap_ratio) * launch_pin_width
    c.launcher_length = 500
    c.inside_padding = 1160
    c.left_inside_padding = 180
    c.C = 0.5e-15  # (factor of 2 smaller than actual value from simulation.)
    c.cap1 = mask_utils.sapphire_capacitor_by_C_Channels(c.C)
    # c.cap1 = sapphire_capacitor_by_Q_Channels(c.frequency, c.Q, 50, resonator_type=0.5)
    ### Calculating the interior length of the resonator
    # c.interior_length = calculate_interior_length(c.frequency, d.phase_velocity,
    # c.imp_rsn, resonator_type=0.5,
    # harmonic=0, Ckin=c.cap1, Ckout=c.cap1)
    c.interior_length = 17631 / 2.  # unit is micron, devide by 2 to get the half wavelength
    # This gives 6.88GHz in reality.
    c.meander_length = c.interior_length  # (c.interior_length - (c.inside_padding))  - c.left_inside_padding
    print('meander_length', c.meander_length)

    c.num_wiggles = 7
    c.meander_horizontal_length = (c.num_wiggles + 1) * 2 * c.radius
    launcher_straight = 645
    chipInit(c, defaults=d)

    ### Components
    #### MaskMaker.Launcher
    two_layer = c.two_layer

    launcher_pin_w = 3
    launcher_gap_w = 2.5

    c.s5.pinw = 4.
    c.s5.gapw = 2.5
    c.s7.pinw = 4.
    c.s7.gapw = 2.5
    c.s3.pinw2 = d.pinw_rsn
    c.s4.pinw2 = d.pinw_rsn
    if two_layer:
        c.s5.chip.two_layer = True
        c.s7.chip.two_layer = True

    ### Left launchers and the drive resonator
    s = c.s3
    shunted_launcher(s, pinw=launcher_pin_w, gapw=launcher_gap_w)

    # Interaction driven programming: encourage trying code out and look at the output, instead of just reading code.
    # such encouragements unlock new behaviors that positively re-enforce itself.
    # this positive re-enforcement is what makes this kind of philosophical change significant.

    # drive resonator from the left

    drive_pinw = channel_W - 2 * res_gp_gap_W
    drive_gapw = res_gp_gap_W
    padding_to_connect_to_ellipse = trap_gap * 2
    two_pin_L = trap_guard_L + trap_gap

    c.s_drive = c.s3
    MaskMaker.CPWStraight(c.s_drive, 6)
    MaskMaker.CPWTaper(c.s_drive, 6, stop_pinw=drive_pinw, stop_gapw=drive_gapw)
    MaskMaker.CPWStraight(c.s_drive, 2562 + 6.5 + 2 * guard_gap + trap_guard_L - center_guard_L / 2)

    # trap area
    # gapw is always res_gp_gap_W
    MaskMaker.CPWStraight(c.s_drive, trap_gap, pinw=trap_pin_W, gapw=(channel_W - trap_pin_W) / 2)
    MaskMaker.ThreePinTaper(c.s_drive, two_pin_L, pinw=res_pin_W - guard_res_gap, center_pinw=trap_pin_W,
                            gapw=guard_res_gap,
                            center_gapw=trap_gap)
    MaskMaker.ThreePinTaper(c.s_drive, padding_to_connect_to_ellipse, pinw=res_pin_W, center_pinw=trap_pin_W,
                            gapw=res_gp_gap_W, center_gapw=trap_gap)
    MaskMaker.CPWStraight(c.s_drive, center_guard_L - padding_to_connect_to_ellipse * 2, pinw=trap_pin_W,
                          gapw=(channel_W - trap_pin_W) / 2)
    MaskMaker.ThreePinTaper(c.s_drive, padding_to_connect_to_ellipse, pinw=res_pin_W, center_pinw=trap_pin_W,
                            gapw=res_gp_gap_W, center_gapw=trap_gap)
    MaskMaker.ThreePinTaper(c.s_drive, two_pin_L, pinw=res_pin_W - guard_res_gap, center_pinw=trap_pin_W,
                            gapw=guard_res_gap,
                            center_gapw=trap_gap)
    MaskMaker.CoupledStraight(c.s_drive, trap_gap, center_gapw=trap_gap * 2 + trap_pin_W)

    ### Right launchers and the readout resonator

    s = c.s4
    s.chip.two_layer = True
    pinw = res_pin_W * 2
    gapw = res_center_gap_W / 2 + res_gp_gap_W

    if inductive_launcher:
        shunted_launcher(s, pinw=4, gapw=4, handedness='right')
        MaskMaker.CPWTaper(s, 80 + 87.00, stop_pinw=pinw, stop_gapw=gapw)
    else:
        MaskMaker.Launcher(s, pinw=pinw, gapw=gapw)
        MaskMaker.CPWStraight(s, 245 + 80)

    ### resonator straignt segment
    right_launcher_straight = 2000 + wiggle_length - 80 - 245. - chip_resonator_length + 280 + 229.890 + 300 + 0.75 + \
                              guard_gap * 2 + trap_guard_L
    cprint("right_launcher_straight: {}".format(right_launcher_straight), color="red")

    MaskMaker.CPWStraight(s, right_launcher_straight)
    MaskMaker.CPWTaper(s, 1)
    MaskMaker.CPWStraight(s, 4.5)
    MaskMaker.CPWTaper(s, 1)  ##, stop_pinw=1.5, stop_gapw=(channel_W - 1.5) / 2)
    MaskMaker.CPWStraight(s, 10)
    MaskMaker.CPWTaper(s, 3, stop_pinw=res_pin_W * 2 + res_center_gap_W, stop_gapw=res_gp_gap_W)

    # resonator (on the right)
    readout_resonator_start_pt = MaskMaker.translate_pt(c.center, (
        chip_resonator_length - 529.390 - 300 + 1000 - wiggle_length - 0.75 - 2 * guard_gap - trap_guard_L, 0))
    c.s_readout = MaskMaker.Structure(c, start=readout_resonator_start_pt, direction=180)
    s = c.s_readout
    s.pinw = res_pin_W
    s.gapw = res_gp_gap_W
    s.center_gapw = res_center_gap_W
    MaskMaker.CoupledStraight(s, 50)

    wiggle_right_length = resonator_length - wiggle_length - 1 - 1.16 + 1.27 - 1.86 - 0.1400 - trap_gap

    MaskMaker.CoupledWiggles(s, 6, wiggle_length, 0, start_up=True, radius=30,
                             segments=30)
    MaskMaker.CoupledStraight(s, wiggle_right_length)

    mid_pt = MaskMaker.translate_pt(MaskMaker.middle(c.s1.last, c.s2.last), (-300, 0))
    s.last = mid_pt
    theta2 = np.arcsin(0.70 / (2 * res_pin_trap_outer_A))
    theta3 = np.arcsin(0.70 / (2 * res_pin_trap_inner_A))

    outer_arc = MaskMaker.ellipse_arcpts(mid_pt, res_pin_trap_outer_A * res_pin_trap_outer_ratio, res_pin_trap_outer_A,
                                         angle_start=theta2, angle_stop=np.pi - theta2, angle=0, segments=15)
    inner_arc = MaskMaker.ellipse_arcpts(mid_pt, res_pin_trap_inner_A * res_pin_trap_inner_ratio, res_pin_trap_inner_A,
                                         angle_start=np.pi - theta3, angle_stop=theta3, angle=0, segments=15)

    for ia in inner_arc:
        outer_arc.append(ia)
    outer_arc.append(outer_arc[0])
    s.pin_layer.append(sdxf.PolyLine(outer_arc))

    # And mirror the trap
    mirrored_outer_arc = MaskMaker.mirror_pts(outer_arc, axis_angle=0, axis_pt=mid_pt)
    s.pin_layer.append(sdxf.PolyLine(mirrored_outer_arc))

    MaskMaker.Ellipses(s.gap_layer, mid_pt, trap_L / 2, trap_W / 2, angle=0, segments=30)
    MaskMaker.Ellipses(s.pin_layer, mid_pt, trap_pin_A * trap_pin_ratio, trap_pin_A, angle=0, segments=30)

    s.chip.two_layer = True

    guardSHorizontal = 360 + 12.68 + 1.277 + 0.0707 - 0.220 - 0.0670 - 0.290 - 0.07
    guardEndStraight = 120 + 20.7 + 2 + 2
    sideGuardEndStraight = 1.0 + 3.9897 + 0.255 - 0.12 - 0.25 - 1.350 + 0.37 - 0.28 - 0.0544 + guard_extra_W

    ### Microwave Feed Couplers

    coupler_offset = 15
    R1 = 60
    L1 = 0
    L3 = 199.5 - 0.0013 - 120 - 40 - 40
    L5 = 27.2513 + 150 + 150 - coupler_offset  # to make it `coupler_offset` um away from the resonator

    s = c.s15
    s.chip.two_layer = False
    s.pinw = 3
    s.gapw = 1
    MaskMaker.Launcher(s)
    MaskMaker.CPWStraight(s, L1 + R1 * 2 + L3)
    MaskMaker.CPWStraight(s, L5)
    MaskMaker.CPWStraight(s, 1.5, pinw=0, gapw=2.5)

    s = c.s19
    s.chip.two_layer = False
    s.pinw = 3
    s.gapw = 1
    MaskMaker.Launcher(s)
    MaskMaker.CPWStraight(s, L1 + R1 * 2 + L3)
    MaskMaker.CPWStraight(s, L5)
    MaskMaker.CPWStraight(s, 1.5, pinw=0, gapw=2.5)

    ### Resonator Couplers
    c.two_layer = True
    coupler_spacing = 0.8
    coupler_offset_v = 1.5 + 1.2 - 1. - 0.73
    coupler_offset_h = 462.4025 - coupler_spacing + 159.6475 - coupler_spacing
    launch_pt = MaskMaker.translate_pt(c.center, (coupler_offset_h, coupler_offset_v))
    setattr(c, 'resonator_coupler_1', MaskMaker.Structure(c, start=launch_pt, direction=90))
    launch_pt = MaskMaker.translate_pt(c.center, (coupler_offset_h, -coupler_offset_v))
    setattr(c, 'resonator_coupler_2', MaskMaker.Structure(c, start=launch_pt, direction=-90))

    coupler_1 = c.resonator_coupler_1
    res_coupler_gap = 0.65
    end_cap_gap = 1.2 / 2 + res_coupler_gap  # 1.25 um

    coupler_1.pinw = 1.2
    coupler_1.gapw = res_coupler_gap
    coupler_2 = c.resonator_coupler_2
    coupler_2.pinw = 1.2
    coupler_2.gapw = res_coupler_gap

    MaskMaker.CPWStraight(coupler_1, coupler_offset + chip_coupler_length)
    MaskMaker.CPWStraight(coupler_1, 1.5, pinw=0, gapw=end_cap_gap)

    MaskMaker.CPWStraight(coupler_2, coupler_offset + chip_coupler_length)
    MaskMaker.CPWStraight(coupler_2, 1.5, pinw=0, gapw=end_cap_gap)

    ### DC Guards
    guard_pin_w = trap_guard_L
    guard_radius = 1.2
    guard_taper_length = 6

    # Trap Side Guards
    s = c.s14
    s.chip.two_layer = False
    horizontal_offset_1 = 92.7441 - center_guard_L / 2
    horizontal_offset_2 = 67.7441 - center_guard_L / 2

    shunted_launcher(s, pinw=launcher_pin_w, gapw=launcher_gap_w)
    girl_with_bonding_tatoo(s, 'right')
    MaskMaker.CPWStraight(s, horizontal_offset_1)
    bend_and_touch_down(s, 'right', guardEndStraight, guard_taper_length, guard_pin_w, trap_gap, guard_radius,
                        sideGuardEndStraight)

    s = c.s18
    s.chip.two_layer = False
    shunted_launcher(s, pinw=launcher_pin_w, gapw=launcher_gap_w, handedness='left')
    girl_with_bonding_tatoo(s, handedness='left')
    MaskMaker.CPWStraight(s, horizontal_offset_1)
    bend_and_touch_down(s, 'left', guardEndStraight, guard_taper_length, guard_pin_w, trap_gap, guard_radius,
                        sideGuardEndStraight)

    # Resonator Side Guards
    s = c.s1
    s.chip.two_layer = False
    shunted_launcher(s, pinw=launcher_pin_w, gapw=launcher_gap_w, handedness='left')
    girl_with_bonding_tatoo(s, handedness='left')
    MaskMaker.CPWStraight(s, horizontal_offset_2)
    bend_and_touch_down(s, 'left', guardEndStraight, guard_taper_length, guard_pin_w, trap_gap, guard_radius,
                        sideGuardEndStraight)

    s = c.s2
    s.chip.two_layer = False
    shunted_launcher(s, pinw=launcher_pin_w, gapw=launcher_gap_w)
    girl_with_bonding_tatoo(s, 'right')
    MaskMaker.CPWStraight(s, horizontal_offset_2)
    bend_and_touch_down(s, 'right', guardEndStraight, guard_taper_length, guard_pin_w, trap_gap, guard_radius,
                        sideGuardEndStraight)

    # Resonator DC Bias pinch electrodes
    L0 = 10
    L1 = 20
    R = 20
    L3 = - (resonator_length - 900 - wiggle_length) + 1450 - 40 - 36.86 + 0.15 + 1.5 + - 0.15 + guard_gap
    L5 = 4
    L6 = 2
    L4 = 450 - 40 - L1 - 0.4 - 1.070 - L5 - L6 - 0.28 - 200 + 82.50 - 1.25 - 8.75

    s = c.s6
    shunted_launcher(s, launcher_pin_w, launcher_gap_w, 'left')
    MaskMaker.CPWTaper(s, L0, stop_pinw=1.5, stop_gapw=1.5)
    MaskMaker.CPWSturn(s, L1, -90, R, L3, 90, R, L4, segments=3)
    MaskMaker.CPWTaper(s, L5, stop_pinw=3.5, stop_gapw=0.5)
    MaskMaker.CPWStraight(s, L6)

    s = c.s8
    shunted_launcher(s, launcher_pin_w, launcher_gap_w, 'right')
    MaskMaker.CPWTaper(s, L0, stop_pinw=1.5, stop_gapw=1.5)
    MaskMaker.CPWSturn(s, L1, 90, R, L3, -90, R, L4, segments=3)
    MaskMaker.CPWTaper(s, L5, stop_pinw=3.5, stop_gapw=0.5)
    MaskMaker.CPWStraight(s, L6)

    s.chip.two_layer = True


if __name__ == "__main__":
    ### define mask name, and open up an explorer window
    MaskName = "M018V6"  # M006 Constriction Gate Resonator"

    m = MaskMaker.WaferMask(MaskName, flat_angle=90., flat_distance=24100., wafer_padding=3.3e3, chip_size=(7000, 1900),
                            dicing_border=400, etchtype=False, wafer_edge=False,
                            dashed_dicing_border=50)
    print("chip size: ", m.chip_size)
    # Smaller alignment markers as requested by Leo
    points = [  # (-11025., -19125.),(-11025., 19125.),(11025., -19125.),(11025., 19125.),
        (-15000., -13200.), (-15000., 13200.), (15000., -13200.), (15000., 13200.)]
    MaskMaker.AlignmentBox(m, linewidth=10, size=(100, 100), points=points, layer='gap', name='alignment_box')
    border_locs = [(-18750., 21600.), (18750., 21600.),
                   (-18750., -21600.), (18750., -21600.)]
    MaskMaker.AlignmentCross(m, linewidth=200, size=(200, 200), points=border_locs, layer='gap', name='border_gap')
    MaskMaker.AlignmentCross(m, linewidth=200, size=(200, 200), points=border_locs, layer='pin', name='border_pin')
    MaskMaker.AlphaNumText(m, text="DIS 170329", size=(400, 400), point=(7650, -19300), centered=True,
                           layer='gap')  # change the mask name/title here
    MaskMaker.AlphaNumText(m, text="M018 Ge Yang", size=(400, 400), point=(7650, -18500), centered=True,
                           layer='gap')  # change the mask name/title here
    MaskMaker.AlphaNumText(m, text="DIS 170329 M018 Ge Yang", size=(700, 700), point=(0, 20500), centered=True,
                           layer='gap')  # change the mask name/title here

    # m.randomize_layout()
    d = set_mask_init()
    # solid = False
    solid = True

    # for i, resonator_length in enumerate([2140 * 0.9, 2140 * 0.9 * 1.42]):
    for i, (resonator_length, wiggle_length) in enumerate([
        [2140 * 0.9 * 1.666, 2000],
        [2140 * 0.9 * 1.42 * 1.666, 3000]
    ]):

        for j, coupler_length in enumerate([180]):
            for k, has_bubble_gum in enumerate([False, True]):
                chip_name = 'r{}c{}{}'.format(i + 1, j + 1, 'b' if has_bubble_gum else "")
                print('chip name: ', chip_name)
                c = MaskMaker.Chip(chip_name, author='GeYang', size=m.chip_size, mask_id_loc=(1300, 1720),
                                   chip_id_loc=(1300, 100), author_loc=(6900 - 120, 100), two_layer=True,
                                   solid=solid, segments=10)
                c.textsize = (80, 80)
                chipDrw_1(c,
                          chip_resonator_length=resonator_length, chip_coupler_length=coupler_length,
                          wiggle_length=wiggle_length,
                          d=d,
                          inductive_launcher=has_bubble_gum)
                if i == 1 and j == 0 and k == 0:
                    m.add_chip(c, 32)
                elif i == 1 and j == 0 and k == 1:
                    m.add_chip(c, 32)

    m.save()
    ### Check and open the folder
    cprint(
        colored('current directory ', 'grey') +
        colored(os.getcwd(), 'green')
    )
    sleep(.1)

    cprint(
        colored("operating system is: ", 'grey') +
        colored(os.name, 'green')
    )
    chip_path = os.path.join(os.getcwd(), MaskName + '-' + c.name + '.dxf')
    # if os.name == 'posix':
    #     subprocess.call('open -a "AutoCAD 2016" ' + chip_path, shell=True)
    # elif os.name == 'nt':
    #     subprocess.Popen(
    #         r'"C:\Program Files\Autodesk\DWG TrueView 2014\dwgviewr.exe" "' + chip_path + '" ')
