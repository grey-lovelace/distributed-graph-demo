package main

import (
	"encoding/json"
	"net/http"

	"demo/rooms/store"
)

// registerRestRoutes serves the rooms as a REST API under /api/rooms.
func registerRestRoutes(mux *http.ServeMux, rooms *store.Store) {
	mux.HandleFunc("GET /api/rooms", func(w http.ResponseWriter, r *http.Request) {
		writeJSON(w, http.StatusOK, rooms.All())
	})

	mux.HandleFunc("GET /api/rooms/{id}", func(w http.ResponseWriter, r *http.Request) {
		id := r.PathValue("id")
		room := rooms.ByID(id)
		if room == nil {
			writeJSON(w, http.StatusNotFound, map[string]string{"error": "Room not found: " + id})
			return
		}
		writeJSON(w, http.StatusOK, room)
	})
}

func writeJSON(w http.ResponseWriter, status int, body any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(body)
}
