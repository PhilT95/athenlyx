# Practical commands for general linux CLI usage


|Category|Command|Purpose and Usage|Examples|
|:-------|:------|:----------------|:-------|
|Basic|`history`| Views the command history||
||`!10`| Execute the 10th command in history||
||!!|Execute the previous command||
|Read File|`cat`|Read a file|`cat sample.txt`|
||`head`|Read the first 10 lines of a file|`head sample.txt`|
||`tail`|Read the last 10 lines of a file|`tail sample.txt`|
|Find & Filter|`cut`|Cut a specific field. The example cuts the first field.|`cat sample.txt \| cut -f 1`|
|||Cut the 1st column.|`cat sample.txt \| cut -c1`|
||`grep`|Filter specific keywords.|`cat sample.txt \| grep 'keywords'`|
||`sort`|Sorts outputs alphabetically.|`cat sample.txt \| sort`|
|||Sorts output numerically.|`cat sample.txt \| sort -n`|
||`uniq`|Eliminates duplicate lines.|`cat sample.txt \| uniq`|
||`wc -l`|Count line numbers.|`cat sample.txt \| wc -l`|
||`n1`|Show line numbers.|`cat sample.txt \| n1`|
|Advanced|`sed`|Prints specific lines. For example line 11.|`cat sample.txt \| sed -n '11p'`|
|||Print lines between 10-15.|`cat sample.txt \| sed -n '10,15p'`|
||`awk`|Print lines below 11.|`cat sample.txt \| awk 'NR < 11 {print $0}'`|
|||Print line 11|`cat sample.txt \| awk 'NR == 11 {print $0}'`|
