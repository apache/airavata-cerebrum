#
# Code copied as it is from V1 Model
#
#
import typing
import numpy as np
from math import sqrt, exp, log
from scipy.stats import multivariate_normal
from scipy.special import erfinv


def lognorm_ppf(x, shape, loc=0, scale=1.0):
    # definition from wikipedia (quantile)
    return scale * exp(sqrt(2 * shape**2) * erfinv(2 * x - 1)) + loc


def delta_theta_cdf(intercept, d_theta):
    B1 = intercept
    # B1 = 2.0 / (1.0 + Q)
    Q = 2.0 / B1 - 1.0
    B2 = B1 * Q
    G = (B2 - B1) / 90.0
    norm = 90 * (B1 + B2)  # total area for normalization
    x = d_theta - 90
    if d_theta < 0:
        raise Exception("d_theta must be >= 0, but was {}".format(d_theta))
    elif d_theta < 90:
        # analytical integration of the pdf to get this cdf
        return (0.5 * G * x**2 + B2 * x) / norm + 0.5
    elif d_theta <= 180:
        return (-0.5 * G * x**2 + B2 * x) / norm + 0.5
    else:
        raise Exception("d_theta must be <= 180, but was {}".format(d_theta))


def compute_pair_type_parameters(
    source_type: str,
    target_type: str,
    cc_props: typing.Dict[str, typing.Any] 
):
    """Takes in two strings for the source and target type. It determined the connectivity parameters needed based on
    distance dependence and orientation tuning dependence and returns a dictionary of these parameters. A description
    of the calculation and resulting formulas used herein can be found in the accompanying documentation. Note that the
    source and target can be the same as this function works on cell TYPES and not individual nodes. The first step of
    this function is getting the parameters that determine the connectivity probabilities reported in the literature.
    From there the calculation proceed based on adapting these values to our model implementation.

    :param source_type: string of the cell type that will be the source (pre-synaptic)
    :param target_type: string of the cell type that will be the targer (post-synaptic)
    :return: dictionary with the values to be used for distance dependent connectivity
             and orientation tuning dependent connectivity (when applicable, else nans populate the dictionary).
    """
    # this part is not used anymore
    # src_new = source_type[3:] if source_type[0:3] == "LIF" else source_type
    # trg_new = target_type[3:] if target_type[0:3] == "LIF" else target_type

    # src_tmp = src_new[0:2]
    # if src_new[0] == "i":
    #     src_tmp = src_new[0:3]
    # if src_new[0:2] == "i2":
    #     src_tmp = src_new[0:2] + src_new[3]

    # trg_tmp = trg_new[0:2]
    # if trg_new[0] == "i":
    #     trg_tmp = trg_new[0:3]
    # if trg_new[0:2] == "i2":
    #     trg_tmp = trg_new[0:2] + trg_new[3]

    # cc_props = cc_prob_dict[src_tmp + "-" + trg_tmp]
    # ### For distance dependence which is modeled as a Gaussian ####
    # P = A * exp(-r^2 / sigma^2)
    # Since papers reported probabilities of connection having measured from 50um to 100um intersomatic distance
    # we had to normalize ensure A. In short, A had to be set such that the integral from 0 to 75um of the above
    # function was equal to the reported A in the literature. Please see accompanying documentation for the derivation
    # of equations which should explain how A_new is determined.
    # Note we intergrate upto 75um as an approximate mid-point from the reported literature.

    # A_literature is different for every source-target pair and was estimated from the literature.
    A_literature = cc_props["A_literature"][
        0
    ]  # TODO: remove [0] after fixing the json file

    # R0 read from the dictionary, but setting it now at 75um for all cases but this allows us to change it
    R0 = cc_props["R0"]

    # Sigma is measure from the literature or internally at the Allen Institute
    sigma = cc_props["sigma"]

    # Gaussian equation was intergrated to and solved to calculate new A_new. See accompanying documentation.
    if cc_props["is_pmax"] == 1:
        A_new = A_literature
    else:
        A_new = A_literature / ((sigma / R0) ** 2 * (1 - np.exp(-((R0 / sigma) ** 2))))

    # Due to the measured values in the literature being from multiple sources and approximations that were
    # made by us and the literature (for instance R0 = 75um and sigma from the literature), we found that it is
    # possible for A_new to go slightly above 1.0 in which case we rescale it to 1.0. We confirmed that if this
    # does happen, it is for a few cases and is not much higher than 1.0.
    if A_new > 1.0:
        # print('WARNING: Adjusted calculated probability based on distance dependence is coming out to be ' \
        #       'greater than 1 for ' + source_type + ' and ' + target_type + '. Setting to 1.0')
        A_new = 1.0

    # ### To include orientation tuning ####
    # Many cells will show orientation tuning and the relative different in orientation tuning angle will influence
    # probability of connections as has been extensively report in the literature. This is modeled here with a linear
    # where B in the largest value from 0 to 90 (if the profile decays, then B is the intercept, if the profile
    # increases, then B is the value at 90). The value of G is the gradient of the curve.
    # The calculations and explanation can be found in the accompanying documentation with this code.

    # Extract the values from the dictionary for B, the maximum value and G the gradient
    B_ratio = cc_props["B_ratio"]
    B_ratio = np.nan if B_ratio is None else B_ratio

    # Check if there is orientation dependence in this source-target pair type. If yes, then a parallel calculation
    # to the one done above for distance dependence is made though with the assumption of a linear profile.
    if not np.isnan(B_ratio):
        # The scaling for distance and orientation must remain less than 1 which is calculated here and reset
        # if it is greater than one. We also ensure that the area under the p(delta_phi) curve is always equal
        # to one (see documentation). Hence the desired ratio by the user may not be possible, in which case
        # an warning message appears indicating the new ratio used. In the worst case scenario the line will become
        # horizontal (no orientation tuning) but will never "reverse" slopes.

        # B1 is the intercept which occurs at (0, B1)
        # B2 is the value when delta_phi equals 90 degree and hence the point (90, B2)
        B1 = 2.0 / (1.0 + B_ratio)
        B2 = B_ratio * B1

        AB = A_new * max(B1, B2)
        if AB > 1.0:
            if B1 >= B2:
                B1_new = 1.0 / A_new
                delta = B1 - B1_new
                B1 = B1_new
                B2 = B2 + delta
            elif B2 > B1:
                B2_new = 1.0 / A_new
                delta = B2 - B2_new
                B2 = B2_new
                B1 = B1 + delta

            B_ratio = B2 / B1
            print(
                "WARNING: Could not satisfy the desired B_ratio (probability of connectivity would become "
                "greater than one in some cases). Rescaled and now for "
                + source_type
                + " --> "
                + target_type
                + " the ratio is set to: ",
                B_ratio,
            )

        G = (B2 - B1) / 90.0

    # If there is no orientation dependent, record this by setting the intercept to Not a Number (NaN).
    else:
        B1 = np.NaN
        G = np.NaN

    # Return the dictionary. Note, the new values are A_new and intercept. The rest are from CC_prob_dict.
    return {
        "A_new": A_new,
        "sigma": sigma,
        "gradient": G,
        "intercept": B1,
        "nsyn_range": cc_props["nsyn_range"],
        "src_ei": cc_props["pre_ei"],   # for Rossi correction
        "trg_ei": cc_props["post_ei"],  # for Rossi
    }


