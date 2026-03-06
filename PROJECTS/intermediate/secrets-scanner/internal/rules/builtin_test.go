/*
©Vincent Plessy | 2026
builtin_test.go

Tests for rules/builtin.go

Tests:
  RegisterBuiltins loads at least 70 rules
  All rules have non-empty ID, description, keywords, and a non-nil pattern with no duplicates
  Pattern match correctness for 50+ services (AWS, GitHub, GitLab, GCP, Azure, Stripe,
    Twilio, Slack, JWT, SSH/PGP keys, DB connection strings, Shopify, npm, PyPI, Docker,
    Vault, DigitalOcean, Grafana, Databricks, HuggingFace, Supabase, and more)
  MatchKeywords routes content to the correct rule by keyword
  No false positives on benign code patterns (imports, constants, comments, loops)
*/

package rules

import (
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestRegisterBuiltins(t *testing.T) {
	t.Parallel()
	reg := NewRegistry()
	RegisterBuiltins(reg)
	assert.GreaterOrEqual(t, reg.Len(), 70)
}

func TestBuiltinRuleIDs(t *testing.T) {
	t.Parallel()
	reg := NewRegistry()
	RegisterBuiltins(reg)
	seen := make(map[string]bool)
	for _, r := range reg.All() {
		assert.NotEmpty(t, r.ID)
		assert.NotEmpty(t, r.Description)
		assert.NotEmpty(t, r.Keywords)
		assert.NotNil(t, r.Pattern)
		assert.False(t, seen[r.ID], "duplicate ID: %s", r.ID)
		seen[r.ID] = true
	}
}

func TestBuiltinPatternMatches(t *testing.T) { //nolint:funlen,gocognit
	t.Parallel()

	// Tokens are split across string literals to avoid triggering static secret
	// scanners (GitHub push protection) on test fixtures. The concatenation
	// happens at compile time so tests behave identically.
	ghPatClassic := "ghp_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij"       //nolint:gosec
	ghPatFine := "github_pat_" + "abcdefghijABCDEFGHIJKL_" +               //nolint:gosec
		"abcdefghij0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABC"
	ghOAuth := "gho_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij"            //nolint:gosec
	ghAppToken := "ghs_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij"         //nolint:gosec
	ghRefresh := "ghr_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij"          //nolint:gosec
	gitlabPAT := "glpat-" + "xYz1234567890AbCdEfGh"                        //nolint:gosec
	gitlabPipeline := "glptt-" + "abcdefghijklmnopqrstuvwxyz0123456789ABCD" //nolint:gosec
	gitlabRunner := "glrt-" + "xYz1234567890AbCdEfGh"                      //nolint:gosec
	gcpAPIKey := "AIzaSy" + "Dabcdefghij1234567890KLMNOPQRSTUV"             //nolint:gosec
	gcpOAuthSecret := "GOCSPX-" + "aBcDeFgHiJkLmNoPqRsTuVwXyZ01"          //nolint:gosec
	stripeWebhook := "whsec_" + "MfKBGsXP8r7B2cGnQ9jT6KxL12AbCdEf"        //nolint:gosec
	stripeRestrictedLive := "rk_live_" + "4eC39HqLyjWDarjtT1zdp7dc"        //nolint:gosec
	twilioAPIKey := "SK" + "1234567890abcdef1234567890abcdef"               //nolint:gosec
	twilioSID := "AC" + "1234567890abcdef1234567890abcdef"                  //nolint:gosec
	sendgridKey := "SG." + "aBcDeFgHiJkLmNoPqRsTuw" + "." +               //nolint:gosec
		"xYzAbCdEfGhIjKlMnOpQrStUvWxYzAbCdEfGhIjKlMn"
	shopifyAccessToken := "shpat_" + "abcdef0123456789abcdef0123456789"     //nolint:gosec
	shopifyCustomApp := "shpca_" + "abcdef0123456789abcdef0123456789"       //nolint:gosec
	shopifyPrivateApp := "shppa_" + "abcdef0123456789abcdef0123456789"      //nolint:gosec
	shopifySharedSecret := "shpss_" + "abcdef0123456789abcdef0123456789"    //nolint:gosec
	npmToken := "npm_" + "aBcDeFgHiJkLmNoPqRsTuVwXyZ0123456789"            //nolint:gosec
	rubygemsKey := "rubygems_" + "abcdef0123456789abcdef0123456789abcdef0123456789" //nolint:gosec
	dockerPAT := "dckr_pat_" + "aBcDeFgHiJkLmNoPqRsTuVwXyZ01"             //nolint:gosec
	vaultToken := "hvs." + "CAESIGH3YzJfaBcDeFgHiJkLmNoPqR"                //nolint:gosec
	digitalOceanPAT := "dop_v1_" + "abcdef01234567890abcdef01234567890" +    //nolint:gosec
		"abcdef01234567890abcdef0123456"
	linearAPIKey := "lin_api_" + "aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmN"      //nolint:gosec
	dopplerToken := "dp.st." + "aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmN"        //nolint:gosec
	grafanaSAToken := "glsa_" + "aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeF_12345678"       //nolint:gosec
	grafanaCloudToken := "glc_" + "aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeF1"             //nolint:gosec
	databricksToken := "dapi" + "1234567890abcdef1234567890abcdef"                  //nolint:gosec
	huggingfaceToken := "hf_" + "aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJ"            //nolint:gosec
	netlifyToken := "nfp_" + "aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmN"           //nolint:gosec
	postmanAPIKey := "PMAK-" + "abcdef0123456789abcdef01-" +                       //nolint:gosec
		"abcdef0123456789abcdef0123456789ab"
	figmaPAT := "figd_" + "aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmN"              //nolint:gosec
	flyioToken := "fo1_" + "aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmN"             //nolint:gosec
	planetscaleToken := "pscale_tkn_" + "aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmN" //nolint:gosec
	replicateToken := "r8_" + "aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqR"      //nolint:gosec
	sentryToken := "sntrys_" + "aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHi" //nolint:gosec
	atlassianToken := "ATATT" + "aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwX"            //nolint:gosec
	renderAPIKey := "rnd_" + "aBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHi"                //nolint:gosec
	ldSDKKey := "sdk-" + "a1b2c3d4-e5f6-7890-abcd-ef1234567890"                   //nolint:gosec
	ldAPIKey := "api-" + "a1b2c3d4-e5f6-7890-abcd-ef1234567890"                   //nolint:gosec

	tests := map[string]struct {
		ruleID    string
		input     string
		wantMatch bool
		wantGroup string
	}{
		"aws access key": { //nolint:gosec
			ruleID:    "aws-access-key-id",
			input:     `aws_key = "AKIAIOSFODNN7EXAMPLE"`,
			wantMatch: true,
			wantGroup: "AKIAIOSFODNN7EXAMPLE",
		},
		"aws access key ABIA prefix": {
			ruleID:    "aws-access-key-id",
			input:     `ABIAIOSFODNN7EXAMPL0`,
			wantMatch: true,
			wantGroup: "ABIAIOSFODNN7EXAMPL0",
		},
		"aws access key too short": {
			ruleID:    "aws-access-key-id",
			input:     `AKIA1234`,
			wantMatch: false,
		},
		"github pat classic": {
			ruleID:    "github-pat-classic",
			input:     ghPatClassic,
			wantMatch: true,
			wantGroup: ghPatClassic,
		},
		"github pat fine-grained": {
			ruleID:    "github-pat-fine",
			input:     ghPatFine,
			wantMatch: true,
		},
		"github oauth": {
			ruleID:    "github-oauth-token",
			input:     ghOAuth,
			wantMatch: true,
			wantGroup: ghOAuth,
		},
		"github app token": {
			ruleID:    "github-app-token",
			input:     ghAppToken,
			wantMatch: true,
			wantGroup: ghAppToken,
		},
		"github refresh token": {
			ruleID:    "github-refresh-token",
			input:     ghRefresh,
			wantMatch: true,
			wantGroup: ghRefresh,
		},
		"gitlab pat": {
			ruleID:    "gitlab-pat",
			input:     gitlabPAT,
			wantMatch: true,
			wantGroup: gitlabPAT,
		},
		"gitlab pipeline trigger": {
			ruleID:    "gitlab-pipeline-trigger",
			input:     gitlabPipeline,
			wantMatch: true,
			wantGroup: gitlabPipeline,
		},
		"gitlab runner token": {
			ruleID:    "gitlab-runner-token",
			input:     gitlabRunner,
			wantMatch: true,
			wantGroup: gitlabRunner,
		},
		"gcp api key": {
			ruleID:    "gcp-api-key",
			input:     gcpAPIKey,
			wantMatch: true,
		},
		"gcp service account": {
			ruleID:    "gcp-service-account",
			input:     `"type" : "service_account"`,
			wantMatch: true,
		},
		"gcp oauth secret": {
			ruleID:    "gcp-oauth-client-secret",
			input:     gcpOAuthSecret,
			wantMatch: true,
		},
		"azure storage key": {
			ruleID: "azure-storage-key",
			input: `AccountKey=` +
				`abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`,
			wantMatch: true,
		},
		"slack bot token": {
			ruleID:    "slack-bot-token",
			input:     `SLACK_BOT_TOKEN_EXAMPLE`,
			wantMatch: true,
		},
		"slack webhook": { //nolint:gosec
			ruleID:    "slack-webhook",
			input:     `https://example.invalid/slack-webhook`,
			wantMatch: true,
		},
		"stripe live key": { //nolint:gosec
			ruleID:    "stripe-live-secret",
			input:     `STRIPE_LIVE_KEY_EXAMPLE`,
			wantMatch: true,
			wantGroup: "STRIPE_LIVE_KEY_EXAMPLE",
		},
		"stripe test key": {
			ruleID:    "stripe-test-secret",
			input:     `STRIPE_TEST_KEY_EXAMPLE`, //nolint:gosec
			wantMatch: true,
			wantGroup: "STRIPE_TEST_KEY_EXAMPLE", //nolint:gosec
		},
		"stripe restricted live": { //nolint:gosec
			ruleID:    "stripe-live-restricted",
			input:     stripeRestrictedLive,
			wantMatch: true,
			wantGroup: stripeRestrictedLive,
		},
		"stripe webhook secret": {
			ruleID:    "stripe-webhook-secret",
			input:     stripeWebhook,
			wantMatch: true,
		},
		"twilio api key": {
			ruleID:    "twilio-api-key",
			input:     twilioAPIKey,
			wantMatch: true,
			wantGroup: twilioAPIKey,
		},
		"twilio account sid": {
			ruleID:    "twilio-account-sid",
			input:     twilioSID,
			wantMatch: true,
			wantGroup: twilioSID,
		},
		"sendgrid api key": {
			ruleID:    "sendgrid-api-key",
			input:     sendgridKey,
			wantMatch: true,
		},
		"shopify access token": {
			ruleID:    "shopify-access-token",
			input:     shopifyAccessToken,
			wantMatch: true,
			wantGroup: shopifyAccessToken,
		},
		"shopify custom app": {
			ruleID:    "shopify-custom-app",
			input:     shopifyCustomApp,
			wantMatch: true,
			wantGroup: shopifyCustomApp,
		},
		"shopify private app": {
			ruleID:    "shopify-private-app",
			input:     shopifyPrivateApp,
			wantMatch: true,
			wantGroup: shopifyPrivateApp,
		},
		"shopify shared secret": {
			ruleID:    "shopify-shared-secret",
			input:     shopifySharedSecret,
			wantMatch: true,
			wantGroup: shopifySharedSecret,
		},
		"npm access token": {
			ruleID:    "npm-access-token",
			input:     npmToken,
			wantMatch: true,
		},
		"pypi token": {
			ruleID: "pypi-api-token",
			input: `pypi-AgEIcHlwaS5vcmcCJDU5NTk5YTJhLWIwN2QtNDRkZi1iM` +
				`jIxLTk2OWU4YmViZDM3NgACKlszLCJjODA0ZWE1OC1kMjFiLTQzMjMtYWR` +
				`mNy0xZjQ4MGQ`,
			wantMatch: true,
		},
		"rubygems api key": {
			ruleID:    "rubygems-api-key",
			input:     rubygemsKey,
			wantMatch: true,
		},
		"docker hub pat": {
			ruleID:    "docker-hub-pat",
			input:     dockerPAT,
			wantMatch: true,
		},
		"jwt": {
			ruleID: "jwt-token",
			input: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.` +
				`eyJzdWIiOiIxMjM0NTY3ODkwIn0.` +
				`dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U`,
			wantMatch: true,
		},
		"rsa private key": { //nolint:gosec
			ruleID:    "ssh-private-key-rsa",
			input:     `-----BEGIN RSA PRIVATE KEY-----`,
			wantMatch: true,
		},
		"openssh private key": {
			ruleID:    "ssh-private-key-openssh",
			input:     `-----BEGIN OPENSSH PRIVATE KEY-----`, //nolint:gosec
			wantMatch: true,
		},
		"ec private key": { //nolint:gosec
			ruleID:    "ssh-private-key-ec",
			input:     `-----BEGIN EC PRIVATE KEY-----`,
			wantMatch: true,
		},
		"dsa private key": { //nolint:gosec
			ruleID:    "ssh-private-key-dsa",
			input:     `-----BEGIN DSA PRIVATE KEY-----`,
			wantMatch: true,
		},
		"pgp private key": { //nolint:gosec
			ruleID:    "pgp-private-key",
			input:     `-----BEGIN PGP PRIVATE KEY BLOCK-----`,
			wantMatch: true,
		},
		"pkcs8 private key": {
			ruleID:    "private-key-pkcs8",
			input:     `-----BEGIN PRIVATE KEY-----`,
			wantMatch: true,
		},
		"generic password": {
			ruleID:    "generic-password",
			input:     `password = "my$ecretP@ss99"`,
			wantMatch: true,
			wantGroup: "my$ecretP@ss99",
		},
		"generic password no match on short": {
			ruleID:    "generic-password",
			input:     `password = "abc"`,
			wantMatch: false,
		},
		"generic secret": {
			ruleID:    "generic-secret",
			input:     `secret_key = "xK9mP2vL5nQ8jR3tB7"`,
			wantMatch: true,
			wantGroup: "xK9mP2vL5nQ8jR3tB7",
		},
		"generic api key": {
			ruleID:    "generic-api-key",
			input:     `api_key = "aK9mP2vL5nQ8jR3tB7wX4cD"`,
			wantMatch: true,
			wantGroup: "aK9mP2vL5nQ8jR3tB7wX4cD",
		},
		"generic token": {
			ruleID:    "generic-token",
			input:     `access_token = "xK9mP2vL5nQ8jR3tB7wY"`,
			wantMatch: true,
			wantGroup: "xK9mP2vL5nQ8jR3tB7wY",
		},
		"postgres connection": { //nolint:gosec
			ruleID:    "postgres-connection",
			input:     `postgresql://admin:s3cr3t@db.example.com:5432/mydb`,
			wantMatch: true,
		},
		"mysql connection": { //nolint:gosec
			ruleID:    "mysql-connection",
			input:     `mysql://root:password123@127.0.0.1:3306/app`,
			wantMatch: true,
		},
		"mongodb connection": { //nolint:gosec
			ruleID:    "mongodb-connection",
			input:     `mongodb+srv://user:p4ssw0rd@cluster0.abc.mongodb.net/db`,
			wantMatch: true,
		},
		"redis connection": { //nolint:gosec
			ruleID:    "redis-connection",
			input:     `redis://default:s3cret@redis.example.com:6379/0`,
			wantMatch: true,
		},
		"hashicorp vault token": {
			ruleID:    "hashicorp-vault-token",
			input:     vaultToken,
			wantMatch: true,
		},
		"digitalocean pat": {
			ruleID:    "digitalocean-pat",
			input:     digitalOceanPAT,
			wantMatch: true,
			wantGroup: digitalOceanPAT,
		},
		"linear api key": {
			ruleID:    "linear-api-key",
			input:     linearAPIKey,
			wantMatch: true,
		},
		"age secret key": {
			ruleID:    "age-secret-key",
			input:     `AGE-SECRET-KEY-1QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ`,
			wantMatch: true,
		},
		"doppler token": {
			ruleID:    "doppler-token",
			input:     dopplerToken,
			wantMatch: true,
		},
		"grafana sa token": {
			ruleID:    "grafana-api-key",
			input:     grafanaSAToken,
			wantMatch: true,
		},
		"grafana cloud token": {
			ruleID:    "grafana-cloud-token",
			input:     grafanaCloudToken,
			wantMatch: true,
		},
		"databricks token": {
			ruleID:    "databricks-token",
			input:     databricksToken,
			wantMatch: true,
			wantGroup: databricksToken,
		},
		"huggingface token": {
			ruleID:    "huggingface-token",
			input:     huggingfaceToken,
			wantMatch: true,
			wantGroup: huggingfaceToken,
		},
		"netlify token": {
			ruleID:    "netlify-token",
			input:     netlifyToken,
			wantMatch: true,
		},
		"postman api key": {
			ruleID:    "postman-api-key",
			input:     postmanAPIKey,
			wantMatch: true,
		},
		"figma pat": {
			ruleID:    "figma-pat",
			input:     figmaPAT,
			wantMatch: true,
		},
		"flyio token": {
			ruleID:    "flyio-token",
			input:     flyioToken,
			wantMatch: true,
		},
		"planetscale token": {
			ruleID:    "planetscale-token",
			input:     planetscaleToken,
			wantMatch: true,
		},
		"replicate token": {
			ruleID:    "replicate-api-token",
			input:     replicateToken,
			wantMatch: true,
		},
		"sentry auth token": {
			ruleID:    "sentry-auth-token",
			input:     sentryToken,
			wantMatch: true,
		},
		"atlassian token": {
			ruleID:    "atlassian-api-token",
			input:     atlassianToken,
			wantMatch: true,
		},
		"render api key": {
			ruleID:    "render-api-key",
			input:     renderAPIKey,
			wantMatch: true,
		},
		"launchdarkly sdk key": {
			ruleID:    "launchdarkly-sdk-key",
			input:     ldSDKKey,
			wantMatch: true,
			wantGroup: ldSDKKey,
		},
		"launchdarkly api key": {
			ruleID:    "launchdarkly-api-key",
			input:     ldAPIKey,
			wantMatch: true,
			wantGroup: ldAPIKey,
		},
		"okta api token": {
			ruleID:    "okta-api-token",
			input:     `OKTA_API_TOKEN = "00ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijkl"`,
			wantMatch: true,
			wantGroup: "00ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijkl",
		},
		"okta ssws header": {
			ruleID:    "okta-api-token",
			input:     `SSWS = "00xK9mP2vL5nQ8jR3tB7wX4cD6eF8gH0iJ2kL"`,
			wantMatch: true,
			wantGroup: "00xK9mP2vL5nQ8jR3tB7wX4cD6eF8gH0iJ2kL",
		},
		"supabase service key": {
			ruleID:    "supabase-service-key",
			input:     `SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJvbGUiOiJzZXJ2aWNlX3JvbGUifQ.xxxxxxxx`,
			wantMatch: true,
			wantGroup: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJvbGUiOiJzZXJ2aWNlX3JvbGUifQ.xxxxxxxx",
		},
		"supabase service key quoted": {
			ruleID:    "supabase-service-key",
			input:     `SUPABASE_SERVICE_ROLE_KEY="eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIn0.sig123"`,
			wantMatch: true,
		},
		"no match on normal text": {
			ruleID:    "aws-access-key-id",
			input:     `this is just normal code`,
			wantMatch: false,
		},
	}

	reg := NewRegistry()
	RegisterBuiltins(reg)

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			t.Parallel()
			rule, ok := reg.Get(tc.ruleID)
			require.True(t, ok, "rule %s not found", tc.ruleID)

			match := rule.Pattern.FindStringSubmatch(tc.input)
			if tc.wantMatch {
				require.NotNil(t, match,
					"expected pattern match for rule %s", tc.ruleID)
				if tc.wantGroup != "" && rule.SecretGroup > 0 {
					require.Greater(t, len(match), rule.SecretGroup)
					assert.Equal(t, tc.wantGroup,
						match[rule.SecretGroup])
				}
			} else {
				assert.Nil(t, match,
					"unexpected match for rule %s", tc.ruleID)
			}
		})
	}
}

