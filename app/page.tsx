'use client';

import React, { useRef, useState, useEffect, useCallback } from 'react';
import { loadModel, detect, Detection } from '@/lib/yolo';
import { CLASS_COLORS } from '@/lib/classes';

type Mode = 'camera' | 'image';
type ModelState = 'idle' | 'loading' | 'ready' | 'error';

export default function Home() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const rafRef = useRef<number>(0);
  const streamRef = useRef<MediaStream | null>(null);

  const [mode, setMode] = useState<Mode>('camera');
  const [modelState, setModelState] = useState<ModelState>('idle');
  const [loadProgress, setLoadProgress] = useState(0);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [fps, setFps] = useState(0);
  const [running, setRunning] = useState(false);
  const [confidence, setConfidence] = useState(0.4);
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [imageDetected, setImageDetected] = useState(false);
  const [camError, setCamError] = useState('');
  const [totalFrames, setTotalFrames] = useState(0);

  const fpsRef = useRef({ frames: 0, last: Date.now() });

  useEffect(() => {
    setModelState('loading');
    loadModel((p) => setLoadProgress(p))
      .then(() => setModelState('ready'))
      .catch(() => setModelState('error'));
  }, []);

  const drawDetections = useCallback(
    (dets: Detection[], w: number, h: number) => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      canvas.width = w;
      canvas.height = h;
      const ctx = canvas.getContext('2d')!;
      ctx.clearRect(0, 0, w, h);

      dets.forEach((d) => {
        const color = CLASS_COLORS[d.classId % CLASS_COLORS.length];
        const bw = d.x2 - d.x1, bh = d.y2 - d.y1;

        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.shadowColor = color;
        ctx.shadowBlur = 8;
        ctx.strokeRect(d.x1, d.y1, bw, bh);
        ctx.shadowBlur = 0;

        const cs = 12;
        ctx.lineWidth = 3;
        const corners = [
          [d.x1, d.y1, cs, 0, 0, cs],
          [d.x2, d.y1, -cs, 0, 0, cs],
          [d.x1, d.y2, cs, 0, 0, -cs],
          [d.x2, d.y2, -cs, 0, 0, -cs],
        ];
        corners.forEach(([x, y, dx1, , , dy2]) => {
          ctx.beginPath();
          ctx.moveTo(x + dx1, y);
          ctx.lineTo(x, y);
          ctx.lineTo(x, y + dy2);
          ctx.stroke();
        });

        const label = `${d.label.toUpperCase()}  ${(d.confidence * 100).toFixed(0)}%`;
        ctx.font = 'bold 11px "Share Tech Mono"';
        const tw = ctx.measureText(label).width;
        const lx = d.x1, ly = d.y1 > 20 ? d.y1 - 22 : d.y1 + 2;
        ctx.fillStyle = color + 'dd';
        ctx.fillRect(lx, ly, tw + 10, 18);
        ctx.fillStyle = '#000';
        ctx.fillText(label, lx + 5, ly + 13);
      });
    },
    []
  );

  const cameraLoop = useCallback(() => {
    if (!videoRef.current || !running) return;
    const vid = videoRef.current;
    if (vid.readyState < 2) {
      rafRef.current = requestAnimationFrame(cameraLoop);
      return;
    }
    detect(vid, confidence)
      .then((dets) => {
        setDetections(dets);
        drawDetections(dets, vid.videoWidth || 640, vid.videoHeight || 480);
        const now = Date.now();
        fpsRef.current.frames++;
        if (now - fpsRef.current.last >= 1000) {
          setFps(fpsRef.current.frames);
          setTotalFrames((p) => p + fpsRef.current.frames);
          fpsRef.current.frames = 0;
          fpsRef.current.last = now;
        }
      })
      .catch(() => {})
      .finally(() => { rafRef.current = requestAnimationFrame(cameraLoop); });
  }, [running, confidence, drawDetections]);

  useEffect(() => {
    if (running && mode === 'camera') {
      rafRef.current = requestAnimationFrame(cameraLoop);
    }
    return () => cancelAnimationFrame(rafRef.current);
  }, [running, mode, cameraLoop]);

  const startCamera = async () => {
    setCamError('');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' },
      });
      streamRef.current = stream;
      if (videoRef.current) { videoRef.current.srcObject = stream; await videoRef.current.play(); }
      setRunning(true);
    } catch (e: unknown) {
      setCamError(e instanceof Error ? e.message : 'Camera access denied');
    }
  };

  const stopCamera = () => {
    cancelAnimationFrame(rafRef.current);
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setRunning(false); setDetections([]); setFps(0);
    canvasRef.current?.getContext('2d')?.clearRect(0, 0, 9999, 9999);
  };

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]; if (!file) return;
    setUploadedImage(URL.createObjectURL(file));
    setImageDetected(false); setDetections([]);
    canvasRef.current?.getContext('2d')?.clearRect(0, 0, 9999, 9999);
  };

  const runImageDetection = async () => {
    if (!imgRef.current || !uploadedImage) return;
    const img = imgRef.current;
    await new Promise((r) => { img.onload = r; img.src = uploadedImage; });
    const dets = await detect(img as unknown as HTMLVideoElement, confidence);
    setDetections(dets);
    drawDetections(dets, img.naturalWidth, img.naturalHeight);
    setImageDetected(true);
  };

  const switchMode = (m: Mode) => {
    if (m === mode) return;
    stopCamera(); setUploadedImage(null); setImageDetected(false); setDetections([]); setMode(m);
  };

  const topClasses = [...new Map(detections.map((d) => [d.classId, d])).values()]
    .sort((a, b) => b.confidence - a.confidence).slice(0, 8);

  return (
    <main style={{ position: 'relative', minHeight: '100vh', padding: '24px', zIndex: 1 }}>
      <header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '28px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ width: '42px', height: '42px', border: '1.5px solid var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
              <rect x="3" y="3" width="7" height="7" stroke="var(--accent)" strokeWidth="1.5"/>
              <rect x="14" y="3" width="7" height="7" stroke="var(--accent)" strokeWidth="1.5"/>
              <rect x="3" y="14" width="7" height="7" stroke="var(--accent)" strokeWidth="1.5"/>
              <circle cx="17.5" cy="17.5" r="2.5" stroke="var(--accent3)" strokeWidth="1.5"/>
            </svg>
            <div style={{ position: 'absolute', top: '-1px', right: '-1px', width: '6px', height: '6px', background: modelState === 'ready' ? 'var(--success)' : modelState === 'loading' ? 'var(--accent)' : 'var(--accent3)', borderRadius: '50%', animation: modelState === 'loading' ? 'pulse 1s infinite' : 'none' }}/>
          </div>
          <div>
            <h1 style={{ fontFamily: 'var(--display)', fontWeight: 700, fontSize: '22px', letterSpacing: '3px', color: '#fff', textTransform: 'uppercase' }}>
              YOLO<span style={{ color: 'var(--accent)' }}>v8</span> DETECTOR
            </h1>
            <p style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: 'var(--text-dim)', letterSpacing: '2px' }}>
              REAL-TIME · 80 CLASSES · ONNX RUNTIME
            </p>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
          <StatusBadge state={modelState} progress={loadProgress} />
          {running && <div style={{ fontFamily: 'var(--mono)', fontSize: '12px', color: 'var(--success)', border: '1px solid var(--success)33', padding: '4px 12px', letterSpacing: '1px' }}>{fps} FPS</div>}
          <div style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: 'var(--text-dim)', padding: '4px 12px', border: '1px solid var(--border)' }}>{detections.length} OBJ</div>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gap: '20px', alignItems: 'start' }}>
        <div>
          <div style={{ display: 'flex', marginBottom: '16px', border: '1px solid var(--border)', width: 'fit-content' }}>
            {(['camera', 'image'] as Mode[]).map((m) => (
              <button key={m} onClick={() => switchMode(m)} style={{ padding: '8px 24px', fontFamily: 'var(--display)', fontWeight: 600, fontSize: '13px', letterSpacing: '2px', textTransform: 'uppercase', background: mode === m ? 'var(--accent)18' : 'transparent', color: mode === m ? 'var(--accent)' : 'var(--text-dim)', border: 'none', borderRight: m === 'camera' ? '1px solid var(--border)' : 'none', cursor: 'pointer' }}>
                {m === 'camera' ? '⬡ LIVE' : '⊞ IMAGE'}
              </button>
            ))}
          </div>

          <div style={{ position: 'relative', background: 'var(--surface)', border: '1px solid var(--border)', overflow: 'hidden', minHeight: '420px', display: 'flex', alignItems: 'center', justifyContent: 'center' }} className="scanlines">
            {mode === 'camera' ? (
              <>
                <video ref={videoRef} muted playsInline style={{ display: 'block', width: '100%', maxHeight: '520px', objectFit: 'contain', opacity: running ? 1 : 0 }} />
                {!running && (
                  <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px' }}>
                    <div style={{ width: '80px', height: '80px', border: '1px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <svg width="36" height="36" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="3" stroke="var(--text-dim)" strokeWidth="1.5"/><path d="M3 9l2-2h14l2 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" stroke="var(--text-dim)" strokeWidth="1.5"/></svg>
                    </div>
                    {camError && <p style={{ fontFamily: 'var(--mono)', fontSize: '12px', color: 'var(--accent3)', maxWidth: '300px', textAlign: 'center' }}>{camError}</p>}
                    <p style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: 'var(--text-dim)', letterSpacing: '2px' }}>CAMERA INACTIVE</p>
                  </div>
                )}
              </>
            ) : (
              <>
                {uploadedImage ? (
                  <div style={{ position: 'relative', width: '100%' }}>
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img ref={imgRef} src={uploadedImage} alt="uploaded" style={{ display: 'block', width: '100%', maxHeight: '520px', objectFit: 'contain' }} />
                  </div>
                ) : (
                  <label style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px', cursor: 'pointer', padding: '60px' }}>
                    <div style={{ width: '80px', height: '80px', border: '1px dashed var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <svg width="32" height="32" viewBox="0 0 24 24" fill="none"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12" stroke="var(--text-dim)" strokeWidth="1.5" strokeLinecap="round"/></svg>
                    </div>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: 'var(--text-dim)', letterSpacing: '2px' }}>DROP IMAGE / CLICK TO UPLOAD</span>
                    <input type="file" accept="image/*" onChange={handleUpload} style={{ display: 'none' }} />
                  </label>
                )}
              </>
            )}
            <canvas ref={canvasRef} style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', pointerEvents: 'none', maxWidth: '100%', maxHeight: '520px' }} />
          </div>

          <div style={{ display: 'flex', gap: '10px', marginTop: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
            {mode === 'camera' ? (
              <ActionButton onClick={running ? stopCamera : startCamera} disabled={modelState !== 'ready'} variant={running ? 'danger' : 'primary'} label={running ? '■ STOP DETECTION' : '▶ START CAMERA'} />
            ) : (
              <>
                <label style={{ cursor: 'pointer' }}>
                  <ActionButton as="span" label="⊞ UPLOAD IMAGE" variant="secondary" />
                  <input type="file" accept="image/*" onChange={handleUpload} style={{ display: 'none' }} />
                </label>
                {uploadedImage && <ActionButton onClick={runImageDetection} disabled={modelState !== 'ready'} variant="primary" label="⬡ RUN DETECTION" />}
              </>
            )}
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginLeft: 'auto' }}>
              <span style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: 'var(--text-dim)', letterSpacing: '1px', whiteSpace: 'nowrap' }}>CONF {(confidence * 100).toFixed(0)}%</span>
              <input type="range" min="10" max="90" value={confidence * 100} onChange={(e) => setConfidence(Number(e.target.value) / 100)} style={{ width: '100px', accentColor: 'var(--accent)', cursor: 'pointer' }} />
            </div>
          </div>
        </div>

        <aside style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <Panel title="DETECTIONS">
            {topClasses.length === 0 ? (
              <p style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: 'var(--text-dim)', padding: '12px 0', textAlign: 'center', letterSpacing: '1px' }}>NO OBJECTS DETECTED</p>
            ) : (
              topClasses.map((d, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: CLASS_COLORS[d.classId % CLASS_COLORS.length], flexShrink: 0 }} />
                  <span style={{ fontFamily: 'var(--display)', fontWeight: 600, fontSize: '13px', textTransform: 'uppercase', letterSpacing: '1px', flex: 1 }}>{d.label}</span>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: CLASS_COLORS[d.classId % CLASS_COLORS.length] }}>{(d.confidence * 100).toFixed(0)}%</span>
                </div>
              ))
            )}
          </Panel>

          <Panel title="SYSTEM">
            <Stat label="MODEL" value="YOLOv8n" />
            <Stat label="RUNTIME" value="ONNX Web" />
            <Stat label="CLASSES" value="80 COCO" />
            <Stat label="INPUT" value="640x640" />
            <Stat label="DEVICE" value="WebAssembly" />
            {running && <Stat label="FPS" value={`${fps}`} highlight />}
            {totalFrames > 0 && <Stat label="FRAMES" value={`${totalFrames}`} />}
          </Panel>

          {detections.length > 0 && (
            <Panel title="ALL OBJECTS">
              {Object.entries(detections.reduce<Record<string, number>>((acc, d) => { acc[d.label] = (acc[d.label] || 0) + 1; return acc; }, {})).map(([label, count]) => (
                <div key={label} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid var(--border)' }}>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: 'var(--text-dim)', textTransform: 'uppercase' }}>{label}</span>
                  <span style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: 'var(--accent)' }}>x{count}</span>
                </div>
              ))}
            </Panel>
          )}
        </aside>
      </div>

      {modelState === 'loading' && (
        <div style={{ position: 'fixed', inset: 0, background: '#050810ee', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '20px', zIndex: 50 }}>
          <div style={{ fontFamily: 'var(--display)', fontSize: '28px', fontWeight: 700, letterSpacing: '6px', color: '#fff' }}>INITIALIZING<span style={{ color: 'var(--accent)' }}>.</span></div>
          <div style={{ width: '320px', height: '2px', background: 'var(--border)', position: 'relative', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', left: 0, top: 0, height: '100%', background: 'var(--accent)', width: `${loadProgress}%`, transition: 'width 0.3s', boxShadow: '0 0 12px var(--accent)' }} />
          </div>
          <p style={{ fontFamily: 'var(--mono)', fontSize: '12px', color: 'var(--text-dim)', letterSpacing: '2px' }}>LOADING YOLOv8n · {loadProgress}%</p>
        </div>
      )}
      <style jsx global>{`@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }`}</style>
    </main>
  );
}

