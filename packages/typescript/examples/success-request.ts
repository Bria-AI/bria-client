/**
 * Simplest possible call: run a synchronous job and print the result.
 * Requires BRIA_API_TOKEN in the environment.
 */
import { BriaClient, Image } from "@bria-ai/client";

async function main(): Promise<void> {
  const client = new BriaClient();

  const response = await client.run("image/edit/remove_background", {
    image: new Image("https://bria-test-images.s3.us-east-1.amazonaws.com/sun-example.png")
      .asBriaApiInput,
  });

  console.log(response);
  console.log("result:", response.result);
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
