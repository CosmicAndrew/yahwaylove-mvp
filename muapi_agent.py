"""
YAHWAYLOVE Muapi.ai Agent — AI Media Production Client
Extracted from Open-Generative-AI source code (Anil-matcha/Open-Generative-AI)

Production Key: YAHWAYLOVE (needs credits top-up)
Test Key: YAHWAYLOVE test (active, verified working)

Usage:
  from muapi_agent import MuapiAgent
  agent = MuapiAgent(use_test_key=True)
  result = await agent.generate_image("golden cross, faith, cinematic")
  print(result['url'])
"""

import asyncio
import aiohttp
import json
import os

PROD_KEY  = "5c86ad03e74e34ee83690c7dea1832e52c4a81bc3c7899a0a5f3b5e5fef079fd"
TEST_KEY  = "4fa4760aef46bea91bad8a758c2a7764872f58674adb9ad7013b8cea87853709"
BASE_URL  = "https://api.muapi.ai"

# ─── Model Endpoints ──────────────────────────────────────────────────────────
MODELS = {
    # Text-to-Image
    "nano-banana-2":   "nano-banana-2",       # Google Gemini, free, 4K
    "flux-dev":        "flux-dev",             # High quality
    "ideogram-v3":     "ideogram-v3",          # Text-in-image
    "seedream-5":      "seedream-5.0",         # ByteDance 4K
    "midjourney-v7":   "midjourney-v7",

    # Text-to-Video
    "kling-v3":        "kling-v3",             # Best quality video
    "sora-2":          "sora-2",               # OpenAI
    "veo-3":           "veo-3",                # Google
    "seedance-2":      "seedance-2.0",         # ByteDance 9:16 social
    "wan-2.6":         "wan-2.6",

    # Lip Sync (Image + Audio → Video)
    "infinite-talk":   "infinitetalk-image-to-video",
    "ltx-lipsync":     "ltx-2.3-lipsync",
    "wan-speech":      "wan2.2-speech-to-video",

    # Video Lip Sync
    "sync-lipsync":    "sync-lipsync",

    # Cinema Studio
    "seedance-cinema": "seedance-2.0",         # with camera prompt modifiers
}

# Camera prompt modifiers for Cinema Studio
CAMERAS = {
    "modular_8k":   "shot on Modular 8K Digital camera",
    "full_frame":   "shot on Full-Frame Cine Digital",
    "70mm_film":    "shot on Grand Format 70mm Film",
    "cinema_16mm":  "shot on Classic 16mm Film",
}
LENSES = {
    "portrait_85mm": "85mm portrait lens",
    "wide_24mm":     "24mm wide lens",
    "human_35mm":    "35mm human eye lens",
    "anamorphic":    "Classic Anamorphic lens",
}


