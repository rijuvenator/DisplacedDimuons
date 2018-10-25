import argparse

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--trigger'  , dest='TRIGGER'  , action='store_true', help='whether this run is for plots with trigger applied')
PARSER.add_argument('--mconly'   , dest='MCONLY'   , action='store_true', help='whether this run is for plots that are MC only'    )
PARSER.add_argument('--cutstring', dest='CUTSTRING', default=''         , help='what the cutstring was for this set of plots'      )
