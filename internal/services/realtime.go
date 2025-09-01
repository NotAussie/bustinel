package services

import (
	"context"
	"io"
	"net/http"

	"github.com/jamespfennell/gtfs"
	"github.com/notaussie/bustinel/internal/helpers"
	"github.com/notaussie/bustinel/internal/models"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.uber.org/zap"
)

// FetchVehiclePositions retrieves real-time vehicle position data from the MTA GTFS API,
// parses the response, and logs each vehicle's information in JSON format.
// It returns an error if any step in the request, response reading, or parsing fails.
//
// Parameters:
//   - ctx: The context for controlling request cancellation and timeouts.
//   - app: The application helper containing logger and configuration.
//
// Returns:
//   - error: An error if the request, response reading, or parsing fails; otherwise, nil.
func FetchVehiclePositions(ctx context.Context, app *helpers.App) error {
	client := &http.Client{}

	app.Logger.Info("Fetching vehicle positions")

	req, err := http.NewRequestWithContext(ctx, "GET", app.Config.FeedURL, nil)
	if err != nil {
		app.Logger.Error("Failed to create request", zap.Error(err))
		return err
	}
	resp, err := client.Do(req)
	if err != nil {
		app.Logger.Error("Failed to perform request", zap.Error(err))
		return err
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		app.Logger.Error("Failed to read response body", zap.Error(err))
		return err
	}

	feed, err := gtfs.ParseRealtime(body, &gtfs.ParseRealtimeOptions{})
	if err != nil {
		app.Logger.Error("Failed to parse feed", zap.Error(err))
		return err
	}

	app.Logger.Info("Fetched vehicle positions", zap.Int("count", len(feed.Vehicles)))

	documents := []models.Record{}
	for _, vehicle := range feed.Vehicles {
		// Get static metadata
		var route *gtfs.Route
		for _, r := range app.Static.Routes {
			if r.Id == vehicle.Trip.ID.RouteID {
				route = &r
				break
			}
		}
		if route == nil {
			app.Logger.Warn("Route not found for vehicle", zap.String("route_id", vehicle.Trip.ID.RouteID))
			continue
		}

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
			Timestamp: *vehicle.Timestamp,
		}

		filter := map[string]interface{}{
			"trip.id":     record.Trip.ID,
			"agency.name": record.Agency.Name,
			"agency.id":   record.Agency.ID,
			"vehicle.id":  record.Vehicle.ID,
		}
		exists := app.Collections.Records.FindOne(ctx, filter)
		if exists.Err() != nil {
			if exists.Err() == mongo.ErrNoDocuments {
				_, err = app.Collections.Records.InsertOne(ctx, record)
				documents = append(documents, record)
				app.Logger.Info("Trip record appended", zap.Any("record", record))
				continue
			}
			app.Logger.Error("Failed to check for existing trip record", zap.Error(exists.Err()), zap.Any("filter", filter), zap.String("collection", app.Collections.Records.Name()))
			continue
		}
	}

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
