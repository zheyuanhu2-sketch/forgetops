# Third-party notices

ForgetOps is licensed under Apache-2.0. The project uses the following third-party software and
assets under their respective licenses. Direct dependencies and media-generation tools are listed
here; `uv.lock`, `web/package-lock.json`, and `demo-video/package-lock.json` are the authoritative
version and transitive-dependency records.

## Runtime and integration dependencies

| Component                                 | Use                                               | License / source                                                                            |
| ----------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| DataHub Core and `acryl-datahub`          | Metadata graph, local quickstart, SDK integration | Apache-2.0, [datahub-project/datahub](https://github.com/datahub-project/datahub)           |
| DataHub MCP Server (`mcp-server-datahub`) | Official read and mutation tool interface         | Apache-2.0, [acryldata/mcp-server-datahub](https://github.com/acryldata/mcp-server-datahub) |
| FastMCP                                   | MCP client/runtime integration                    | Apache-2.0, [jlowin/fastmcp](https://github.com/jlowin/fastmcp)                             |
| DuckDB                                    | Transactional synthetic executor                  | MIT, [duckdb/duckdb](https://github.com/duckdb/duckdb)                                      |
| Pydantic, Typer, Rich                     | Typed models and CLI                              | MIT                                                                                         |
| React and React DOM                       | Reviewer workbench                                | MIT                                                                                         |
| Vite and `@vitejs/plugin-react`           | Reviewer workbench build                          | MIT                                                                                         |
| XYFlow / React Flow                       | Impact-map rendering                              | MIT, [xyflow/xyflow](https://github.com/xyflow/xyflow)                                      |
| Tabler Icons                              | Interface icons                                   | MIT, [tabler/tabler-icons](https://github.com/tabler/tabler-icons)                          |

## Fonts

| Component                                            | Use                                         | License / source                                                                                     |
| ---------------------------------------------------- | ------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| Fontsource Fraunces                                  | Workbench display typeface and packaging    | SIL Open Font License 1.1                                                                            |
| Fontsource IBM Plex Sans Condensed and IBM Plex Mono | Workbench interface typefaces and packaging | SIL Open Font License 1.1                                                                            |
| Inter                                                | Demo-video interface typeface               | SIL Open Font License 1.1, [rsms/inter](https://github.com/rsms/inter)                               |
| JetBrains Mono                                       | Demo-video evidence typeface                | SIL Open Font License 1.1, [JetBrains/JetBrainsMono](https://github.com/JetBrains/JetBrainsMono)     |
| EB Garamond                                          | Demo-video editorial typeface               | SIL Open Font License 1.1, [octaviopardo/EBGaramond12](https://github.com/octaviopardo/EBGaramond12) |

## Demo-video and generation tools

| Component                                          | Use                                           | License / source                                                                                                                                              |
| -------------------------------------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GSAP 3.14.2                                        | Deterministic demo-video motion               | GSAP Standard "No Charge" License, [gsap.com/licensing](https://gsap.com/licensing/)                                                                          |
| HyperFrames 0.7.58                                 | Demo-video composition and rendering          | Apache-2.0, [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes)                                                                               |
| Kokoro ONNX runtime                                | Local synthetic narration generation          | MIT, [thewh1teagle/kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx)                                                                                  |
| Kokoro-82M / Kokoro-82M-v1.0-ONNX model and voices | Local synthetic narration model               | Apache-2.0, [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) and [ONNX conversion](https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX) |
| whisper.cpp and `ggml-base.en`                     | Local transcript timing and caption alignment | MIT, [ggml-org/whisper.cpp](https://github.com/ggml-org/whisper.cpp)                                                                                          |

## Development and validation dependencies

| Component group                | Use                                         | License    |
| ------------------------------ | ------------------------------------------- | ---------- |
| mypy, pytest, pytest-cov, Ruff | Python type, test, coverage, and lint gates | MIT        |
| Testing Library, Vitest, jsdom | Web tests                                   | MIT        |
| ESLint and plugins, Prettier   | Web lint and formatting                     | MIT        |
| TypeScript                     | Web type checking                           | Apache-2.0 |
| axe-core                       | Automated accessibility checks              | MPL-2.0    |

The demo video uses no third-party music or stock footage. Visible product imagery is captured
from this repository's synthetic ForgetOps workbench. Interface symbols are covered by the Tabler
Icons notice above. No DataHub or other third-party logo is used as the project identity. No
pre-existing application code or private dataset is incorporated into the submission.
