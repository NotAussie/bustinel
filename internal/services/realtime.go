package services

import (
	"context"
	"io"
	"net/http"

	"github.com/jamespfennell/gtfs"
	"github.com/notaussie/bustinel/internal/helpers"
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

	for _, vehicle := range feed.Vehicles {
		app.Logger.Info("Vehicle found", zap.String("vehicle_id", vehicle.ID.ID), zap.String("vehicle_label", vehicle.ID.Label), zap.String("trip_id", vehicle.Trip.ID.ID), zap.String("route_id", vehicle.Trip.ID.RouteID))
	}
	return nil
}
