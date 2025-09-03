// Reusable application helpers
package helpers

import (
	"github.com/NotAussie/bustinel/internal/models"
	"github.com/jamespfennell/gtfs"
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
