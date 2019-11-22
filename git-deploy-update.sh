# deploy merges changes from devel repo

development_branch=${1:-devel}
production_branch=${2:-deploy}
development_repo=${3:-development}
with_submodules=${4:-nosubs}
pip_installs=${5:-1} # default True
pip_requires="requirements.txt"

if [[ "${with_submodules}" -eq "nosubs" ]]; then
   with_submodules='';
else
   with_submodules='--recurse-submodules';
fi

git checkout \
    ${production_branch} \
    && \
git pull \
    --verbose \
    --no-edit \
    --tags \
    ${with_submodules} \
    ${development_repo} \
    ${development_branch}


# check pip_installs match 1, [Yy]es, [Tt]rue
if [ $? -eq 0  -a \
    $(expr $pip_installs : '^[1YyTt].*') -gt 0 ]; then
  #pip install -q -r ${pip_requires}
  pip install -r ${pip_requires}
fi
