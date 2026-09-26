"use client";

import React from "react";
import Map, { NavigationControl, ScaleControl, Source, Layer, FillLayer, LineLayer } from "react-map-gl";
import maplibregl from "maplibre-gl";

interface MapViewProps {
  center?: { lat: number; lng: number };
  zoom?: number;
  boundaries?: any; // GeoJSON FeatureCollection or Feature
  markers?: any[];
  onBoundsChange?: (bounds: any) => void;
}

export function MapView({ 
  center = { lat: 26.2, lng: 92.9 }, 
  zoom = 7, 
  boundaries,
  markers,
  onBoundsChange 
}: MapViewProps) {

  const boundaryFillLayer: FillLayer = {
    id: "boundary-fill",
    type: "fill",
    paint: {
      "fill-color": "#588157",
      "fill-opacity": 0.2,
    },
  };

  const boundaryLineLayer: LineLayer = {
    id: "boundary-line",
    type: "line",
    paint: {
      "line-color": "#344e41",
      "line-width": 2,
    },
  };

  return (
    <div className="w-full h-full relative">
      <Map
        initialViewState={{
          longitude: center.lng,
          latitude: center.lat,
          zoom: zoom,
        }}
        mapStyle={{
          version: 8,
          sources: {
            "osm-tiles": {
              type: "raster",
              tiles: [
                "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
              ],
              tileSize: 256,
              attribution: "&copy; OpenStreetMap Contributors",
            },
          },
          layers: [
            {
              id: "osm-tiles-layer",
              type: "raster",
              source: "osm-tiles",
              minzoom: 0,
              maxzoom: 19,
            },
          ],
        }}
        onMoveEnd={(e) => {
          if (onBoundsChange) {
            onBoundsChange(e.viewState);
          }
        }}
      >
        <NavigationControl position="top-right" />
        <ScaleControl />

        {boundaries && (
          <Source id="project-boundary" type="geojson" data={boundaries}>
            <Layer {...boundaryFillLayer} />
            <Layer {...boundaryLineLayer} />
          </Source>
        )}
      </Map>
    </div>
  );
}
