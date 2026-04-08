// react imports
import React, { useEffect, useRef, useState } from "react";

// cesium imports
import * as Cesium from "cesium";
import "cesium/Build/Cesium/Widgets/widgets.css";

// api imports
import { getSatellitePositionsPage } from "../api/satelliteService";
import { getSatelliteCategoryColor } from "../constants/satelliteColors";

// styles
import styles from "../styles/SatelliteGlobe.module.css";

// set the cesium token
Cesium.Ion.defaultAccessToken = process.env.CESIUM_TOKEN;

// compute total frames and loop durations
const TOTAL_FRAMES = 288;
const LOOP_DURATION_MS = 200 * 1000;
const FLY_IN_DURATION_S = 1.2;
const FLY_IN_DURATION_MS = FLY_IN_DURATION_S * 1000;

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

// Release lookAt lock and smoothly fly camera to an Earth-facing orientation.
function releaseToEarth(viewer) {
  if (!viewer || viewer.isDestroyed()) return;
  const cam = viewer.camera;
  cam.lookAtTransform(Cesium.Matrix4.IDENTITY);

  const camPos = cam.position.clone();
  const toEarth = Cesium.Cartesian3.normalize(
    Cesium.Cartesian3.negate(camPos, new Cesium.Cartesian3()),
    new Cesium.Cartesian3(),
  );
  // Stable up vector perpendicular to toEarth
  const worldZ = new Cesium.Cartesian3(0, 0, 1);
  const refAxis =
    Math.abs(Cesium.Cartesian3.dot(toEarth, worldZ)) > 0.99
      ? new Cesium.Cartesian3(1, 0, 0)
      : worldZ;
  const right = Cesium.Cartesian3.normalize(
    Cesium.Cartesian3.cross(toEarth, refAxis, new Cesium.Cartesian3()),
    new Cesium.Cartesian3(),
  );
  const up = Cesium.Cartesian3.cross(right, toEarth, new Cesium.Cartesian3());

  cam.flyTo({
    destination: camPos,
    orientation: { direction: toEarth, up },
    duration: 1.2,
    easingFunction: Cesium.EasingFunction.CUBIC_IN_OUT,
  });
}

