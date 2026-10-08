// Percorso di Chromium condiviso da Playwright e Lighthouse.
import { chromium } from 'playwright';

export function chromePath() {
  return process.env.CHROME_PATH || chromium.executablePath();
}

// Flag per WebGL software (SwiftShader) in headless.
export const GL_ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'];
