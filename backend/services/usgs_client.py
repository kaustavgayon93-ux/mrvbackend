import logging
from pystac_client import Client
from typing import List, Dict, Any
import os
import aiohttp
import aiofiles

logger = logging.getLogger(__name__)

class USGSLandsatClient:
    """
    USGS Landsat STAC Client.
    """

    def __init__(self):
        # Using Element84 Earth Search as the preferred stable STAC API for Landsat C2 L2
        self.stac_url = "https://earth-search.aws.element84.com/v1"

    async def search_landsat(self, bbox: List[float], start_date: str, end_date: str, max_cloud: float = 20.0) -> List[Dict[str, Any]]:
        """
        Search Landsat 8/9 Collection 2 Level-2 SR via STAC.
        """
        try:
            catalog = Client.open(self.stac_url)
            search = catalog.search(
                collections=["landsat-c2l2-sr"],
                bbox=bbox,
                datetime=f"{start_date}/{end_date}",
                query={"eo:cloud_cover": {"lt": max_cloud}}
            )
            items = list(search.items())
            logger.info(f"Found {len(items)} Landsat scenes.")
            return [item.to_dict() for item in items]
        except Exception as e:
            logger.error(f"Failed to search Landsat: {str(e)}")
            raise

    async def download_scene(self, scene_item: Dict[str, Any], output_dir: str) -> List[str]:
        """
        Download COG bands from S3/HTTPS.
        """
        os.makedirs(output_dir, exist_ok=True)
        downloaded_files = []

        try:
            # For public Earth Search assets, we can usually fetch directly without auth
            async with aiohttp.ClientSession() as session:
                for asset_key, asset in scene_item.get("assets", {}).items():
                    if "href" in asset:
                        url = asset["href"]
                        # Convert s3:// URLs to https if necessary, though Element84 usually provides https hrefs
                        if url.startswith("s3://"):
                            # This is a simplification. Real implementation might need boto3 for s3://
                            logger.warning(f"S3 protocol found, using direct request might fail if private: {url}")
                            
                        filename = os.path.basename(url.split("?")[0])
                        if not filename:
                            filename = f"{asset_key}.tif"
                            
                        file_path = os.path.join(output_dir, filename)
                        
                        logger.info(f"Downloading Landsat asset {asset_key} from {url}...")
                        async with session.get(url) as response:
                            response.raise_for_status()
                            async with aiofiles.open(file_path, "wb") as f:
                                async for chunk in response.content.iter_chunked(8192):
                                    await f.write(chunk)
                                    
                        downloaded_files.append(file_path)
            
            logger.info(f"Successfully downloaded {len(downloaded_files)} Landsat files to {output_dir}")
            return downloaded_files
        except Exception as e:
            logger.error(f"Failed to download Landsat scene: {str(e)}")
            raise
