// Reusable application models
package models

import "time"

// Represents all configurable application settings
type Config struct {
	Environment             string
	MongoURI                string
	MongoDatabase           string
	FeedURL                 string
	MetadataURL             string
	MetadataRefreshInterval string // CRON format
	FeedRefreshInterval     string // CRON format
	Authorisation           *string
	AuthorisationHeader     string
	Contact                 string
	Timeout                 time.Duration
}
