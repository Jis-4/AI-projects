import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'YOLOv8 Real-Time Object Detector',
  description: 'Browser-based real-time object detection powered by YOLOv8 ONNX',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}