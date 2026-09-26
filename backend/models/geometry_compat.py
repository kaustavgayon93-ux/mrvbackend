"""
Geometry type compatibility layer.
Uses GeoAlchemy2 Geometry when PostGIS is available,
falls back to Text (storing GeoJSON strings) for SQLite local dev.
"""
from sqlalchemy import Text

try:
    from geoalchemy2 import Geometry as _PGGeometry
    HAS_GEOALCHEMY2 = True
except ImportError:
    HAS_GEOALCHEMY2 = False


def GeometryColumn(geometry_type: str = "GEOMETRY", srid: int = 4326, **kwargs):
    """
    Returns a Geometry column type compatible with the current database backend.

    For PostgreSQL+PostGIS: returns GeoAlchemy2 Geometry type with spatial index.
    For SQLite (local dev): returns Text type (stores GeoJSON as string).

    Args:
        geometry_type: The geometry type (e.g., 'POINT', 'MULTIPOLYGON', 'POLYGON')
        srid: Spatial Reference System Identifier (default: 4326 = WGS84)
    """
    if HAS_GEOALCHEMY2:
        return _PGGeometry(geometry_type, srid=srid, spatial_index=True)
    else:
        # Fallback: store as GeoJSON text in SQLite
        return Text()
