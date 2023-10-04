__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

import argparse
from pipelite.pipelineProcess import pipelineProcess
from pipelite.config.cmdLineConfig import cmdLineConfig

def main():
	"""Entry point for the application script"""
	# Get configuration from cmdline & ini file
	config = cmdLineConfig.readConfig(argparse.ArgumentParser())
	# Get the logger
	log = pipelineProcess.getLogger(config)
	# Execute the pipeline 
	pipelineProcess(config, log).process()

if __name__ == "__main__":
	main()