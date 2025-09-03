package main

import (
	"context"
	"os"
	"os/signal"
	"syscall"

	"github.com/notaussie/bustinel/internal/helpers"
	"github.com/notaussie/bustinel/internal/services"
	"github.com/robfig/cron/v3"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
	"go.uber.org/zap"
)

// Application entry point
func main() {
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	// Initialise logging
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	app := &helpers.App{
		Logger: logger,
		Config: helpers.LoadConfig(logger),
	}

	// Connect to MongoDB
	client, err := mongo.Connect(options.Client().ApplyURI(app.Config.MongoURI))
	if err != nil {
		logger.Fatal("Failed to connect to MongoDB", zap.Error(err))
	}
	defer client.Disconnect(ctx)

	// Test MongoDB connection
	err = client.Ping(ctx, nil)
	if err != nil {
		logger.Fatal("Failed to ping MongoDB", zap.Error(err))
	}
	logger.Info("MongoDB connection established")

	// Set up MongoDB database and collections
	app.Mongo = client.Database(app.Config.MongoDatabase)
	app.Collections = &helpers.Collections{
		Records: app.Mongo.Collection("records"),
	}

	// Pre-fetch the GTFS feed's static data
	err = services.FetchStaticData(ctx, app)
	if err != nil {
		logger.Fatal("Error doing first fetch of static data", zap.Error(err))
	}

	// Create CRON jobs
	c := cron.New()
	c.Start()
	defer c.Stop()

	// Vehicle positions
	_, err = c.AddFunc(app.Config.FeedRefreshInterval, func() {
		if err := services.FetchVehiclePositions(ctx, app); err != nil {
			logger.Error("Error fetching vehicle positions", zap.Error(err))
		}
	})
	if err != nil {
		logger.Error("Error adding cron job", zap.Error(err))
	}

	// Static data
	_, err = c.AddFunc(app.Config.MetadataRefreshInterval, func() {
		err := services.FetchStaticData(ctx, app)
		if err != nil {
			logger.Error("Error fetching static data", zap.Error(err))
		}
	})
	if err != nil {
		logger.Error("Error adding cron job", zap.Error(err))
	}

	<-ctx.Done()
	defer logger.Info("Shutting down")
}
