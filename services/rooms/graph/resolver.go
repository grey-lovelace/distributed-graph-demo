package graph

import "demo/rooms/store"

// This file will not be regenerated automatically.
//
// Resolver gives every resolver access to the room data.
type Resolver struct {
	Store *store.Store
}