def connect_cells(sources, target, params, source_nodes, core_radius):
    """This function determined which nodes are connected based on the parameters in the dictionary params. The
    function iterates through every cell pair when called and hence no for loop is seen iterating pairwise
    although this is still happening.

    By iterating though every cell pair, a decision is made whether or not two cells are connected and this
    information is returned by the function. This function calculates these probabilities based on the distance between
    two nodes and (if applicable) the orientation tuning angle difference.

    :param sid: the id of the source node
    :param source: the attributes of the source node
    :param tid: the id of the target node
    :param target: the attributes of the target node
    :param params: parameters dictionary for probability of connection (see function: compute_pair_type_parameters)
    :return: if two cells are deemed to be connected, the return function automatically returns the source id
             and the target id for that connection. The code further returns the number of synapses between
             those two neurons
    """
    # special handing of the empty sources
    if source_nodes.empty:
        # since there is no sources, no edges will be created.
        print("Warning: no sources for target: {}".format(target.node_id))
        return []

    # TODO: remove list comprehension
    # sources_x = np.array([s["x"] for s in sources])
    # sources_z = np.array([s["z"] for s in sources])
    # sources_tuning_angle = [s["tuning_angle"] for s in sources]
    sources_x = np.array(source_nodes["x"])
    sources_z = np.array(source_nodes["z"])
    sources_tuning_angle = np.array(source_nodes["tuning_angle"])

    # Get target id
    tid = target.node_id
    # if tid % 1000 == 0:
    #     print('target {}'.format(tid))

    # size of target cell (total syn number) will modulate connection probability
    target_size = target["target_sizes"]
    target_pop_mean_size = target["nsyn_size_mean"]

    # Read parameter values needed for distance and orientation dependence
    A_new = params["A_new"]
    sigma = params["sigma"]
    gradient = params["gradient"]
    intercept = params["intercept"]
    # nsyn_range = params["nsyn_range"]

    # Calculate the intersomatic distance between the current two cells (in 2D - not including depth)
    intersomatic_distance = np.sqrt(
        (sources_x - target["x"]) ** 2 + (sources_z - target["z"]) ** 2
    )

    # For Rossi correction. The distance dependence is asymmetrical in the X-Z plane and depends on the target neuron
    # orientation preference.
    intersomatic_x = sources_x - target["x"]
    intersomatic_z = sources_z - target["z"]
    intersomatic_xz = [
        [delta_x, delta_z] for delta_x, delta_z in zip(intersomatic_x, intersomatic_z)
    ]
    if np.sqrt(target["x"] ** 2 + target["z"] ** 2) > (core_radius * 1.5):
        Rossi_displacement = 0.0
    else:
        Rossi_displacement = (
            50.0  # displacement of presynaptic soma distribution centroid
        )
    Rossi_scaling = 1.5  # scaling of major/minor axes of covariance

    Rossi_theta = np.radians(target["tuning_angle"])

    if params["src_ei"] == "i":
        Rossi_mean = [
            Rossi_displacement * np.cos(Rossi_theta),
            Rossi_displacement * np.sin(Rossi_theta),
        ]
        cov_ = np.array([[(sigma) ** 2, 0.0], [0.0, (sigma) ** 2]])
    else:
        Rossi_mean = [
            -Rossi_displacement * np.cos(Rossi_theta),
            -Rossi_displacement * np.sin(Rossi_theta),
        ]
        cov_ = np.array(
            [[(sigma / Rossi_scaling) ** 2, 0.0], [0.0, (sigma * Rossi_scaling) ** 2]]
        )

    c, s = np.cos(Rossi_theta), np.sin(Rossi_theta)
    R = np.array(((c, -s), (s, c)))
    Rossi_cov = R @ cov_ @ R.transpose()

    Rossi_mvNorm = multivariate_normal(Rossi_mean, Rossi_cov)  # type: ignore

    # if target.node_id % 10000 == 0:
    #     print("Working on tid: ", target.node_id)

    # Check if there is orientation dependence
    if not np.isnan(gradient):
        # Calculate the difference in orientation tuning between the cells
        delta_orientation = np.array(sources_tuning_angle, dtype=float) - float(
            target["tuning_angle"]
        )

        # For OSI, convert to quadrant from 0 - 90 degrees
        delta_orientation = abs(abs(abs(180.0 - abs(delta_orientation)) - 90.0) - 90.0)

        # Calculate the probability two cells are connected based on distance and orientation
        # p_connect = (
        #    A_new
        #    * np.exp(-((intersomatic_distance / sigma) ** 2))
        #    * (intercept + gradient * delta_orientation)
        # )

        # using Rossi:
        p_connect = (
            A_new
            * Rossi_mvNorm.pdf(intersomatic_xz)
            / Rossi_mvNorm.pdf(Rossi_mean)
            * (intercept + gradient * delta_orientation)
        )

    # If no orientation dependence
    else:
        # Calculate the probability two cells are connection based on distance only
        # p_connect = A_new * np.exp(-((intersomatic_distance / sigma) ** 2))

        # using Rossi:
        p_connect = (
            A_new * Rossi_mvNorm.pdf(intersomatic_xz) / Rossi_mvNorm.pdf(Rossi_mean)
        )

    # # Sanity check warning
    # if p_connect > 1:
    #    print(
    #        "WARNING WARNING WARNING: p_connect is greater that 1.0 it is: "
    #        + str(p_connect)
    #    )

    # If not the same cell (no self-connections)
    if 0.0 in intersomatic_distance:
        p_connect[np.where(intersomatic_distance == 0.0)[0][0]] = 0

    # Connection p proportional to target cell synapse number relative to population average:
    p_connect = p_connect * target_size / target_pop_mean_size

    # If p_connect > 1 set to 1:
    p_connect[p_connect > 1] = 1

    # Decide which cells get a connection based on the p_connect value calculated
    p_connected = np.random.binomial(1, p_connect)

    # Synapse number only used for calculating numbers of "leftover" syns to assign as background;
    #    N_syn_ will be added through 'add_properties'
    # p_connected[p_connected == 1] = 1

    # p_connected[p_connected == 1] = np.random.randint(
    #    nsyn_range[0], nsyn_range[1], len(p_connected[p_connected == 1])
    # )

    # TODO: remove list comprehension
    nsyns_ret = [Nsyn if Nsyn != 0 else None for Nsyn in p_connected]
    return nsyns_ret