class MuapiAgent:
    """YAHWAYLOVE AI Media Production Agent — wraps Muapi.ai API"""

    def __init__(self, use_test_key: bool = False):
        self.key = TEST_KEY if use_test_key else PROD_KEY
        self.base = BASE_URL

    # ── Core Poll Loop ────────────────────────────────────────────────────────
    async def _poll(self, request_id: str, max_attempts: int = 60, interval: float = 3.0) -> dict:
        url = f"{self.base}/api/v1/predictions/{request_id}/result"
        async with aiohttp.ClientSession() as session:
            for attempt in range(1, max_attempts + 1):
                await asyncio.sleep(interval)
                async with session.get(url, headers={"x-api-key": self.key}) as r:
                    data = await r.json()
                    status = data.get("status", "").lower()
                    print(f"  Poll {attempt}/{max_attempts} — {status}")
                    if status in ("completed", "succeeded", "success"):
                        url_out = (data.get("outputs") or [None])[0] or data.get("url")
                        return {"status": "completed", "url": url_out, "raw": data}
                    if status in ("failed", "error"):
                        raise RuntimeError(f"Generation failed: {data.get('error', 'unknown')}")
        raise TimeoutError("Muapi generation timed out")

    async def _submit_and_poll(self, endpoint: str, payload: dict) -> dict:
        url = f"{self.base}/api/v1/{endpoint}"
        headers = {"Content-Type": "application/json", "x-api-key": self.key}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as r:
                if not r.ok:
                    text = await r.text()
                    raise RuntimeError(f"API error {r.status}: {text[:200]}")
                data = await r.json()
        print(f"  Submitted to {endpoint} — request_id: {data.get('request_id', data.get('id'))}")
        request_id = data.get("request_id") or data.get("id")
        if not request_id:
            return data  # direct result
        return await self._poll(request_id)

    # ── Public Methods ────────────────────────────────────────────────────────

    async def generate_image(
        self,
        prompt: str,
        model: str = "nano-banana-2",
        aspect_ratio: str = "16:9",
        resolution: str = "1k"
    ) -> dict:
        """Text-to-image generation. Best free model: nano-banana-2"""
        endpoint = MODELS.get(model, model)
        payload = {"prompt": prompt, "aspect_ratio": aspect_ratio, "resolution": resolution}
        return await self._submit_and_poll(endpoint, payload)

    async def generate_video(
        self,
        prompt: str,
        model: str = "seedance-2",
        aspect_ratio: str = "9:16",
        duration: int = 5,
        quality: str = "high"
    ) -> dict:
        """Text-to-video generation. Best for social: seedance-2 (9:16)"""
        endpoint = MODELS.get(model, model)
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "duration": duration,
            "quality": quality,
        }
        return await self._submit_and_poll(endpoint, payload)

    async def image_to_video(
        self,
        image_url: str,
        prompt: str = "",
        model: str = "seedance-2",
        aspect_ratio: str = "9:16",
        duration: int = 5,
    ) -> dict:
        """Animate a still image into video. Great for church photos."""
        endpoint = MODELS.get(model, model)
        payload = {"image_url": image_url, "prompt": prompt,
                   "aspect_ratio": aspect_ratio, "duration": duration}
        return await self._submit_and_poll(endpoint, payload)

    async def lip_sync(
        self,
        image_url: str,
        audio_url: str,
        model: str = "ltx-lipsync",
        resolution: str = "720p"
    ) -> dict:
        """Portrait image + audio → talking video. Perfect for pastor content."""
        endpoint = MODELS.get(model, model)
        payload = {"image_url": image_url, "audio_url": audio_url, "resolution": resolution}
        return await self._submit_and_poll(endpoint, payload)

    async def cinema_shot(
        self,
        prompt: str,
        camera: str = "full_frame",
        lens: str = "portrait_85mm",
        aspect_ratio: str = "16:9",
        duration: int = 5,
    ) -> dict:
        """Cinematic shot with professional camera controls."""
        cam_mod = CAMERAS.get(camera, "")
        lens_mod = LENSES.get(lens, "")
        full_prompt = f"{prompt}, {cam_mod}, {lens_mod}, cinematic, photorealistic"
        return await self.generate_video(full_prompt, model="kling-v3",
                                         aspect_ratio=aspect_ratio, duration=duration)

    async def faith_post_image(self, scripture: str, theme: str = "church") -> dict:
        """Generate a social media image for a faith post. Used by CONTENT agent."""
        prompt = (
            f"Professional faith-based social media graphic, {theme} setting, "
            f"scripture overlay style, deep navy (#0a0f2e) and gold (#c9a227) color palette, "
            f"cinematic lighting, modern Christian aesthetic, 'Kingdom of God' energy, "
            f"photorealistic. Theme: {scripture}"
        )
        return await self.generate_image(prompt, model="nano-banana-2",
                                         aspect_ratio="4:5", resolution="2k")

    async def upload_file(self, file_path: str) -> str:
        """Upload local file to Muapi CDN. Returns hosted URL."""
        url = f"{self.base}/api/v1/upload_file"
        async with aiohttp.ClientSession() as session:
            with open(file_path, "rb") as f:
                data = aiohttp.FormData()
                data.add_field("file", f, filename=os.path.basename(file_path))
                async with session.post(url, headers={"x-api-key": self.key}, data=data) as r:
                    result = await r.json()
                    return result.get("url") or result.get("file_url")


# ── Quick-test runner ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    async def test():
        agent = MuapiAgent(use_test_key=True)  # use test key first
        print("Testing YAHWAYLOVE faith post image generation...")
        result = await agent.faith_post_image(
            scripture="John 3:16 — For God so loved the world",
            theme="church sanctuary"
        )
        print(f"Result: {result}")

    asyncio.run(test())
