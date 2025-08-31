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

	client, _ := mongo.Connect(options.Client().ApplyURI("mongodb://localhost:27017"))

	app := &helpers.App{
		Logger: logger,
		Mongo:  client.Database("bustinel"),
	}

	// initial static fetch
	services.FetchStaticData(ctx, app)

	_, err := c.AddFunc("*/1 * * * *", func() {
		if err := services.FetchVehiclePositions(ctx, app); err != nil {
			logger.Error("Error fetching vehicle positions", zap.Error(err))
		}
	})
	if err != nil {
		logger.Error("Error adding cron job", zap.Error(err))
	}

	_, err = c.AddFunc("0 * * * *", func() {
		if err := services.FetchStaticData(ctx, app); err != nil {
			logger.Error("Error fetching static data", zap.Error(err))
		}
	})
	if err != nil {
		logger.Error("Error adding cron job", zap.Error(err))
	}

	c.Start()
	defer c.Stop()
	defer func() {
		if err = client.Disconnect(ctx); err != nil {
			panic(err)
		}
	}()

	select {}
}
