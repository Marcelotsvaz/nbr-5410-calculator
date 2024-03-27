#! /usr/bin/env fish

function header
	echo -n $spacing
	
	set line $(set_color blue --bold; string repeat --count 80 -; set_color normal)
	
	echo $line
	echo $argv
	echo $line
	
	set -g spacing \n
end


argparse coverage -- $argv
or return


set unittestCommand unittest discover --pattern \*_tests.py --start-directory tests/ --verbose


if set --query _flag_coverage
	header Running tests with code coverage
	coverage run -m $unittestCommand
	
	header Coverage report
	coverage report && coverage xml
else
	header Running tests
	python -m $unittestCommand
end