function StatusBadge({ state, progress }: { state: ModelState; progress: number }) {
  const map = { idle: { color: 'var(--text-dim)', label: 'IDLE' }, loading: { color: 'var(--accent)', label: `LOADING ${progress}%` }, ready: { color: 'var(--success)', label: 'MODEL READY' }, error: { color: 'var(--accent3)', label: 'ERROR' } };
  const s = map[state];
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', border: `1px solid ${s.color}44`, padding: '4px 12px' }}>
      <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: s.color, animation: state === 'loading' ? 'pulse 1s infinite' : 'none' }} />
      <span style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: s.color, letterSpacing: '1px' }}>{s.label}</span>
    </div>
  );
}

function ActionButton({ onClick, disabled, variant, label, as: As = 'button' }: { onClick?: () => void; disabled?: boolean; variant: string; label: string; as?: React.ElementType; }) {
  const colors = { primary: { bg: 'var(--accent)22', border: 'var(--accent)', color: 'var(--accent)' }, secondary: { bg: 'transparent', border: 'var(--border)', color: 'var(--text-dim)' }, danger: { bg: 'var(--accent3)22', border: 'var(--accent3)', color: 'var(--accent3)' } } as Record<string, { bg: string; border: string; color: string }>;
  const c = colors[variant] ?? colors.secondary;
  return <As onClick={onClick} disabled={disabled} style={{ padding: '8px 20px', fontFamily: 'var(--display)', fontWeight: 600, fontSize: '13px', letterSpacing: '2px', textTransform: 'uppercase', background: disabled ? 'transparent' : c.bg, border: `1px solid ${disabled ? 'var(--border)' : c.border}`, color: disabled ? 'var(--text-dim)' : c.color, cursor: disabled ? 'not-allowed' : 'pointer' }}>{label}</As>;
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div style={{ border: '1px solid var(--border)', background: 'var(--surface)' }}>
      <div style={{ padding: '8px 12px', borderBottom: '1px solid var(--border)', background: 'var(--bg)' }}>
        <span style={{ fontFamily: 'var(--mono)', fontSize: '10px', color: 'var(--accent)', letterSpacing: '3px' }}>{title}</span>
      </div>
      <div style={{ padding: '10px 12px' }}>{children}</div>
    </div>
  );
}

function Stat({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid var(--border)40' }}>
      <span style={{ fontFamily: 'var(--mono)', fontSize: '10px', color: 'var(--text-dim)', letterSpacing: '1px' }}>{label}</span>
      <span style={{ fontFamily: 'var(--mono)', fontSize: '10px', color: highlight ? 'var(--success)' : 'var(--text)', letterSpacing: '1px' }}>{value}</span>
    </div>
  );
}