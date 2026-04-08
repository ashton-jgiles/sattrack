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

  Object.keys(groups).forEach((id) => {
    groups[id].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
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

// Release lookAt lock and reorient camera to face Earth so Cesium orbits it correctly.
function reorientTowardEarth(viewer) {
  if (!viewer || viewer.isDestroyed()) return;
  const cam = viewer.camera;
  cam.lookAtTransform(Cesium.Matrix4.IDENTITY);

  const camPos = cam.position.clone();
  const toEarth = Cesium.Cartesian3.normalize(
    Cesium.Cartesian3.negate(camPos, new Cesium.Cartesian3()),
    new Cesium.Cartesian3(),
  );
  // Build a stable up vector perpendicular to toEarth (use world Z, fall back to X near poles)
  const worldZ = new Cesium.Cartesian3(0, 0, 1);
  const refAxis = Math.abs(Cesium.Cartesian3.dot(toEarth, worldZ)) > 0.99
    ? new Cesium.Cartesian3(1, 0, 0)
    : worldZ;
  const right = Cesium.Cartesian3.normalize(
    Cesium.Cartesian3.cross(toEarth, refAxis, new Cesium.Cartesian3()),
    new Cesium.Cartesian3(),
  );
  const up = Cesium.Cartesian3.cross(right, toEarth, new Cesium.Cartesian3());

  cam.setView({ destination: camPos, orientation: { direction: toEarth, up } });
}

export default function SatelliteGlobe({
  highlightedSatellites = [],
  // When set, only satellites whose IDs are in this Set/array are shown.
  // When null/undefined, all satellites are shown.
  visibleSatelliteIds = null,
  onReady = null,
  tracking = false,
  onStopTracking = null,
}) {
  const cesiumContainer = useRef(null);
  const viewerRef = useRef(null);
  const pointCollectionRef = useRef(null);
  const pointsRef = useRef([]);
  const animRef = useRef(null);
  const startTimeRef = useRef(null);
  const satelliteGroupsRef = useRef({});
  const satelliteIdsRef = useRef([]);
  const pendingSatelliteIdsRef = useRef(new Set());
  const labelCollectionRef = useRef(null);
  const selectedLabelRef = useRef(null);
  const trackingRef = useRef(false);
  const trackingRangeRef = useRef(null); // null = use default on next frame
  const onStopTrackingRef = useRef(null);
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

    viewerRef.current = viewer;
    pointCollectionRef.current = viewer.scene.primitives.add(
      new Cesium.PointPrimitiveCollection(),
    );
    labelCollectionRef.current = viewer.scene.primitives.add(
      new Cesium.LabelCollection(),
    );
    selectedLabelRef.current = labelCollectionRef.current.add({
      show: false,
      text: "",
      font: "11px monospace",
      fillColor: Cesium.Color.fromCssColorString("#e2e8f0"),
      outlineColor: Cesium.Color.fromCssColorString("#020917"),
      outlineWidth: 4,
      style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      pixelOffset: new Cesium.Cartesian2(12, -8),
      horizontalOrigin: Cesium.HorizontalOrigin.LEFT,
      verticalOrigin: Cesium.VerticalOrigin.TOP,
      disableDepthTestDistance: Number.POSITIVE_INFINITY,
    });

    if (onReady) {
      onReady({
        resetCamera: () => {
          if (viewerRef.current && !viewerRef.current.isDestroyed()) {
            viewerRef.current.camera.flyHome(1.0);
          }
        },
      });
    }

    const ro = new ResizeObserver(() => {
      if (viewerRef.current && !viewerRef.current.isDestroyed()) {
        viewerRef.current.resize();
      }
    });
    ro.observe(cesiumContainer.current);

    const handleWheel = (e) => {
      if (!trackingRef.current || trackingRangeRef.current === null) return;
      e.preventDefault();
      // Normalize deltaY across deltaMode values to match Cesium's feel.
      // DOM_DELTA_PIXEL (0) ~100-120 per tick, LINE (1) ~3, PAGE (2) ~1.
      const normalized =
        e.deltaMode === 1 ? e.deltaY * 40 :
        e.deltaMode === 2 ? e.deltaY * 800 :
        e.deltaY;
      // ~10% range change per standard 120-unit tick, scaling with scroll speed.
      const fraction = (normalized / 120) * 0.1;
      trackingRangeRef.current = Math.max(500_000, trackingRangeRef.current * (1 + fraction));
    };
    cesiumContainer.current.addEventListener("wheel", handleWheel, { passive: false });

    // When the user drags while tracking, release tracking and reorient toward Earth
    let dragOrigin = null;
    const handlePointerDown = (e) => {
      if (!trackingRef.current) return;
      dragOrigin = { x: e.clientX, y: e.clientY };
    };
    const handlePointerMove = (e) => {
      if (!trackingRef.current || !dragOrigin) return;
      const dx = e.clientX - dragOrigin.x;
      const dy = e.clientY - dragOrigin.y;
      if (Math.sqrt(dx * dx + dy * dy) > 5) {
        dragOrigin = null;
        trackingRef.current = false;
        trackingRangeRef.current = null;
        reorientTowardEarth(viewer);
        onStopTrackingRef.current?.();
      }
    };
    const handlePointerUp = () => { dragOrigin = null; };
    cesiumContainer.current.addEventListener("pointerdown", handlePointerDown);
    cesiumContainer.current.addEventListener("pointermove", handlePointerMove);
    cesiumContainer.current.addEventListener("pointerup", handlePointerUp);

    return () => {
      ro.disconnect();
      cesiumContainer.current?.removeEventListener("wheel", handleWheel);
      cesiumContainer.current?.removeEventListener("pointerdown", handlePointerDown);
      cesiumContainer.current?.removeEventListener("pointermove", handlePointerMove);
      cesiumContainer.current?.removeEventListener("pointerup", handlePointerUp);
      cancelAnimationFrame(animRef.current);
      if (viewerRef.current && !viewerRef.current.isDestroyed()) {
        viewerRef.current.destroy();
        viewerRef.current = null;
      }
    };
  }, []);

  // Keep onStopTrackingRef current
  useEffect(() => { onStopTrackingRef.current = onStopTracking; }, [onStopTracking]);

  // Sync tracking prop → ref, and release camera when tracking is turned off
  useEffect(() => {
    trackingRef.current = tracking;
    if (!tracking && viewerRef.current && !viewerRef.current.isDestroyed()) {
      reorientTowardEarth(viewerRef.current);
      trackingRangeRef.current = null;
    }
  }, [tracking]);

  // Fetch positions and create one point per satellite
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
        const allPages = [first, ...remaining];
        const allPositions = allPages.flatMap((p) => p.results);
        const pendingSatelliteIds = new Set(
          allPages.flatMap((p) => p.pending_satellite_ids ?? []),
        );
        pendingSatelliteIdsRef.current = pendingSatelliteIds;
        const groups = groupBySatellite(allPositions);
        satelliteGroupsRef.current = groups;

        const collection = pointCollectionRef.current;
        if (!collection || collection.isDestroyed()) return;

        const satelliteList = Object.entries(groups);
        satelliteIdsRef.current = satelliteList.map(([id]) => id);

        const points = satelliteList.map(([satelliteId, positions]) => {
          const pos = positions[0];
          const id = parseInt(satelliteId);
          const isHighlighted = highlightedSatellites.includes(id);
          const isPending = pendingSatelliteIds.has(id);
          const isVisible =
            visibleSatelliteIds === null || visibleSatelliteIds.has(id);

          const baseColor = isHighlighted
            ? "#3b82f6"
            : isPending
              ? "#f59e0b"
              : "#22c55e";
          const outlineColor = isHighlighted
            ? "#60a5fa"
            : isPending
              ? "#fbbf24"
              : "#4ade80";

          return collection.add({
            position: Cesium.Cartesian3.fromDegrees(
              pos.longitude,
              pos.latitude,
              pos.altitude * 1000,
            ),
            color: Cesium.Color.fromCssColorString(baseColor).withAlpha(0.9),
            pixelSize: isHighlighted ? 14 : 6,
            outlineColor: isHighlighted
              ? Cesium.Color.WHITE.withAlpha(0.4)
              : Cesium.Color.fromCssColorString(outlineColor).withAlpha(0.4),
            outlineWidth: isHighlighted ? 2 : 3,
            show: isVisible,
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

  // Update visibility and colours when filters or highlights change
  useEffect(() => {
    const collection = pointCollectionRef.current;
    if (!collection || collection.isDestroyed()) return;

    const satelliteIds = satelliteIdsRef.current;
    pointsRef.current.forEach((point, index) => {
      const id = parseInt(satelliteIds[index]);
      const isHighlighted = highlightedSatellites.includes(id);
      const isVisible =
        visibleSatelliteIds === null || visibleSatelliteIds.has(id);

      const isPending = pendingSatelliteIdsRef.current.has(id);
      point.show = isVisible;
      point.color = isHighlighted
        ? Cesium.Color.fromCssColorString("#3b82f6").withAlpha(0.9)
        : isPending
          ? Cesium.Color.fromCssColorString("#f59e0b").withAlpha(0.9)
          : Cesium.Color.fromCssColorString("#22c55e").withAlpha(0.9);
      point.pixelSize = isHighlighted ? 14 : 6;
      point.outlineColor = isHighlighted
        ? Cesium.Color.WHITE.withAlpha(0.4)
        : isPending
          ? Cesium.Color.fromCssColorString("#fbbf24").withAlpha(0.4)
          : Cesium.Color.fromCssColorString("#4ade80").withAlpha(0.4);
      point.outlineWidth = isHighlighted ? 2 : 3;
    });
  }, [highlightedSatellites, visibleSatelliteIds]);

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
      const satelliteIds = satelliteIdsRef.current;
      const highlightedId = highlightedSatellites[0] ?? null;

      points.forEach((point, index) => {
        const positions = groups[index];
        if (!positions || !point) return;

        const posA = positions[frameIndex];
        const posB = positions[(frameIndex + 1) % TOTAL_FRAMES];
        if (!posA || !posB) return;

        const interpolated = interpolatePosition(posA, posB, t);
        point.position = interpolated;

        if (parseInt(satelliteIds[index]) === highlightedId) {
          const altKm = lerp(posA.altitude, posB.altitude, t);
          const velKms = lerp(posA.velocity, posB.velocity, t).toFixed(2);

          const label = selectedLabelRef.current;
          if (label) {
            label.position = interpolated;
            label.text = `ALT ${altKm.toFixed(0)} km\nVEL ${velKms} km/s`;
            label.show = true;
          }

          if (
            trackingRef.current &&
            viewerRef.current &&
            !viewerRef.current.isDestroyed()
          ) {
            // Seed range on first tracking frame; afterwards the wheel handler owns it.
            if (trackingRangeRef.current === null) {
              trackingRangeRef.current = Math.max(12_000_000, altKm * 1000 * 1.2);
            }
            viewerRef.current.camera.lookAt(
              interpolated,
              new Cesium.HeadingPitchRange(
                0,
                Cesium.Math.toRadians(-50),
                trackingRangeRef.current,
              ),
            );
          }
        }
      });

      if (highlightedId === null && selectedLabelRef.current) {
        selectedLabelRef.current.show = false;
      }

      animRef.current = requestAnimationFrame(animate);
    };

    animRef.current = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animRef.current);
  }, [highlightedSatellites]);

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
