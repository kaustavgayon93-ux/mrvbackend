import logging
import httpx
from pystac_client import Client
from typing import List, Dict, Any, Optional
import os
import aiofiles

logger = logging.getLogger(__name__)

class CopernicusClient:
    """
    Copernicus Data Space Ecosystem client.
    """

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.username = username or os.environ.get("CDSE_USERNAME")
        self.password = password or os.environ.get("CDSE_PASSWORD")
        self.token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        self.stac_url = "https://catalogue.dataspace.copernicus.eu/stac"
        self.access_token = None

    async def authenticate(self) -> str:
        """
        Gets OAuth2 JWT token from CDSE Keycloak endpoint.
        """
        if not self.username or not self.password:
            raise ValueError("CDSE credentials not provided.")

        data = {
            "client_id": "cdse-public",
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.token_url, data=data)
                response.raise_for_status()
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                logger.info("Successfully authenticated with CDSE.")
                return self.access_token
        except httpx.HTTPError as e:
            logger.error(f"CDSE authentication failed: {str(e)}")
            raise

    async def search_sentinel2(self, bbox: List[float], start_date: str, end_date: str, max_cloud: float = 15.0) -> List[Dict[str, Any]]:
        """
        Search Sentinel-2 L2A scenes via STAC API.
        """
        try:
            catalog = Client.open(self.stac_url)
            search = catalog.search(
                collections=["SENTINEL-2"],
                bbox=bbox,
                datetime=f"{start_date}/{end_date}",
                query={"eo:cloud_cover": {"lt": max_cloud}}
            )
            items = list(search.items())
            logger.info(f"Found {len(items)} Sentinel-2 scenes.")
            return [item.to_dict() for item in items]
        except Exception as e:
            logger.error(f"Failed to search Sentinel-2: {str(e)}")
            raise

    async def search_sentinel1(self, bbox: List[float], start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Search Sentinel-1 GRD scenes.
        """
        try:
            catalog = Client.open(self.stac_url)
            search = catalog.search(
                collections=["SENTINEL-1"],
                bbox=bbox,
                datetime=f"{start_date}/{end_date}",
                # Additional filters could be applied for GRD
            )
            items = list(search.items())
            logger.info(f"Found {len(items)} Sentinel-1 scenes.")
            return [item.to_dict() for item in items]
        except Exception as e:
            logger.error(f"Failed to search Sentinel-1: {str(e)}")
            raise

    async def download_scene(self, scene_item: Dict[str, Any], output_dir: str) -> List[str]:
        """
        Download scene assets using OData API with auth token.
        """
        if not self.access_token:
            await self.authenticate()

        os.makedirs(output_dir, exist_ok=True)
        downloaded_files = []

        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            async with httpx.AsyncClient(headers=headers, timeout=60.0) as client:
                for asset_key, asset in scene_item.get("assets", {}).items():
                    if "href" in asset:
                        url = asset["href"]
                        # Simplify filename from URL
                        filename = os.path.basename(url.split("?")[0])
                        if not filename:
                            filename = f"{asset_key}.bin"
                            
                        file_path = os.path.join(output_dir, filename)
                        
                        logger.info(f"Downloading asset {asset_key} from {url}...")
                        async with client.stream("GET", url) as response:
                            response.raise_for_status()
                            async with aiofiles.open(file_path, "wb") as f:
                                async for chunk in response.aiter_bytes():
                                    await f.write(chunk)
                        
                        downloaded_files.append(file_path)
            
            logger.info(f"Successfully downloaded {len(downloaded_files)} files to {output_dir}")
            return downloaded_files
        except Exception as e:
            logger.error(f"Failed to download scene: {str(e)}")
            raise