def syn_weight_by_experimental_distribution(
    source,
    target,
    src_type,
    trg_type,
    src_ei,
    trg_ei,
    PSP_correction,
    PSP_lognorm_shape,
    PSP_lognorm_scale,
    connection_params,
    # delta_theta_dist,
):
    # src_ei = "e" if src_type.startswith("e") or src_type.startswith("LIFe") else "i"
    # trg_ei = "e" if trg_type.startswith("e") or trg_type.startswith("LIFe") else "i"
    src_tuning = source["tuning_angle"]
    tar_tuning = target["tuning_angle"]

    x_tar = target["x"]
    x_src = source["x"]
    z_tar = target["z"]
    z_src = source["z"]

    #
    if PSP_lognorm_shape < target["nsyn_size_shape"]:
        weight_shape = 0.001
    else:
        weight_shape = sqrt(PSP_lognorm_shape**2 - target["nsyn_size_shape"] ** 2)
    weight_scale = exp(
        log(PSP_lognorm_scale)
        + log(target["nsyn_size_scale"])
        - log(target["nsyn_size_mean"])
    )
    # weight_rv = lognorm(weight_shape, loc=0, scale=weight_scale)

    # To set syn_weight, use the PPF with the orientation difference:
    # if not np.isnan(src_trg_params["gradient"]):

    # randomizing_factor = 0.1 #  8/15/2022 after discussion, decided to weaken the randomness
    randomizing_factor = (
        1.0  # 8/18/2022 reverting as it didn't affect the results much
    )
    # Original if condition:
    # if src_ei == "e" and trg_ei == "e" and (not type(delta_theta_dist) == float):
    # TODO: Please make sure if I'm doing it right.
    if (
        src_ei == "e"
        and trg_ei == "e"
        and (not np.isnan(connection_params["gradient"]))
    ):
        # For e-to-e, there is a non-uniform distribution of delta_orientations.
        # These need to be ordered and mapped uniformly over [0,1] using the cdf:

        # adds some randomization to like-to-like and avoids 0-degree delta
        # tuning_rnd = float(np.random.randn(1) * 5) * randomizing_factor
        tuning_rnd = 0.0

        delta_tuning_180 = np.abs(
            np.abs(np.mod(np.abs(tar_tuning - src_tuning + tuning_rnd), 360.0) - 180.0)
            - 180.0
        )

        # orient_temp = 1 - delta_theta_dist.cdf(delta_tuning_180)
        orient_temp = 1 - delta_theta_cdf(
            connection_params["intercept"], delta_tuning_180
        )
        # orient_temp = np.min([0.999, orient_temp])
        # orient_temp = np.max([0.001, orient_temp])
        orient_temp = min(0.999, orient_temp)
        orient_temp = max(0.001, orient_temp)
        syn_weight = lognorm_ppf(orient_temp, weight_shape, loc=0, scale=weight_scale)
        # weight_rv = lognorm(weight_shape, loc=0, scale=weight_scale)
        # syn_weight = weight_rv.ppf(orient_temp)
        n_syns_ = 1

    elif (src_ei == "e" and trg_ei == "i") or (src_ei == "i" and trg_ei == "e"):
        # If there was no like-to-like connection rule for the population, we can use
        # delta_orientation directly with the PPF

        # adds some randomization to like-to-like and avoids 0-degree delta
        tuning_rnd = float(np.random.randn(1) * 5) * randomizing_factor

        delta_tuning_180 = np.abs(
            np.abs(np.mod(np.abs(tar_tuning - src_tuning + tuning_rnd), 360.0) - 180.0)
            - 180.0
        )

        orient_temp = 1 - (delta_tuning_180 / 180)
        # orient_temp = np.min([0.999, orient_temp])
        # orient_temp = np.max([0.001, orient_temp])
        orient_temp = min(0.999, orient_temp)
        orient_temp = max(0.001, orient_temp)
        syn_weight = lognorm_ppf(orient_temp, weight_shape, loc=0, scale=weight_scale)
        # syn_weight = weight_rv.ppf(orient_temp)
        n_syns_ = 1

    elif src_ei == "i" and trg_ei == "i":
        # If there was no like-to-like connection rule for the population, we can use
        # delta_orientation directly with the PPF

        # adds some randomization to like-to-like and avoids 0-degree delta
        tuning_rnd = float(np.random.randn(1) * 10) * randomizing_factor

        delta_tuning_180 = np.abs(
            np.abs(np.mod(np.abs(tar_tuning - src_tuning + tuning_rnd), 360.0) - 180.0)
            - 180.0
        )

        orient_temp = 1 - (delta_tuning_180 / 180)
        # orient_temp = np.min([0.999, orient_temp])
        # orient_temp = np.max([0.001, orient_temp])
        orient_temp = min(0.999, orient_temp)
        orient_temp = max(0.001, orient_temp)

        syn_weight = lognorm_ppf(orient_temp, weight_shape, loc=0, scale=weight_scale)
        # syn_weight = weight_rv.ppf(orient_temp)
        n_syns_ = 1

    else:
        # If there was no like-to-like connection rule for the population, we can use
        # delta_orientation directly with the PPF

        # adds some randomization to like-to-like and avoids 0-degree delta
        tuning_rnd = float(np.random.randn(1) * 5) * randomizing_factor

        delta_tuning_180 = np.abs(
            np.abs(np.mod(np.abs(tar_tuning - src_tuning + tuning_rnd), 360.0) - 180.0)
            - 180.0
        )

        orient_temp = 1 - (delta_tuning_180 / 180)
        # orient_temp = np.min([0.999, orient_temp])
        # orient_temp = np.max([0.001, orient_temp])
        orient_temp = min(0.999, orient_temp)
        orient_temp = max(0.001, orient_temp)
        syn_weight = lognorm_ppf(orient_temp, weight_shape, loc=0, scale=weight_scale)
        # syn_weight = weight_rv.ppf(orient_temp)
        n_syns_ = 1

    # Below was copied from Billeh to use as an initial correction factor, but it is not clear how applicable
    # it is to the current Rossi Rule
    # delta_x = (x_tar - x_src) * 0.07
    # delta_z = (z_tar - z_src) * 0.04

    # theta_pref = tar_tuning * (np.pi / 180.0)
    # xz = delta_x * np.cos(theta_pref) + delta_z * np.sin(theta_pref)
    # sigma_phase = 1.0
    # phase_scale_ratio = np.exp(-(xz**2 / (2 * sigma_phase**2)))

    # # To account for the 0.07 vs 0.04 dimensions. This ensures the horizontal neurons are scaled by 5.5/4 (from the
    # # midpoint of 4 & 7). Also, ensures the vertical is scaled by 5.5/7. This was a basic linear estimate to get the
    # # numbers (y = ax + b).
    # theta_tar_scale = abs(
    #     abs(abs(180.0 - np.mod(np.abs(tar_tuning), 360.0)) - 90.0) - 90.0
    # )
    # phase_scale_ratio = phase_scale_ratio * (
    #     5.5 / 4.0 - 11.0 / 1680.0 * theta_tar_scale
    # )

    syn_weight = (
        syn_weight
        * target["nsyn_size_mean"]
        / (PSP_correction * target["target_sizes"])
    )
    return syn_weight, n_syns_


