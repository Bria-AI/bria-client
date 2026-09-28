# Examples

Runnable examples for `@bria-ai/client`. They mirror the Python SDK's `examples/`.

## Running

Set `BRIA_API_TOKEN` and run with [tsx](https://github.com/privatenumber/tsx) (no build step):

```bash
export BRIA_API_TOKEN=your-token
npx tsx examples/success-request.ts
```

Or build the package first (`npm run build`) and run the compiled JS.

| File                 | Shows                                                                                      |
| -------------------- | ------------------------------------------------------------------------------------------ |
| `success-request.ts` | A simple synchronous `run()` call.                                                         |
| `failed-request.ts`  | Reading `response.error` and `raiseForStatus()`.                                           |
| `polling.ts`         | `submit()` then `poll()` for long jobs.                                                    |
| `concurrency.ts`     | Many jobs at once via `Promise.all` (the JS analog of the Python thread/process examples). |
| `custom-client.ts`   | Custom base URL, default headers, retry policy, per-call token override.                   |
| `webhook-handler.ts` | Verifying a signed webhook (dependency-free `node:http` server).                           |

> These examples import from `@bria-ai/client`. Inside this repo the package name resolves to
> `src/` for type-checking; when running with `tsx` outside the repo, install the published
> package first.
