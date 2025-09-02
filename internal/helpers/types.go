// Reusable application helpers
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

// Shared application context
type App struct {
	Logger       *zap.Logger
	Mongo        *mongo.Database
	Static       *gtfs.Static
	Collections  *Collections
	Config       models.Config
	LastModified string
}
