// react imports
import React, { useEffect, useRef, useState } from "react";

// cesium imports
import * as Cesium from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";

// api imports
import { getSatellitePositionsPage } from "../api/trajectoryService";

// styles
import styles from "../styles/SatelliteGlobe.module.css";

// set the cesium token
Cesium.Ion.defaultAccessToken = process.env.CESIUM_TOKEN;

// compute total frames and loop durations
const TOTAL_FRAMES = 288;
const LOOP_DURATION_MS = 200 * 1000;

// take the data returned from the satellite positions endpoint into satellite groups by id
function groupBySatellite(positions) {
  const groups = positions.reduce((acc, pos) => {
    if (!acc[pos.satellite_id]) acc[pos.satellite_id] = [];
    acc[pos.satellite_id].push(pos);
    return acc;
  }, {});

  // Sort each satellite's positions by timestamp ascending
  Object.keys(groups).forEach((id) => {
    groups[id].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    // Slice to first TOTAL_FRAMES for a clean loop
    groups[id] = groups[id].slice(0, TOTAL_FRAMES);
  });

  return groups;
}

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function lerpLongitude(a, b, t) {
  let diff = b - a;
  if (diff > 180) diff -= 360;
  if (diff < -180) diff += 360;
  return a + diff * t;
}

function interpolatePosition(posA, posB, t) {
  return Cesium.Cartesian3.fromDegrees(
    lerpLongitude(posA.longitude, posB.longitude, t),
    lerp(posA.latitude, posB.latitude, t),
    lerp(posA.altitude, posB.altitude, t) * 1000,
  );
}

