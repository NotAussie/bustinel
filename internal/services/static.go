package services

import (
	"context"
	"io"
	"net/http"

	"github.com/jamespfennell/gtfs"
	"github.com/notaussie/bustinel/internal/helpers"
	"go.uber.org/zap"
)

func FetchStaticData(ctx context.Context, app *helpers.App) error {
	client := &http.Client{}

	app.Logger.Info("Fetching static data")

	req, err := http.NewRequestWithContext(ctx, "GET", "https://gtfs.adelaidemetro.com.au/v1/static/latest/google_transit.zip", nil)
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

	static, err := gtfs.ParseStatic(body, gtfs.ParseStaticOptions{InheritWheelchairBoarding: true})
	if err != nil {
		app.Logger.Error("Failed to parse static data", zap.Error(err))
		return err
	}
	app.Static = static

	app.Logger.Info("Fetched static data", zap.Int("stops", len(static.Stops)), zap.Int("routes", len(static.Routes)), zap.Int("agencies", len(static.Agencies)))

	return nil
}
