from kling_clone import KlingClone

async def main():
    async with KlingClone() as kl:
        output = await kl.generate_and_download(
            "Votre prompt ici",
            "output.mp4"
        )

asyncio.run(main())