package models

// Config
type Config struct {
	Environment             string
	MongoURI                string
	MongoDatabase           string
	FeedURL                 string
	MetadataURL             string
	MetadataRefreshInterval string // CRON
	FeedRefreshInterval     string // CRON
}
