#!/usr/bin/env bash
set -o pipefail

# Acquire our secrets
FILE=secrets/github_settings.sh

if [ -f $FILE ]; then
    . $FILE
else
    echo "File $FILE does not exist."
    exit 1
fi

# Generate a JWT for the GitHub App

echo $PRIVATE_KEY_PATH
echo $APP_ID

now=$(date +%s)
iat=$((${now} - 60)) # Issues 60 seconds in the past
exp=$((${now} + 600)) # Expires 10 minutes in the future

b64enc() { openssl base64 | tr -d '=' | tr '/+' '_-' | tr -d '\n'; }

header_json='{
    "typ":"JWT",
    "alg":"RS256"
}'
header=$( echo -n "${header_json}" | b64enc )

payload_json="{
    \"iat\":${iat},
    \"exp\":${exp},
    \"iss\":\"${APP_ID}\"
}"
payload=$( echo -n "${payload_json}" | b64enc )

header_payload="${header}"."${payload}"
signature=$(
    openssl dgst -sha256 -sign $PRIVATE_KEY_PATH \
    <(echo -n "${header_payload}") | b64enc
)

JWT="${header_payload}"."${signature}"
printf '%s\n' "JWT: $JWT"

# Get Installation Access Token 

response=$(curl --request POST \
--url "https://api.github.com/app/installations/$INSTALLATION_ID/access_tokens" \
--header "Accept: application/vnd.github+json" \
--header "Authorization: Bearer $JWT" \
--header "X-GitHub-Api-Version: 2022-11-28")
token=$(echo $response | grep -o '"token": *"[^"]*' | cut -d'"' -f4)

# Post our re-run request

endpoint="https://api.github.com/repos/NCIOCPL/teams-notifications/actions/runs/$RUN_ID/rerun"
echo $endpoint
curl --request POST \
--url $endpoint \
--header "Accept: application/vnd.github+json" \
--header "Authorization: token $token" \
--header "X-GitHub-Api-Version: 2022-11-28"