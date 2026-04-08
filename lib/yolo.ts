import * as ort from 'onnxruntime-web';
import { COCO_CLASSES } from './classes';

export interface Detection {
  x1: number; y1: number; x2: number; y2: number;
  confidence: number; classId: number; label: string;
}

const MODEL_URL =
  'https://huggingface.co/nicolo-calcagni-ds/yolov8n-onnx/resolve/main/yolov8n.onnx';

const INPUT_SIZE = 640;
let session: ort.InferenceSession | null = null;
let loading = false;

export async function loadModel(
  onProgress?: (p: number) => void
): Promise<void> {
  if (session || loading) return;
  loading = true;

  ort.env.wasm.wasmPaths =
    'https://cdn.jsdelivr.net/npm/onnxruntime-web@1.18.0/dist/';
  ort.env.wasm.numThreads = 1;

  onProgress?.(5);

  const res = await fetch(MODEL_URL);
  const total = Number(res.headers.get('content-length') || 0);
  const reader = res.body!.getReader();
  const chunks: Uint8Array[] = [];
  let received = 0;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
    received += value.length;
    if (total) onProgress?.(5 + Math.round((received / total) * 80));
  }

  const buf = new Uint8Array(received);
  let off = 0;
  for (const c of chunks) { buf.set(c, off); off += c.length; }

  onProgress?.(88);
  session = await ort.InferenceSession.create(buf.buffer, {
    executionProviders: ['wasm'],
  });
  onProgress?.(100);
  loading = false;
}

function preprocess(source: HTMLVideoElement | HTMLImageElement | ImageData): Float32Array {
  const canvas = document.createElement('canvas');
  canvas.width = INPUT_SIZE; canvas.height = INPUT_SIZE;
  const ctx = canvas.getContext('2d')!;

  if (source instanceof ImageData) {
    const tmp = document.createElement('canvas');
    tmp.width = source.width; tmp.height = source.height;
    tmp.getContext('2d')!.putImageData(source, 0, 0);
    ctx.drawImage(tmp, 0, 0, INPUT_SIZE, INPUT_SIZE);
  } else {
    ctx.drawImage(source, 0, 0, INPUT_SIZE, INPUT_SIZE);
  }

  const imgData = ctx.getImageData(0, 0, INPUT_SIZE, INPUT_SIZE).data;
  const tensor = new Float32Array(3 * INPUT_SIZE * INPUT_SIZE);
  for (let i = 0; i < INPUT_SIZE * INPUT_SIZE; i++) {
    tensor[i] = imgData[i * 4] / 255;
    tensor[INPUT_SIZE * INPUT_SIZE + i] = imgData[i * 4 + 1] / 255;
    tensor[2 * INPUT_SIZE * INPUT_SIZE + i] = imgData[i * 4 + 2] / 255;
  }
  return tensor;
}

function iou(a: Detection, b: Detection): number {
  const ix1 = Math.max(a.x1, b.x1), iy1 = Math.max(a.y1, b.y1);
  const ix2 = Math.min(a.x2, b.x2), iy2 = Math.min(a.y2, b.y2);
  const inter = Math.max(0, ix2 - ix1) * Math.max(0, iy2 - iy1);
  const ua = (a.x2-a.x1)*(a.y2-a.y1) + (b.x2-b.x1)*(b.y2-b.y1) - inter;
  return ua > 0 ? inter / ua : 0;
}

function nms(dets: Detection[], iouThresh = 0.45): Detection[] {
  dets.sort((a, b) => b.confidence - a.confidence);
  const kept: Detection[] = [];
  const suppressed = new Set<number>();
  for (let i = 0; i < dets.length; i++) {
    if (suppressed.has(i)) continue;
    kept.push(dets[i]);
    for (let j = i + 1; j < dets.length; j++) {
      if (!suppressed.has(j) && iou(dets[i], dets[j]) > iouThresh)
        suppressed.add(j);
    }
  }
  return kept;
}

export async function detect(
  source: HTMLVideoElement | HTMLImageElement | HTMLCanvasElement,
  confThresh = 0.4
): Promise<Detection[]> {
  if (!session) throw new Error('Model not loaded');

  const srcWidth = source instanceof HTMLVideoElement
    ? source.videoWidth : source.width;
  const srcHeight = source instanceof HTMLVideoElement
    ? source.videoHeight : source.height;

  const tensor = preprocess(source as HTMLVideoElement);
  const input = new ort.Tensor('float32', tensor, [1, 3, INPUT_SIZE, INPUT_SIZE]);
  const results = await session.run({ images: input });

  const output = results[Object.keys(results)[0]].data as Float32Array;
  const numDets = 8400;
  const scaleX = srcWidth / INPUT_SIZE;
  const scaleY = srcHeight / INPUT_SIZE;

  const detections: Detection[] = [];
  for (let i = 0; i < numDets; i++) {
    const cx = output[i];
    const cy = output[numDets + i];
    const w  = output[2 * numDets + i];
    const h  = output[3 * numDets + i];

    let maxConf = 0, classId = 0;
    for (let c = 0; c < 80; c++) {
      const v = output[(4 + c) * numDets + i];
      if (v > maxConf) { maxConf = v; classId = c; }
    }
    if (maxConf < confThresh) continue;

    detections.push({
      x1: (cx - w / 2) * scaleX,
      y1: (cy - h / 2) * scaleY,
      x2: (cx + w / 2) * scaleX,
      y2: (cy + h / 2) * scaleY,
      confidence: maxConf,
      classId,
      label: COCO_CLASSES[classId] ?? `class${classId}`,
    });
  }

  return nms(detections);
}