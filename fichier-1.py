import asyncio
import base64
import json
from pathlib import Path

class KlingClone:
    def __init__(self, model_name="kling-v3"):
        self.model_name = model_name
        self.api_base = "https://api.kling.ai/v1"
        self.session = None
        
    async def __aenter__(self):
        import aiohttp
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def generate(self, prompt, negative_prompt="", **kwargs):
        """Génère une vidéo Kling à partir d'un prompt"""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            **kwargs
        }
        async with self.session.post(
            f"{self.api_base}/generate",
            json=payload
        ) as resp:
            return await resp.json()
    
    async def poll_status(self, task_id, max_retries=30):
        """Poll le statut de génération"""
        for _ in range(max_retries):
            result = await self.generate_status(task_id)
            if result.get("status") == "completed":
                return result
            await asyncio.sleep(2)
        return {"status": "timeout"}
    
    async def generate_and_download(self, prompt, output_path="output.mp4"):
        """Pipeline complet : génération + téléchargement"""
        gen_result = await self.generate(prompt)
        task_id = gen_result.get("task_id") or gen_result.get("id")
        if not task_id:
            raise ValueError("No task ID returned")
            
        result = await self.poll_status(task_id)
        if result.get("status") != "completed":
            raise RuntimeError(f"Generation failed: {result}")
            
        # Téléchargement du fichier
        video_url = result.get("video_url") or result.get("output_url")
        if not video_url:
            raise ValueError("No video URL in result")
            
        import aiohttp
        async with self.session.get(video_url) as resp:
            data = await resp.read()
        Path(output_path).write_bytes(data)
        return output_path

async def main():
    async with KlingClone() as kl:
        output = await kl.generate_and_download(
            "Un homme marche dans la rue la nuit, style cinématique",
            "output_kling.mp4"
        )
        print(f"Vidéo sauvegardée : {output}")

if __name__ == "__main__":
    asyncio.run(main())