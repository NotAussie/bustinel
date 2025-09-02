package services

import (
	"context"
	"io"
	"net/http"

	"github.com/jamespfennell/gtfs"
	"github.com/notaussie/bustinel/internal/helpers"
	"go.uber.org/zap"
)

// Retrieves GTFS static data and stores the parsed data into the global app storage
func FetchStaticData(ctx context.Context, app *helpers.App) error {
	client := &http.Client{}

	app.Logger.Info("Fetching static data", zap.String("url", app.Config.MetadataURL))

	// Create HTTP request
	req, err := http.NewRequestWithContext(ctx, "GET", app.Config.MetadataURL, nil)
	req.Header.Set("If-Modified-Since", app.LastModified)
	if err != nil {
		app.Logger.Error("Failed to create request", zap.Error(err))
		return err
	}
	resp, err := client.Do(req)
	if err != nil {
		app.Logger.Error("Failed to perform request", zap.Error(err))
		return err
	}
	if resp.StatusCode == http.StatusNotModified {
		app.Logger.Info("Static data not modified", zap.String("url", app.Config.MetadataURL), zap.String("last_modified", app.LastModified))
		return nil
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		app.Logger.Error("Failed to read response body", zap.Error(err))
		return err
	}

	// Parse GTFS static data and store it globally
	static, err := gtfs.ParseStatic(body, gtfs.ParseStaticOptions{InheritWheelchairBoarding: true})
	if err != nil {
		app.Logger.Error("Failed to parse static data", zap.Error(err))
		return err
	}
	app.Static = static

	app.LastModified = resp.Header.Get("Last-Modified")
	app.Logger.Info("Fetched static data", zap.String("url", app.Config.MetadataURL), zap.String("last_modified", app.LastModified), zap.Int("stops", len(static.Stops)), zap.Int("routes", len(static.Routes)), zap.Int("agencies", len(static.Agencies)))

	return nil
}