def generate_random_positions(N, layer_range, radial_range):
    radius_outer = radial_range[1]
    radius_inner = radial_range[0]

    phi = 2.0 * np.pi * np.random.random([N])
    r = np.sqrt(
        (radius_outer ** 2 - radius_inner ** 2) * np.random.random([N])
        + radius_inner ** 2
    )
    x = r * np.cos(phi)
    z = r * np.sin(phi)

    layer_start = layer_range[0]
    layer_end = layer_range[1]
    # Generate N random z values.
    y = (layer_end - layer_start) * np.random.random([N]) + layer_start

    positions = np.column_stack((x, y, z))

    return positions


def generate_positions_grids(N, x_grids, y_grids, x_len, y_len):
    widthPerTile = x_len / x_grids
    heightPerTile = y_len / y_grids

    X = np.zeros(N * x_grids * y_grids)
    Y = np.zeros(N * x_grids * y_grids)

    counter = 0
    for i in range(x_grids):
        for j in range(y_grids):
            x_tile = np.random.uniform(i * widthPerTile, (i + 1) * widthPerTile, N)
            y_tile = np.random.uniform(j * heightPerTile, (j + 1) * heightPerTile, N)
            X[counter * N : (counter + 1) * N] = x_tile
            Y[counter * N : (counter + 1) * N] = y_tile
            counter = counter + 1
    return np.column_stack((X, Y))


