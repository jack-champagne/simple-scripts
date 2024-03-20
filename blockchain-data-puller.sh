PROJECT_ORGS=( "bitcoin" "ethereum" "bitcoinjs" "spesmilo" "bitcoinj" "consensys" "ckolivas" "btcsuite" "ethereumjs" "bitcoinbook" "iurimatias")

# Call command for each project
for projorg in "${PROJECT_ORGS[@]}"; do
    gh repo list $projorg --json nameWithOwner --jq "map(.nameWithOwner)"
    gh repo list $projorg --json watchers --json stargazerCount --json updatedAt --json pullRequests --json issues --json forkCount --json nameWithOwner --jq "map({
  forkCount,
  issueCount: .issues.totalCount,
  "pullRequestsCount": .pullRequests.totalCount,
  stargazerCount,
  updatedAt,
  watchersCount: .watchers.totalCount,
  nameWithOwner
})" > $projorg
done

# Build the proj orgs files by iterating over the array
PROJ_ORGS_FILES=""
for filename in "${PROJECT_ORGS[@]}"; do
    PROJ_ORGS_FILES+="${filename} "
done

jq "flatten" -s $PROJ_ORGS_FILES > data.json
