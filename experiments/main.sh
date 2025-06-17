#!/usr/bin/env sh
set -xeu
pushd ./fcp
sudo ionice -c3 nice -n 10 contain experiments --proof-loop-budget 16 --attempt-budget 2 --models "snt4" --models "ops4" --models "gpt41" --models "o3"
popd
