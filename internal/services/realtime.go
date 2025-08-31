package services

import (
	"context"
	"io"
	"net/http"

	"github.com/jamespfennell/gtfs"
	"github.com/notaussie/bustinel/internal/helpers"
	"github.com/notaussie/bustinel/internal/models"
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

	req, err := http.NewRequestWithContext(ctx, "GET", "https://gtfs.adelaidemetro.com.au/v1/realtime/vehicle_positions", nil)
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
				Direction: vehicle.Trip.ID.DirectionID.String(),
			},
			Agency: models.Agency{
				ID:       route.Agency.Id,
				Name:     route.Agency.Name,
				URL:      route.Agency.Url,
				Timezone: route.Agency.Timezone,
			},
			Timestamp: *vehicle.Timestamp,
		}
		app.Logger.Info("Vehicle record", zap.Any("record", record))
	}
	return nil
}