export default function SatelliteGlobe({
  highlightedSatellites = [],
  // When set, only satellites whose IDs are in this Set/array are shown.
  // When null/undefined, all satellites are shown.
  visibleSatelliteIds = null,
  satelliteTypeById = {},
  onReady = null,
  tracking = false,
}) {
  const cesiumContainer = useRef(null);
  const viewerRef = useRef(null);
  const pointCollectionRef = useRef(null);
  const pointsRef = useRef([]);
  const animRef = useRef(null);
  const startTimeRef = useRef(null);
  const satelliteGroupsRef = useRef({});
  const satelliteIdsRef = useRef([]);
  const satelliteTypeByIdRef = useRef({});
  const pendingSatelliteIdsRef = useRef(new Set());
  const labelCollectionRef = useRef(null);
  const selectedLabelRef = useRef(null);
  const trackingRef = useRef(false);
  const trackingRangeRef = useRef(null); // null = use default on next frame
  const flyingInRef = useRef(false); // true while the fly-in animation plays
  const currentSatPosRef = useRef(null); // live ECEF position of highlighted satellite
  const currentSatAltRef = useRef(0); // live altitude (km) of highlighted satellite

  const getSatelliteColorPalette = (
    satelliteId,
    isHighlighted,
    fallbackType = "",
  ) => {
    if (isHighlighted) {
      return {
        baseColor: "#3b82f6",
      };
    }

    const rawType =
      satelliteTypeById[String(satelliteId)] ??
      satelliteTypeByIdRef.current[String(satelliteId)] ??
      fallbackType;
    const typeColor = getSatelliteCategoryColor(rawType);

    return {
      baseColor: typeColor,
    };
  };

  const getSatelliteSampleAtTimestamp = (satelliteId, timestampMs) => {
    if (satelliteId === null || satelliteId === undefined) return null;

    const positions = satelliteGroupsRef.current[String(satelliteId)];
    if (!positions || positions.length === 0) return null;

    if (positions.length === 1 || !startTimeRef.current) {
      const only = positions[0];
      return {
        position: Cesium.Cartesian3.fromDegrees(
          only.longitude,
          only.latitude,
          only.altitude * 1000,
        ),
        altKm: only.altitude,
      };
    }

    const frameCount = positions.length;
    const elapsed = (timestampMs - startTimeRef.current) % LOOP_DURATION_MS;
    const continuousFrame = (elapsed / LOOP_DURATION_MS) * frameCount;
    const frameIndex = Math.floor(continuousFrame) % frameCount;
    const t = continuousFrame - Math.floor(continuousFrame);

    const posA = positions[frameIndex];
    const posB = positions[(frameIndex + 1) % frameCount];
    if (!posA || !posB) return null;

    return {
      position: interpolatePosition(posA, posB, t),
      altKm: lerp(posA.altitude, posB.altitude, t),
    };
  };

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
        e.deltaMode === 1
          ? e.deltaY * 40
          : e.deltaMode === 2
            ? e.deltaY * 800
            : e.deltaY;
      // ~10% range change per standard 120-unit tick, scaling with scroll speed.
      const fraction = (normalized / 120) * 0.1;
      trackingRangeRef.current = Math.max(
        500_000,
        trackingRangeRef.current * (1 + fraction),
      );
    };
    cesiumContainer.current.addEventListener("wheel", handleWheel, {
      passive: false,
    });

    return () => {
      ro.disconnect();
      cesiumContainer.current?.removeEventListener("wheel", handleWheel);
      cancelAnimationFrame(animRef.current);
      if (viewerRef.current && !viewerRef.current.isDestroyed()) {
        viewerRef.current.destroy();
        viewerRef.current = null;
      }
    };
  }, []);

  // Sync tracking prop → ref; disable/enable camera controls; smooth release
  useEffect(() => {
    trackingRef.current = tracking;
    const viewer = viewerRef.current;
    if (!viewer || viewer.isDestroyed()) return;
    const ctrl = viewer.scene.screenSpaceCameraController;
    if (tracking) {
      // Lock out all drag interactions; scroll is handled by our own wheel listener
      viewer.camera.cancelFlight();
      ctrl.enableRotate = false;
      ctrl.enableTranslate = false;
      ctrl.enableTilt = false;
      ctrl.enableZoom = false;

      // Fly in to the satellite if we already have its live position
      const satPos = currentSatPosRef.current;
      const altKm = currentSatAltRef.current;
      if (satPos) {
        const highlightedId = highlightedSatellites[0] ?? null;
        const predictedSample = getSatelliteSampleAtTimestamp(
          highlightedId,
          performance.now() + FLY_IN_DURATION_MS,
        );
        const targetSatPos = predictedSample?.position ?? satPos;
        const targetAltKm = predictedSample?.altKm ?? altKm;

        const heading = 0;
        const pitch = Cesium.Math.toRadians(-50);
        const range = Math.max(12_000_000, targetAltKm * 1000 * 1.2);
        trackingRangeRef.current = range;

        const cosP = Math.cos(pitch);
        const enuOffset = new Cesium.Cartesian3(
          -Math.sin(heading) * cosP * range,
          -Math.cos(heading) * cosP * range,
          -Math.sin(pitch) * range,
        );
        const enuToEcef =
          Cesium.Transforms.eastNorthUpToFixedFrame(targetSatPos);
        const ecefOffset = Cesium.Matrix4.multiplyByPointAsVector(
          enuToEcef,
          enuOffset,
          new Cesium.Cartesian3(),
        );
        const cameraPos = Cesium.Cartesian3.add(
          targetSatPos,
          ecefOffset,
          new Cesium.Cartesian3(),
        );

        const dir = Cesium.Cartesian3.normalize(
          Cesium.Cartesian3.subtract(
            targetSatPos,
            cameraPos,
            new Cesium.Cartesian3(),
          ),
          new Cesium.Cartesian3(),
        );
        const radial = Cesium.Cartesian3.normalize(
          cameraPos,
          new Cesium.Cartesian3(),
        );
        const right = Cesium.Cartesian3.normalize(
          Cesium.Cartesian3.cross(dir, radial, new Cesium.Cartesian3()),
          new Cesium.Cartesian3(),
        );
        const up = Cesium.Cartesian3.cross(right, dir, new Cesium.Cartesian3());

        flyingInRef.current = true;
        viewer.camera.flyTo({
          destination: cameraPos,
          orientation: { direction: dir, up },
          duration: FLY_IN_DURATION_S,
          easingFunction: Cesium.EasingFunction.CUBIC_IN_OUT,
          complete: () => {
            flyingInRef.current = false;
            if (
              trackingRef.current &&
              viewerRef.current &&
              !viewerRef.current.isDestroyed() &&
              currentSatPosRef.current
            ) {
              viewerRef.current.camera.lookAt(
                currentSatPosRef.current,
                new Cesium.HeadingPitchRange(
                  0,
                  Cesium.Math.toRadians(-50),
                  trackingRangeRef.current ?? range,
                ),
              );
            }
          },
          cancel: () => {
            flyingInRef.current = false;
          },
        });
      }
    } else {
      // Restore controls and smoothly fly back to an Earth-facing view
      flyingInRef.current = false;
      ctrl.enableRotate = true;
      ctrl.enableTranslate = true;
      ctrl.enableTilt = true;
      ctrl.enableZoom = true;
      trackingRangeRef.current = null;
      releaseToEarth(viewer);
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
          const isVisible =
            visibleSatelliteIds === null || visibleSatelliteIds.has(id);
          const inferredType = pos?.satellite_type ?? "";
          if (inferredType) {
            satelliteTypeByIdRef.current[String(satelliteId)] = inferredType;
          }
          const { baseColor } = getSatelliteColorPalette(
            satelliteId,
            isHighlighted,
            inferredType,
          );

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
              : Cesium.Color.fromCssColorString(baseColor).withAlpha(0.45),
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
    satelliteTypeByIdRef.current = {
      ...satelliteTypeByIdRef.current,
      ...satelliteTypeById,
    };

    const collection = pointCollectionRef.current;
    if (!collection || collection.isDestroyed()) return;

    const satelliteIds = satelliteIdsRef.current;
    pointsRef.current.forEach((point, index) => {
      const id = parseInt(satelliteIds[index]);
      const isHighlighted = highlightedSatellites.includes(id);
      const isVisible =
        visibleSatelliteIds === null || visibleSatelliteIds.has(id);

      const inferredType =
        satelliteGroupsRef.current[String(id)]?.[0]?.satellite_type ?? "";
      const { baseColor } = getSatelliteColorPalette(
        id,
        isHighlighted,
        inferredType,
      );
      point.show = isVisible;
      point.color = Cesium.Color.fromCssColorString(baseColor).withAlpha(0.9);
      point.pixelSize = isHighlighted ? 14 : 6;
      point.outlineColor = isHighlighted
        ? Cesium.Color.WHITE.withAlpha(0.4)
        : Cesium.Color.fromCssColorString(baseColor).withAlpha(0.45);
      point.outlineWidth = isHighlighted ? 2 : 3;
    });
  }, [highlightedSatellites, visibleSatelliteIds, satelliteTypeById]);

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

          // Keep live position/altitude available for the fly-in on tracking start
          currentSatPosRef.current = interpolated;
          currentSatAltRef.current = altKm;

          const label = selectedLabelRef.current;
          if (label) {
            label.position = interpolated;
            label.text = `ALT ${altKm.toFixed(0)} km\nVEL ${velKms} km/s`;
            label.show = true;
          }

          if (
            trackingRef.current &&
            !flyingInRef.current &&
            viewerRef.current &&
            !viewerRef.current.isDestroyed()
          ) {
            // Seed range on first tracking frame; afterwards the wheel handler owns it.
            if (trackingRangeRef.current === null) {
              trackingRangeRef.current = Math.max(
                12_000_000,
                altKm * 1000 * 1.2,
              );
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
