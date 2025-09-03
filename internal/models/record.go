// Reusable application models
package models

import (
	"time"

	"go.mongodb.org/mongo-driver/v2/bson"
)

type VehicleType int

const (
	VehicleTypeTram      VehicleType = 0
	VehicleTypeSubway    VehicleType = 1
	VehicleTypeRail      VehicleType = 2
	VehicleTypeBus       VehicleType = 3
	VehicleTypeFerry     VehicleType = 4
	VehicleTypeCableTram VehicleType = 5
	VehicleTypeAerial    VehicleType = 6
	VehicleTypeFunicular VehicleType = 7
	VehicleTypeTrolley   VehicleType = 11
	VehicleTypeMonorail  VehicleType = 12
	VehicleTypeUnknown   VehicleType = 1000
)

// Represents a route a vehicle has taken
type Route struct {
	ID        string      `bson:"id" json:"id"`
	ShortName *string     `bson:"short_name,omitempty" json:"short_name,omitempty"`
	LongName  *string     `bson:"long_name,omitempty" json:"long_name,omitempty"`
	Type      VehicleType `bson:"type" json:"type"`
}

// Represents a trip taken by a vehicle
type Trip struct {
	ID        string `bson:"id" json:"id"`
	Direction uint64 `bson:"direction" json:"direction"`
	Route     Route  `bson:"route" json:"route"`
}

// Represents a vehicle
type Vehicle struct {
	ID    string      `bson:"id" json:"id"`
	Label *string     `bson:"label,omitempty" json:"label,omitempty"`
	Plate *string     `bson:"plate,omitempty" json:"plate,omitempty"`
	Type  VehicleType `bson:"type" json:"type"`
}

// Represents an agency that operates a vehicle
type Agency struct {
	ID       string `bson:"id" json:"id"`
	Name     string `bson:"name" json:"name"`
	URL      string `bson:"url" json:"url"`
	Timezone string `bson:"timezone" json:"timezone"`
}

// Represents a unique trip that a vehicle has taken
type Record struct {
	ID        bson.ObjectID `bson:"_id,omitempty" json:"id,omitempty"`
	Vehicle   Vehicle       `bson:"vehicle" json:"vehicle"`
	Trip      Trip          `bson:"trip" json:"trip"`
	Agency    Agency        `bson:"agency" json:"agency"`
	Timestamp time.Time     `bson:"timestamp" json:"timestamp"`
}
