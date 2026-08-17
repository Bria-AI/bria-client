/**
 * Run many jobs concurrently. JavaScript is single-threaded and async, so the Python SDK's
 * thread/process pool examples become a simple `Promise.all` over async work — the event loop
 * keeps all the in-flight requests going at once.
 */
import { BriaClient, Image, type BriaResponse } from "@bria-ai/client";

const IMAGE = "https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png";

async function removeBackground(client: BriaClient): Promise<BriaResponse> {
  const submitted = await client.submit("image/edit/remove_background", {
    image: new Image(IMAGE).asBriaApiInput,
  });
  return client.poll(submitted);
}

async function main(): Promise<void> {
  const client = new BriaClient();

  // Fire several submit+poll chains at once.
  const results = await Promise.all(Array.from({ length: 3 }, () => removeBackground(client)));

  for (const res of results) {
    console.log(res.status, res.result);
  }
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
