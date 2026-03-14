<div class="wrapper">
  <div class="noise-overlay"></div>
  <div class="canvas">
    <div class="pill">
      <slot />
    </div>
  </div>
</div>

<style>
  .wrapper {
    position: relative;
    display: flex;
    min-height: 100vh;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    background-color: #0f111a;
  }

  .noise-overlay {
    pointer-events: none;
    position: fixed;
    inset: 0;
    opacity: 0.04;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  }

  .canvas {
    position: relative;
    width: 100%;
    max-width: 800px;
    aspect-ratio: 2 / 1;
    min-height: 200px;
    padding: 1rem;
  }

  .pill {
    position: absolute;
    left: 50%;
    top: 50%;
    z-index: 10;
    display: flex;
    transform: translate(-50%, -50%);
    align-items: center;
    justify-content: center;
    border-radius: 9999px;
    width: min(90%, 560px);
    height: clamp(40px, 6vw, 48px);
    background: linear-gradient(
      90deg,
      #b8b8b8 0%,
      #e8e8e8 20%,
      #ffffff 50%,
      #e8e8e8 80%,
      #b8b8b8 100%
    );
    box-shadow:
      0 0 0 1px rgba(144, 224, 239, 0.6),
      0 0 12px 1px rgba(144, 224, 239, 0.4),
      0 12px 40px 0 rgba(144, 224, 239, 0.25),
      0 20px 60px 0 rgba(144, 224, 239, 0.15);
  }

  @media (max-width: 640px) {
    .canvas {
      min-height: 160px;
      padding: 0.75rem;
    }

    .pill {
      width: min(95%, 560px);
      height: clamp(36px, 10vw, 48px);
    }
  }
</style>
