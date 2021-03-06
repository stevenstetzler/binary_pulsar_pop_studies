import argparse
import numpy as np
import matplotlib
matplotlib.use('agg')
from matplotlib import pyplot as plt
from analysis_utils import get_pulsar_dict, get_par_range, make_directory
import cPickle as pickle
import os
from ad_simulations import run_simulation_ad_ksamp


def anderson_darling_analysis(chains, par, niter=10000, nsample=1, compare_nsample=None, mean=1.46, scale=0.21, test_pulsars='all', save_dir=None, visualize=False):
        if compare_nsample is None:
                compare_nsample = len(chains) * nsample

        kwargs = {}
        kwargs['mean'] = mean
        kwargs['scale'] = scale

	if par == 'COSI':
		par_range = (0, 1)
		dist = 'uniform'
	else:
	        par_range = (min([min(chain) for chain in chains]), max([max(chain) for chain in chains]))
		dist = 'normal'

        if save_dir is not None:
                save_name = os.path.join(save_dir, "anderson_darling_{}_chain_{}_compare.png".format(nsample, compare_nsample))
        else:
                save_name = None

        run_simulation_ad_ksamp(chains, par_range=par_range, distribution_type=dist, niter=niter, chain_samples_scaling=nsample, compare_sample_size=compare_nsample, save_name=save_name, verify_sampling=False, visualize=visualize, **kwargs)

	if par == 'COSI':
		p_vals  
		for i in range(niter)

# The number of samples for this method may be too low - histogramming will be very sensitive to the number of bins
def chi2_analysis_sample(chains, niter=10000, test_pulsars='all', nbins=5, save_dir=None, visualize=False):
        plot = visualize or save_dir is not None

        for i in range(niter):
                chains_sample = sample(chains)

                weights = np.ones_like(chains_sample) / float(len(chains_sample))

                if plot:
                        bin_heights, bins, _ = plt.hist(chain, bins=nbins, range=(0, 1), weights=weights)
                else:
                        bin_heights, bins = np.histogram(chain, bins=nbins, range=(0, 1), weights=weights)

                observed_frequency = bin_heights



# This method actually makes no sense: a good measurement will appear narrow in the final histogram
def chi2_analysis(chains, test_pulsars='all', nbins=100, save_dir=None, visualize=False):
        bin_heights = []

        plot = visualize or save_dir is not None

        for chain in chains:
                weights = np.ones_like(chain) / float(len(chain) * len(chains))
                if plot:
                        heights, bins, _ = plt.hist(chain, bins=nbins, range=(0, 1), weights=weights)
                else:
                        heights, bins = np.histogram(chain, bins=nbins, range=(0, 1), weights=weights)
                bin_heights.append(heights)

        observed_frequencies = np.zeros(nbins)
        for heights in bin_heights:
                observed_frequencies += heights

        expected_frequencies = np.ones_like(observed_frequencies) / float(nbins)

        relative_square_diff = [ (obs - exp)**2 / exp for obs, exp in zip(observed_frequencies, expected_frequencies)]

        chi_2 = sum(relative_square_diff)
        print "Computed chi squared = {} for {}\n\t{}".format(chi_2, save_dir.split("/")[-1], "\n\t".join(test_pulsars))

        if save_dir is not None:
                save_name = os.path.join(save_dir, "histograms.png")
                print "Saving figure to {}".format(save_name)
                plt.savefig(save_name)

        if visualize:
                plt.show()

        plt.close('all')

        if plot:
                x = np.linspace(0, 1, len(observed_frequencies))
                plt.plot(x, observed_frequencies, label="Observations")
                plt.plot(x, expected_frequencies, label="Expectation")
                plt.legend()
		plt.title("Chi-Squared = {}".format(chi_2))
		plt.xlabel("COSI values")
                if save_dir is not None:
                        save_name = os.path.join(save_dir, "chi2_comparison.png")
                        print "Saving figure to {}".format(save_name)
                        plt.savefig(save_name)
                if visualize:
                        plt.show()

        plt.close('all')


