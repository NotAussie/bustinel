package helpers

import (
	"github.com/jamespfennell/gtfs"
	"github.com/notaussie/bustinel/internal/models"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.uber.org/zap"
)

// MongoDB collections
type Collections struct {
	Records *mongo.Collection
}

// App holds shared clients
type App struct {
	Logger      *zap.Logger
	Mongo       *mongo.Database
	Static      *gtfs.Static
	Collections *Collections
	Config      models.Config
}