export default function SatelliteGlobe({
  highlightedSatellites = [],
  onSatelliteSelect,
  selectedSatelliteId,
}) {
  const cesiumContainer = useRef(null);
  const viewerRef = useRef(null);
  const pointCollectionRef = useRef(null);
  const pointsRef = useRef([]);
  const animRef = useRef(null);
  const startTimeRef = useRef(null);
  const satelliteGroupsRef = useRef({});
  const satelliteIdsRef = useRef([]); // ordered list of satellite IDs matching pointsRef
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize Cesium viewer once
  useEffect(() => {
    if (!cesiumContainer.current || viewerRef.current) return;

    const viewer = new Cesium.Viewer(cesiumContainer.current, {
      timeline: false,
      animation: false,
      baseLayerPicker: false,
      navigationHelpButton: false,
      homeButton: false,
      sceneModePicker: false,
      geocoder: false,
      fullscreenButton: false,
      infoBox: false,
      selectionIndicator: false,
      creditContainer: document.createElement("div"),
      baseLayer: Cesium.ImageryLayer.fromProviderAsync(
        Cesium.TileMapServiceImageryProvider.fromUrl(
          Cesium.buildModuleUrl("Assets/Textures/NaturalEarthII"),
          {
            fileExtension: "jpg",
            maximumLevel: 5,
          },
        ),
      ),
    });

    // set the viewer reference
    viewerRef.current = viewer;
    pointCollectionRef.current = viewer.scene.primitives.add(
      new Cesium.PointPrimitiveCollection(),
    );

    // Click handler: find the nearest point within a pixel threshold
    const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
    handler.setInputAction((click) => {
      const points = pointsRef.current;
      const satelliteIds = satelliteIdsRef.current;
      if (!points.length || !satelliteIds.length) return;

      const scene = viewer.scene;
      const PICK_RADIUS = 8; // pixels
      let closestIndex = -1;
      let closestDist = Infinity;

      points.forEach((point, index) => {
        if (!point || !point.position) return;
        const screenPos = Cesium.SceneTransforms.worldToWindowCoordinates(
          scene,
          point.position,
        );
        if (!screenPos) return;
        const dx = screenPos.x - click.position.x;
        const dy = screenPos.y - click.position.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < PICK_RADIUS && dist < closestDist) {
          closestDist = dist;
          closestIndex = index;
        }
      });

      if (closestIndex >= 0 && onSatelliteSelect) {
        const satelliteId = parseInt(satelliteIds[closestIndex]);
        onSatelliteSelect(satelliteId);
      }
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

    // return the component
    return () => {
      handler.destroy();
      cancelAnimationFrame(animRef.current);
      if (viewerRef.current && !viewerRef.current.isDestroyed()) {
        viewerRef.current.destroy();
        viewerRef.current = null;
      }
    };
  }, []);

  // Fetch positions, sort, slice to TOTAL_FRAMES, create one point per satellite
  useEffect(() => {
    const fetchPositions = async () => {
      try {
        const first = await getSatellitePositionsPage(1);
        const remaining =
          first.total_pages > 1
            ? await Promise.all(
                Array.from({ length: first.total_pages - 1 }, (_, i) =>
                  getSatellitePositionsPage(i + 2),
                ),
              )
            : [];
        const allPositions = [first, ...remaining].flatMap((p) => p.results);
        const groups = groupBySatellite(allPositions);
        satelliteGroupsRef.current = groups;

        const collection = pointCollectionRef.current;
        if (!collection || collection.isDestroyed()) return;

        const satelliteList = Object.entries(groups);
        // Store the ordered satellite IDs for click lookup
        satelliteIdsRef.current = satelliteList.map(([id]) => id);

        const points = satelliteList.map(([satelliteId, positions]) => {
          const pos = positions[0];
          const isHighlighted = highlightedSatellites.includes(
            parseInt(satelliteId),
          );
          const isSelected = selectedSatelliteId === parseInt(satelliteId);
          return collection.add({
            position: Cesium.Cartesian3.fromDegrees(
              pos.longitude,
              pos.latitude,
              pos.altitude * 1000,
            ),
            color: isSelected
              ? Cesium.Color.fromCssColorString("#facc15").withAlpha(1.0)
              : isHighlighted
                ? Cesium.Color.fromCssColorString("#ff6b6b").withAlpha(0.9)
                : Cesium.Color.fromCssColorString("#22c55e").withAlpha(0.9),
            pixelSize: isSelected ? 12 : isHighlighted ? 10 : 6,
            outlineColor: isSelected
              ? Cesium.Color.fromCssColorString("#fde68a").withAlpha(0.6)
              : isHighlighted
                ? Cesium.Color.fromCssColorString("#ff8e8e").withAlpha(0.4)
                : Cesium.Color.fromCssColorString("#4ade80").withAlpha(0.4),
            outlineWidth: 3,
          });
        });

        pointsRef.current = points;
      } catch (err) {
        console.error("Failed to fetch satellite positions:", err);
        setError("Failed to load satellite positions");
      } finally {
        setLoading(false);
      }
    };

    fetchPositions();
  }, []);

  // Update point colors when highlighted or selected satellite changes
  useEffect(() => {
    const collection = pointCollectionRef.current;
    if (!collection || collection.isDestroyed()) return;

    const satelliteIds = satelliteIdsRef.current;
    pointsRef.current.forEach((point, index) => {
      const satelliteId = parseInt(satelliteIds[index]);
      const isHighlighted = highlightedSatellites.includes(satelliteId);
      const isSelected = selectedSatelliteId === satelliteId;

      point.color = isSelected
        ? Cesium.Color.fromCssColorString("#facc15").withAlpha(1.0)
        : isHighlighted
          ? Cesium.Color.fromCssColorString("#ff6b6b").withAlpha(0.9)
          : Cesium.Color.fromCssColorString("#22c55e").withAlpha(0.9);
      point.pixelSize = isSelected ? 12 : isHighlighted ? 10 : 6;
      point.outlineColor = isSelected
        ? Cesium.Color.fromCssColorString("#fde68a").withAlpha(0.6)
        : isHighlighted
          ? Cesium.Color.fromCssColorString("#ff8e8e").withAlpha(0.4)
          : Cesium.Color.fromCssColorString("#4ade80").withAlpha(0.4);
    });
  }, [highlightedSatellites, selectedSatelliteId]);

  // Animation loop
  useEffect(() => {
    const animate = (timestamp) => {
      if (!startTimeRef.current) startTimeRef.current = timestamp;

      const elapsed = (timestamp - startTimeRef.current) % LOOP_DURATION_MS;
      const continuousFrame = (elapsed / LOOP_DURATION_MS) * TOTAL_FRAMES;
      const frameIndex = Math.floor(continuousFrame) % TOTAL_FRAMES;
      const t = continuousFrame - Math.floor(continuousFrame);

      const points = pointsRef.current;
      const groups = Object.values(satelliteGroupsRef.current);

      points.forEach((point, index) => {
        const positions = groups[index];
        if (!positions || !point) return;

        const posA = positions[frameIndex];
        const posB = positions[(frameIndex + 1) % TOTAL_FRAMES];
        if (!posA || !posB) return;

        point.position = interpolatePosition(posA, posB, t);
      });

      animRef.current = requestAnimationFrame(animate);
    };

    animRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animRef.current);
  }, []);

  // return the component
  return (
    <div className={styles.globeWrapper}>
      {loading && (
        <div className={styles.overlay}>
          <span className={styles.overlayText}>
            Loading satellite positions...
          </span>
        </div>
      )}
      {error && (
        <div className={styles.overlay}>
          <span className={styles.overlayError}>{error}</span>
        </div>
      )}
      <div ref={cesiumContainer} className={styles.viewer} />
    </div>
  );
}