def get_filter_spatial_size(N, X_grids, Y_grids, size_range):
    spatial_sizes = np.zeros(N * X_grids * Y_grids)
    counter = 0
    for i in range(X_grids):
        for j in range(Y_grids):
            if len(size_range) == 1:
                sizes = np.ones(N) * size_range[0]
            else:
                sizes = np.random.triangular(
                    size_range[0], size_range[0] + 1, size_range[1], N
                )
            spatial_sizes[counter * N : (counter + 1) * N] = sizes
            counter = counter + 1
    return spatial_sizes


def select_bkg_sources(sources, target, n_syns, n_conn):
    # draw n_conn connections randomly from the background sources.
    # n_syns is the number of synapses per connection
    # n_conn is the number of connections to draw
    n_unit = len(sources)
    # select n_conn units randomly
    selected_units = np.random.choice(n_unit, size=n_conn, replace=False)
    nsyns_ret = np.zeros(n_unit, dtype=int)
    nsyns_ret[selected_units] = n_syns
    nsyns_ret = list(nsyns_ret)
    # getting back to list
    nsyns_ret = [None if n == 0 else n for n in nsyns_ret]
    return nsyns_ret


def lgn_synaptic_weight_rule(source, target, base_weight, mean_size):
    return base_weight * mean_size / target["target_sizes"]
