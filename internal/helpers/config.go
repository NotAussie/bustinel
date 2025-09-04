// Reusable application helpers
package helpers

import (
	"os"
	"regexp"
	"strconv"
	"strings"
	"time"

	"github.com/NotAussie/bustinel/internal/models"
	"go.uber.org/zap"
)

var email = regexp.MustCompile(`^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`)

// Loads application configuration from environment variables
func LoadConfig(logger *zap.Logger) models.Config {
	return models.Config{
		Environment: func() string {
			if v := os.Getenv("ENVIRONMENT"); v != "" {
				return v
			}
			return "production"
		}(),
		MongoURI: func() string {
			if v := os.Getenv("MONGO_URI"); v != "" {
				return v
			}
			logger.Fatal("Missing required environment variable", zap.String("key", "MONGO_URI"))
			return ""
		}(),
		MongoDatabase: func() string {
			if v := strings.TrimSpace(os.Getenv("MONGO_DATABASE")); v != "" {
				return v
			}
			return "bustinel"
		}(),
		FeedURL: func() string {
			if v := os.Getenv("FEED_URL"); v != "" {
				return v
			}
			logger.Fatal("Missing required environment variable", zap.String("key", "FEED_URL"))
			return ""
		}(),
		MetadataURL: func() string {
			if v := os.Getenv("METADATA_URL"); v != "" {
				return v
			}
			logger.Fatal("Missing required environment variable", zap.String("key", "METADATA_URL"))
			return ""
		}(),
		MetadataRefreshInterval: func() string {
			if v := os.Getenv("METADATA_REFRESH_INTERVAL"); v != "" {
				return v
			}
			return "0 * * * *"
		}(),
		FeedRefreshInterval: func() string {
			if v := os.Getenv("FEED_REFRESH_INTERVAL"); v != "" {
				return v
			}
			return "* * * * *"
		}(),
		Authorisation: func() *string {
			if v := os.Getenv("AUTHORIZATION"); v != "" {
				return &v
			}
			return nil
		}(),
		AuthorisationHeader: func() string {
			if v := os.Getenv("AUTHORIZATION_HEADER"); v != "" {
				return v
			}
			return "Authorization"
		}(),
		Contact: func() string {
			if v := os.Getenv("CONTACT"); v != "" {
				if matched := email.MatchString(v); matched {
					return v
				}
				logger.Fatal("Invalid CONTACT email format", zap.String("value", v))
				return ""
			}
			return ""
		}(),
		Timeout: func() time.Duration {
			if v := strings.TrimSpace(os.Getenv("TIMEOUT")); v != "" {
				if parsed, err := strconv.Atoi(v); err == nil {
					if parsed < 30 {
						logger.Fatal("Invalid TIMEOUT value: must be >= 30", zap.String("value", v))
					}
					return time.Duration(parsed) * time.Second
				}
				logger.Fatal("Invalid TIMEOUT value: expected integer seconds or Go duration (e.g., 500ms, 30s, 1m)", zap.String("value", v))
			}
			return 30 * time.Second
		}(),
	}
}
