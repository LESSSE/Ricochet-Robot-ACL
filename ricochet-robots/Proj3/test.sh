#! /bin/bash
# usage: test.sh [test-files] 
function debug { echo $@ >&2; }

for f in `ls ./Problems/*.rr | sort -n -t - -k 2`; do
	
	base=$(basename "$f" ".rr")
	echo "========================$f======================"
	./proj3 "$f" > "Resolve/$base.sol" 2>"Resolve/$base.err"
	./rr_checker "$f" "Resolve/$base.sol" 	
	diff <(head -n 1 "Resolve/$base.sol") <(head -n 1 "Solutions/$base.sol")
	
done
#debug "generated cube of size $size with <= $alive_n alive cells in $SECONDS seconds."
