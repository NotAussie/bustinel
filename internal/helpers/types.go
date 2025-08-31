package helpers

import (
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.uber.org/zap"
	"github.com/jamespfennell/gtfs"
)

// App holds shared clients
type App struct {

	// Application logger
	Logger *zap.Logger
	Mongo  *mongo.Database
	Static *gtfs.Static
}
