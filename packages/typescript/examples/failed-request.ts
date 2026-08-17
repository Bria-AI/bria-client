/**
 * Error handling: a failing request returns a BriaResponse whose `error` is set. Calling
 * `raiseForStatus()` turns that into a thrown BriaException.
 */
import { BriaClient, BriaException } from "@bria-ai/client";

async function main(): Promise<void> {
  const client = new BriaClient();

  const response = await client.run("image/edit/remove_background", {
    image: "https://error.com/non-existing-image.png",
  });

  console.log("status:", response.status);
  console.log("error:", response.error);

  try {
    response.raiseForStatus();
  } catch (err) {
    if (err instanceof BriaException) {
      console.error(`BriaException ${err.code}: ${err.message} — ${err.details}`);
    } else {
      throw err;
    }
  }
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
