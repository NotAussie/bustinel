package models

import "time"
import "go.mongodb.org/mongo-driver/bson/primitive"

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

type Trip struct {
	ID        string `bson:"id" json:"id"`
	Direction int    `bson:"direction" json:"direction"`
	Route     string `bson:"route" json:"route"`
}

type Vehicle struct {
	ID    string      `bson:"id" json:"id"`
	Label *string     `bson:"label,omitempty" json:"label,omitempty"`
	Plate *string     `bson:"plate,omitempty" json:"plate,omitempty"`
	Type  VehicleType `bson:"type" json:"type"`
}

type Agency struct {
	ID   string `bson:"id" json:"id"`
	Name string `bson:"name" json:"name"`
	URL  string `bson:"url" json:"url"`
}

type Record struct {
	ID        primitive.ObjectID `bson:"_id,omitempty" json:"id,omitempty"`
	Vehicle   Vehicle            `bson:"vehicle" json:"vehicle"`
	Trip      Trip               `bson:"trip" json:"trip"`
	Agency    Agency             `bson:"agency" json:"agency"`
	Timestamp time.Time          `bson:"timestamp" json:"timestamp"`
}
