package testfixtures

import (
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

// Path provides existing fixtures and synthetic values in a temporary directory.
func Path(t testing.TB, parts ...string) string {
	t.Helper()
	_, file, _, _ := runtime.Caller(0)
	source := filepath.Join(filepath.Dir(file), "..", "..", "tests", "testdata")
	dir := t.TempDir()
	err := filepath.WalkDir(source, func(path string, entry os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		relative, err := filepath.Rel(source, path)
		if err != nil {
			return err
		}
		destination := filepath.Join(dir, relative)
		if entry.IsDir() {
			return os.MkdirAll(destination, 0o700)
		}
		data, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		return os.WriteFile(destination, data, 0o600)
	})
	if err != nil {
		t.Fatal(err)
	}
	values := [][2]string{
		{"AWS_ACCESS_KEY_ID", "AKIA" + strings.Repeat("0", 16)},
		{"AWS_SECRET_ACCESS_KEY", strings.Repeat("A", 40)},
		{"DATABASE_URL", "postgres://demo:synthetic@database.invalid/demo"},
		{"MONGODB_URI", "mongodb://demo:synthetic@database.invalid/demo"},
		{"POSTGRES_PASSWORD", "synthetic-test-password"},
		{"STRIPE_SECRET_KEY", "sk_" + "live_" + "abcdefghijklmnopqrstuvwx"},
		{"GITHUB_TOKEN", "gh" + "p_" + strings.Repeat("A", 36)},
		{"OPEN" + "AI_API_KEY", "sk-" + strings.Repeat("A", 48)},
		{"JWT_SECRET", "synthetic-signing-secret"},
		{"API_KEY", "synthetic-test-api-key"},
		{"PASSWORD", "synthetic-test-password"},
	}
	var dockerfile, compose strings.Builder
	dockerfile.WriteString("FROM alpine:3.20\n")
	compose.WriteString("services:\n  app:\n    image: alpine:3.20\n    environment:\n")
	for _, value := range values {
		fmt.Fprintf(&dockerfile, "ENV %s=%q\n", value[0], value[1])
		fmt.Fprintf(&compose, "      %s: %q\n", value[0], value[1])
	}
	for path, content := range map[string]string{"dockerfiles/bad-secrets.Dockerfile": dockerfile.String(), "compose/bad-secrets.yml": compose.String()} {
		if err := os.WriteFile(filepath.Join(dir, path), []byte(content), 0o600); err != nil {
			t.Fatal(err)
		}
	}
	return filepath.Join(append([]string{dir}, parts...)...)
}
