// Reusable application helpers
package helpers

import (
	"os"
	"regexp"

	"github.com/notaussie/bustinel/internal/models"
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
			return "*/1 * * * *"
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
	}
}
