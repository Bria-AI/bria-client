/**
 * Submit an asynchronous job and poll until it reaches a terminal state.
 * Good for long-running endpoints (e.g. video).
 */
import { BriaClient } from "@bria-ai/client";

async function main(): Promise<void> {
  const client = new BriaClient();

  const submitted = await client.submit("video/segment/mask_by_prompt", {
    video:
      "https://bria-test-images.s3.us-east-1.amazonaws.com/videos/eraser_mask/woman_right_side.mov",
    prompt: "women",
  });
  console.log("submitted:", submitted.requestId);

  const result = await client.poll(submitted, { interval: 1, timeout: 300 });
  console.log(result);
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