func TestBuiltinKeywordMatches(t *testing.T) {
	t.Parallel()
	reg := NewRegistry()
	RegisterBuiltins(reg)

	tests := map[string]struct {
		content string
		wantIDs []string
	}{
		"aws content": { //nolint:gosec
			content: "found AKIAIOSFODNN7EXAMPLE in config",
			wantIDs: []string{"aws-access-key-id"},
		},
		"github content": {
			content: "token = ghp_abc123",
			wantIDs: []string{"github-pat-classic"},
		},
		"stripe content": {
			content: "key = sk_live_abc123",
			wantIDs: []string{"stripe-live-secret"},
		},
		"private key content": { //nolint:gosec
			content: "-----BEGIN RSA PRIVATE KEY-----",
			wantIDs: []string{"ssh-private-key-rsa"},
		},
		"postgres content": { //nolint:gosec
			content: "DATABASE_URL=postgres://user:pass@host/db",
			wantIDs: []string{"postgres-connection"},
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			t.Parallel()
			matched := reg.MatchKeywords(tc.content)
			ids := make([]string, len(matched))
			for i, r := range matched {
				ids[i] = r.ID
			}
			for _, wantID := range tc.wantIDs {
				assert.Contains(t, ids, wantID)
			}
		})
	}
}

func TestBuiltinNoFalsePositives(t *testing.T) {
	t.Parallel()

	reg := NewRegistry()
	RegisterBuiltins(reg)

	benignInputs := []string{
		`import os`,
		`func main() {}`,
		`const x = 42`,
		`// this is a comment`,
		`print("hello world")`,
		`if err != nil { return err }`,
		`for i := 0; i < 10; i++ {}`,
	}

	for _, rule := range reg.All() {
		for _, input := range benignInputs {
			match := rule.Pattern.FindString(input)
			assert.Empty(t, match,
				"rule %s false positive on: %s", rule.ID, input)
		}
	}
}
