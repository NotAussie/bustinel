package helpers

import (
	"os"

	"github.com/notaussie/bustinel/internal/models"
	"go.uber.org/zap"
)

func getEnvOrDefault(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}

func getEnvOrFatal(key string, logger *zap.Logger) string {
	value := os.Getenv(key)
	if value == "" {
		logger.Fatal("Missing required environment variable", zap.String("key", key))
	}
	return value
}

func LoadConfigFromEnv(logger *zap.Logger) models.Config {
	return models.Config{
		Environment:             getEnvOrDefault("ENVIRONMENT", "production"),
		MongoURI:                getEnvOrFatal("MONGO_URI", logger),
		FeedURL:                 getEnvOrFatal("FEED_URL", logger),
		MetadataURL:             getEnvOrFatal("METADATA_URL", logger),
		MetadataRefreshInterval: getEnvOrDefault("METADATA_REFRESH_INTERVAL", "*/1 * * * *"),
		FeedRefreshInterval:     getEnvOrDefault("FEED_REFRESH_INTERVAL", "0 * * * *"),
	}
}
