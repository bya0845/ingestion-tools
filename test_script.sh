#!/bin/bash
# This is an unformatted shell script
function test_function() {
	local variable="value"
	if [ $variable == "value" ]; then
		echo "Hello World"
	else
		echo "World"
	fi
}
