package services

import (
	"context"
	"errors"
	"io"
	"net/http"
	"time"

	"github.com/jamespfennell/gtfs"
	"github.com/notaussie/bustinel/internal/helpers"
	"github.com/notaussie/bustinel/internal/models"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.uber.org/zap"
)

// Retrieves real-time vehicle positions from a GTFS feed and stores new trip records in the database.
func FetchVehiclePositions(ctx context.Context, app *helpers.App) error {
	client := &http.Client{Timeout: 30 * time.Second}

	// Create HTTP request
	req, err := http.NewRequestWithContext(ctx, "GET", app.Config.FeedURL, nil)
	if err != nil {
		app.Logger.Error("Failed to create request", zap.Error(err))
		return err
	}
	app.Logger.Info("Fetching vehicle positions", zap.String("url", app.Config.FeedURL))
	resp, err := client.Do(req)
	if err != nil {
		app.Logger.Error("Failed to perform request", zap.Error(err))
		return err
	}
	if resp.StatusCode != http.StatusOK {
		app.Logger.Error("Unexpected response status", zap.Int("status", resp.StatusCode))
		return errors.New("unexpected response status: " + resp.Status)
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		app.Logger.Error("Failed to read response body", zap.Error(err))
		return err
	}

	// Parse GTFS real-time feed
	feed, err := gtfs.ParseRealtime(body, &gtfs.ParseRealtimeOptions{})
	if err != nil {
		app.Logger.Error("Failed to parse feed", zap.Error(err))
		return err
	}

	app.Logger.Info("Fetched vehicle positions", zap.Int("count", len(feed.Vehicles)))

	// Loop through each vehicle and process it
	documents := []models.Record{}
	for _, vehicle := range feed.Vehicles {
		// Get static metadata
		var route *gtfs.Route
		static := app.Static // Snapshot static data to prevent race conditions
		for i := range static.Routes {
			if static.Routes[i].Id == vehicle.Trip.ID.RouteID {
				route = &static.Routes[i]
				break
			}
		}
		if route == nil {
			app.Logger.Warn("Route not found for vehicle", zap.String("route_id", vehicle.Trip.ID.RouteID))
			continue
		}

		// Assemble record
		record := models.Record{
			Vehicle: models.Vehicle{
				ID:    vehicle.ID.ID,
				Label: &vehicle.ID.Label,
				Plate: &vehicle.ID.LicensePlate,
				Type:  models.VehicleType(route.Type),
			},
			Trip: models.Trip{
				ID: vehicle.Trip.ID.ID,
				Route: models.Route{
					ID:        route.Id,
					ShortName: &route.ShortName,
					LongName:  &route.LongName,
					Type:      models.VehicleType(route.Type),
				},
				Direction: uint64(vehicle.Trip.ID.DirectionID),
			},
			Agency: models.Agency{
				ID:       route.Agency.Id,
				Name:     route.Agency.Name,
				URL:      route.Agency.Url,
				Timezone: route.Agency.Timezone,
			},
			Timestamp: time.Now().UTC(),
		}

		// Check if the trip already exists, if not append it
		filter := map[string]interface{}{
			"trip.id":     record.Trip.ID,
			"agency.name": record.Agency.Name,
			"agency.id":   record.Agency.ID,
			"vehicle.id":  record.Vehicle.ID,
		}
		exists := app.Collections.Records.FindOne(ctx, filter)
		if exists.Err() != nil {
			if exists.Err() == mongo.ErrNoDocuments {
				documents = append(documents, record)
			} else {
				app.Logger.Error("Failed to check for existing trip record", zap.Error(exists.Err()), zap.Any("filter", filter), zap.String("collection", app.Collections.Records.Name()))
			}
		}
	}

	// Insert new trips to the database
	if len(documents) > 0 {
		_, err := app.Collections.Records.InsertMany(ctx, documents)
		if err != nil {
			app.Logger.Error("Failed to insert documents", zap.Error(err))
			return err
		}
		app.Logger.Info("Inserted new trip records", zap.Int("count", len(documents)))
	}

	return nil
}
;.