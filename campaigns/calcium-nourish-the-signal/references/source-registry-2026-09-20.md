# Source registry — Calcium / NOURISH THE SIGNAL execution v1

Verified/seeded: 2026-09-20.

## Campaign/employer context

1. Calcium+Company official site
   https://calciumco.com/
   Use for public company positioning only. Current site describes Calcium+Company as a health communications group and Cobalt as its technology/innovation division; it also references the proprietary NORA AI platform.

2. User-supplied LinkedIn job posting
   https://www.linkedin.com/jobs/view/4452316145/
   Treat as application-role input. Re-check availability before quoting current posting status.

## OpenAI

3. OpenAI image generation guide
   https://developers.openai.com/api/docs/guides/image-generation
   Re-check current GPT Image model IDs and supported sizes/quality before execution.

4. OpenAI video generation guide
   https://developers.openai.com/api/docs/guides/video-generation
   CRITICAL: on 2026-09-20 the guide states Sora 2 models and Videos API are deprecated and scheduled to shut down 2026-09-24. Do not create a new Sora video integration unless official docs change.

## xAI / Grok

5. xAI Imagine overview
   https://docs.x.ai/developers/model-capabilities/imagine

6. xAI video generation
   https://docs.x.ai/developers/model-capabilities/video/generation
   Current docs support text-to-video, image-to-video, reference-to-video, first/last-frame control, edits and extensions for the documented Imagine video models. Verify exact model name at execution time.

7. xAI file inputs for Imagine
   https://docs.x.ai/developers/model-capabilities/imagine/files/inputs
   Useful for reference-image/video reuse by file_id.

## ComfyUI / Wan

8. Official ComfyUI repository
   https://github.com/Comfy-Org/ComfyUI
   Canonical install/runtime source. Do not use an unofficial fork for production setup without documenting why.

9. ComfyUI documentation
   https://docs.comfy.org/
   Verify workflow/API behavior and node availability against current docs/runtime.

10. Official Wan2.2 repository
    https://github.com/Wan-Video/Wan2.2
    Use for model-family/runtime requirements and licenses. Do not download weights until GPU/storage/license conditions are explicitly satisfied.

## Repository-local authorities

11. `ARCHITECTURE.md`
12. `campaigns/calcium-nourish-the-signal/creative-contract.json`
13. `campaigns/calcium-nourish-the-signal/tokens.json`
14. `campaigns/calcium-nourish-the-signal/tasks/keyframes.yaml`
15. `campaigns/calcium-nourish-the-signal/tasks/motion-isolates.yaml`
16. `campaigns/calcium-nourish-the-signal/workflows/wan-staged-api.json`
17. `campaigns/calcium-nourish-the-signal/qa/qa-report.yaml`
18. `tests/test_campaign.py`
19. `.github/workflows/campaign-validation.yml`

Repository-local semantic contracts remain authoritative for campaign intent. External provider docs are authoritative for provider capability/model/runtime facts. Do not allow provider behavior to rewrite the campaign observations or creative contract without an explicit reviewed decision.
