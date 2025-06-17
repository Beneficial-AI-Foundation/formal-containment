#!/usr/bin/env sh
set -xeu
pushd ./fcp
sudo ionice -c3 nice -n 10 contain experiments --proof-loop-budget 1 --attempt-budget 1 --models "hku35"
popd