def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("--pulsar_dir", help="The directory containing pulsar directories with completed simulations to analyze")
        parser.add_argument("--pulsar_dicts", help="The pickle file containing pulsar dictionaries to be analyzed")
        parser.add_argument("--visualize", action="store_true", help="Include to show histograms.")
        parser.add_argument("--save_dir", help="The directory to save plots to.")
        parser.add_argument("--test_pulsar_files", nargs='+', help="A text file containing the name of one pulsar to test on each line.")
        parser.add_argument("--niter", type=int, default=10000, help="The number of iterations to run simulations for.")
        parser.add_argument("--nsample", type=int, default=1, help="The number of times to sample each chain before comparison.")
        parser.add_argument("--compare_nsample", type=int, default=None, help="The number of samples to draw from the comparison distribution before testing.")
	parser.add_argument("--par", required=True, help="The parameter to perform tests for, either COSI or M1")

        args = parser.parse_args()

        pulsar_dir = args.pulsar_dir
        pulsar_dicts = args.pulsar_dicts
        visualize = args.visualize
        save_dir = args.save_dir
        test_pulsar_files = args.test_pulsar_files
        niter = args.niter
        nsample = args.nsample
        compare_nsample = args.compare_nsample
	par = args.par

	if par != 'M1' and par != 'COSI':
		print "--par must be 'M1' or 'COSI'"
		exit()

        if (pulsar_dir is None and pulsar_dicts is None) or (pulsar_dir is not None and pulsar_dicts is not None):
                print "Must pass either a directory with pulsar simulations or a pickle file with pre-compiled pulsar dictionaries"
                exit()

        if pulsar_dir is not None:
                pulsar_dict = get_pulsar_dict(pulsar_dir)
        else:
                pulsar_dict, sim_type = pickle.load(open(pulsar_dicts, "rb"))

        if test_pulsar_files is None:
		chains = []

		for pulsar in pulsar_dict.keys():
			try:
				_, _, par_dict = pulsar_dict[pulsar]
			except KeyError:
				print "{} not in pulsar dict - excluding.".format(pulsar)
				continue

			try:
				chain = par_dict[par]
			except KeyError:
				print "{} not in {} par dictionary - excluding.".format(par, pulsar)
			chains.append(chain)

                if save_dir is not None:
                        test_save_dir = os.path.join(save_dir, par, sim_type, 'all_pulsars')
			make_directory(test_save_dir)
                else:
                        test_save_dir = None
		if par == 'COSI':
	                chi2_analysis(chains, test_pulsars='all', save_dir=test_save_dir, visualize=visualize)
                anderson_darling_analysis(chains, par, test_pulsars='all', save_dir=test_save_dir, visualize=visualize, niter=niter, nsample=nsample, compare_nsample=compare_nsample)
        else:
                for test_pulsar_file in test_pulsar_files:
			print "Opening {}".format(test_pulsar_file)
                        test_pulsars = open(test_pulsar_file, 'r').readlines()
                        test_pulsars = [p.strip() for p in test_pulsars if ('J' in p or 'B' in p) and ('+' in p or '-' in p)]
                        test_pulsar_descriptor = test_pulsar_file.split("/")[-1].split('.')[0]

			chains = []

			for pulsar in test_pulsars:
				try:
					_, _, par_dict = pulsar_dict[pulsar]
				except KeyError:
					print "{} not in pulsar dict - excluding.".format(pulsar)
					continue

				try:
					chain = par_dict[par]
				except KeyError:
					print "{} not in {} par dictionary - exclusing.".format(par, pulsar)
				chains.append(chain)


                        if save_dir is not None:
                                test_save_dir = os.path.join(save_dir, par, sim_type, test_pulsar_descriptor)
				make_directory(test_save_dir)
                        else:
                                test_save_dir = None
			if par == 'COSI':
				chi2_analysis(chains, test_pulsars=test_pulsars, save_dir=test_save_dir, visualize=visualize)
                        anderson_darling_analysis(chains, par, test_pulsars=test_pulsars, save_dir=test_save_dir, visualize=visualize, niter=niter, nsample=nsample, compare_nsample=compare_nsample)


if __name__ == "__main__":
        main()


