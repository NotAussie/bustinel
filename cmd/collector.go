package main

import (
	"context"

	"github.com/notaussie/bustinel/internal/helpers"
	"github.com/notaussie/bustinel/internal/services"
	"github.com/robfig/cron/v3"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
	"go.uber.org/zap"
)

// Main initializes the application logger, sets up a cron job to periodically fetch vehicle positions,
// and starts the cron scheduler. The cron job runs every minute and logs any errors encountered during
// the fetch operation. The function blocks indefinitely to keep the application running.
func main() {
	ctx := context.Background()
	c := cron.New()

	logger, _ := zap.NewProduction()
	defer logger.Sync()

	app := &helpers.App{
		Logger: logger,
		Config: helpers.LoadConfigFromEnv(logger),
	}

	client, err := mongo.Connect(options.Client().ApplyURI(app.Config.MongoURI))
	if err != nil {
		logger.Fatal("Failed to connect to MongoDB", zap.Error(err))
	}
	defer client.Disconnect(ctx)

	app.Mongo = client.Database("bustinel")
	app.Collections = &helpers.Collections{
		Records: client.Database("bustinel").Collection("records"),
	}

	err = services.FetchStaticData(ctx, app)
	if err != nil {
		logger.Fatal("Error doing first fetch of static data", zap.Error(err))
	}

	_, err = c.AddFunc("*/1 * * * *", func() {
		if err := services.FetchVehiclePositions(ctx, app); err != nil {
			logger.Error("Error fetching vehicle positions", zap.Error(err))
		}
	})
	if err != nil {
		logger.Error("Error adding cron job", zap.Error(err))
	}

	_, err = c.AddFunc("0 * * * *", func() {
		err := services.FetchStaticData(ctx, app)
		if err != nil {
			logger.Error("Error fetching static data", zap.Error(err))
		}
	})
	if err != nil {
		logger.Error("Error adding cron job", zap.Error(err))
	}

	c.Start()
	defer c.Stop()
	select {}
}
