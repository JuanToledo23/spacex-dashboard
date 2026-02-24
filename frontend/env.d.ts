/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<Record<string, unknown>, Record<string, unknown>, unknown>
  export default component
}

declare module 'topojson-client' {
  import type { Topology, Objects } from 'topojson-specification'
  export function feature<G extends GeoJSON.GeoJsonProperties>(
    // eslint-disable-next-line no-unused-vars
    topology: Topology<Objects<G>>,
    // eslint-disable-next-line no-unused-vars
    object: string | { type: string; geometries: unknown[] }
  ): GeoJSON.FeatureCollection<GeoJSON.Geometry, G>
}
