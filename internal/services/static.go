package services

import (
	"context"
	"errors"
	"io"
	"net/http"
	"time"

	"github.com/NotAussie/bustinel/internal/helpers"
	"github.com/jamespfennell/gtfs"
	"go.uber.org/zap"
)

// Retrieves GTFS static data and stores the parsed data into the global app storage
func FetchStaticData(ctx context.Context, app *helpers.App) error {
	client := &http.Client{Timeout: 30 * time.Second}

	app.Logger.Info("Fetching static data", zap.String("url", app.Config.MetadataURL))

	// Create HTTP request
	req, err := http.NewRequestWithContext(ctx, "GET", app.Config.MetadataURL, nil)
	if err != nil {
		app.Logger.Error("Failed to create request", zap.Error(err))
		return err
	}
	if app.LastModified != "" {
		req.Header.Set("If-Modified-Since", app.LastModified)
	}
	if app.Config.Authorisation != nil {
		req.Header.Set(app.Config.AuthorisationHeader, *app.Config.Authorisation)
	}
	resp, err := client.Do(req)
	if err != nil {
		app.Logger.Error("Failed to perform request", zap.Error(err))
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode == http.StatusNotModified {
		app.Logger.Info("Static data not modified", zap.String("url", app.Config.MetadataURL), zap.String("last_modified", app.LastModified))
		return nil
	}
	if resp.StatusCode != http.StatusOK {
		app.Logger.Error("Unexpected response status", zap.Int("status", resp.StatusCode))
		return errors.New("unexpected response status: " + resp.Status)
	}
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
