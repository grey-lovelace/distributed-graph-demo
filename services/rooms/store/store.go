// Package store loads the rooms from data/rooms.json and keeps them in memory.
// The GraphQL resolvers and the REST handlers both read from it.
package store

import (
	"encoding/json"
	"os"
	"sort"

	"demo/rooms/graph/model"
)

type Store struct {
	rooms []*model.Room
}

func Load(path string) (*Store, error) {
	bytes, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	var rooms []*model.Room
	if err := json.Unmarshal(bytes, &rooms); err != nil {
		return nil, err
	}

	// Sort from the largest room to the smallest.
	sort.Slice(rooms, func(i, j int) bool { return rooms[i].Capacity > rooms[j].Capacity })

	return &Store{rooms: rooms}, nil
}

func (s *Store) All() []*model.Room {
	return s.rooms
}

// ByID returns nil when no room has the given ID.
func (s *Store) ByID(id string) *model.Room {
	for _, room := range s.rooms {
		if room.ID == id {
			return room
		}
	}
	return nil
}
