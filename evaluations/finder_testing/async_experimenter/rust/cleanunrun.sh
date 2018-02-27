#! /bin/sh
#
# cleanunrun.sh
# Copyright (C) 2017 huang <huang@huang-Precision-WorkStation-T3500>
#
# Distributed under terms of the MIT license.
#


for i in `cat unrun.log`
do
    echo $i
    rm -rf $i
done
