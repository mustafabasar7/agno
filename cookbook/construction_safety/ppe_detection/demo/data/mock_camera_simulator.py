#!/usr/bin/env python3
"""
Mock Camera Simulator for Demo

Simulates camera feeds for demo purposes without requiring actual cameras.
Can loop videos, simulate RTSP streams, and generate test patterns.
"""

import cv2
import numpy as np
import time
import argparse
import threading
from pathlib import Path
from typing import Optional
import sys


class MockCameraSimulator:
    """Simulate camera feeds for demo purposes"""

    def __init__(
        self,
        video_path: Optional[str] = None,
        loop: bool = True,
        fps: int = 30,
        camera_name: str = "Mock Camera"
    ):
        """
        Initialize mock camera simulator.

        Args:
            video_path: Path to video file (if None, generates test pattern)
            loop: Loop video when it ends
            fps: Frames per second
            camera_name: Name of the camera
        """
        self.video_path = video_path
        self.loop = loop
        self.fps = fps
        self.camera_name = camera_name
        self.running = False
        self.cap = None

    def _generate_test_pattern(self, width: int = 1920, height: int = 1080) -> np.ndarray:
        """
        Generate a test pattern image.

        Args:
            width: Image width
            height: Image height

        Returns:
            Test pattern image
        """
        # Create test pattern
        img = np.zeros((height, width, 3), dtype=np.uint8)

        # Add color bars
        bar_width = width // 7
        colors = [
            (255, 255, 255),  # White
            (255, 255, 0),    # Yellow
            (0, 255, 255),    # Cyan
            (0, 255, 0),      # Green
            (255, 0, 255),    # Magenta
            (255, 0, 0),      # Red
            (0, 0, 255),      # Blue
        ]

        for i, color in enumerate(colors):
            x1 = i * bar_width
            x2 = (i + 1) * bar_width
            img[:, x1:x2] = color

        # Add text
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(
            img,
            f"{self.camera_name}",
            (50, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 0, 0),
            3
        )
        cv2.putText(
            img,
            f"TEST PATTERN - {timestamp}",
            (50, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 0),
            2
        )
        cv2.putText(
            img,
            "Mock Camera Simulator",
            (50, 200),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 0),
            2
        )

        return img

    def start(self, display: bool = True):
        """
        Start the mock camera feed.

        Args:
            display: Whether to display the feed in a window
        """
        print(f"Starting {self.camera_name}...")

        if self.video_path and Path(self.video_path).exists():
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                print(f"Error: Could not open video file: {self.video_path}")
                return

            # Get video properties
            total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            print(f"Video: {self.video_path}")
            print(f"Resolution: {width}x{height}")
            print(f"FPS: {video_fps}")
            print(f"Total frames: {total_frames}")
            print(f"Loop: {self.loop}")
        else:
            if self.video_path:
                print(f"Warning: Video file not found: {self.video_path}")
            print("Using test pattern instead")
            self.cap = None

        self.running = True
        frame_delay = 1.0 / self.fps

        frame_count = 0

        try:
            while self.running:
                start_time = time.time()

                if self.cap is not None:
                    # Read from video
                    ret, frame = self.cap.read()

                    if not ret:
                        if self.loop:
                            # Loop video
                            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            ret, frame = self.cap.read()
                            if not ret:
                                print("Error reading video frame")
                                break
                        else:
                            print("Video ended")
                            break

                    # Add timestamp overlay
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    cv2.putText(
                        frame,
                        f"{self.camera_name} - {timestamp}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2
                    )
                else:
                    # Generate test pattern
                    frame = self._generate_test_pattern()

                frame_count += 1

                # Display frame
                if display:
                    cv2.imshow(self.camera_name, frame)

                    # Handle keyboard
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        print("\nStopping (user requested)...")
                        break
                    elif key == ord('s'):
                        # Save screenshot
                        screenshot_path = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
                        cv2.imwrite(screenshot_path, frame)
                        print(f"Screenshot saved: {screenshot_path}")

                # Maintain FPS
                elapsed = time.time() - start_time
                sleep_time = max(0, frame_delay - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

                # Print progress every 100 frames
                if frame_count % 100 == 0:
                    actual_fps = 1.0 / max(elapsed, 0.001)
                    print(f"Frames: {frame_count}, FPS: {actual_fps:.1f}")

        except KeyboardInterrupt:
            print("\nStopping (interrupted)...")
        finally:
            self.stop()

        print(f"Total frames processed: {frame_count}")

    def stop(self):
        """Stop the mock camera feed"""
        self.running = False

        if self.cap is not None:
            self.cap.release()

        cv2.destroyAllWindows()

    def get_frame(self) -> Optional[np.ndarray]:
        """
        Get a single frame from the mock camera.

        Returns:
            Frame as numpy array, or None if not available
        """
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                return frame
            elif self.loop:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
                return frame if ret else None
        else:
            return self._generate_test_pattern()

        return None


class MockRTSPServer:
    """
    Simulate RTSP server for demo.

    Note: This is a simplified simulation. For real RTSP streaming,
    use tools like ffmpeg or MediaMTX.
    """

    def __init__(self, port: int = 8554):
        """
        Initialize mock RTSP server.

        Args:
            port: Server port
        """
        self.port = port
        self.cameras = {}
        self.running = False

    def add_camera(self, stream_name: str, simulator: MockCameraSimulator):
        """
        Add a camera to the server.

        Args:
            stream_name: RTSP stream name
            simulator: MockCameraSimulator instance
        """
        self.cameras[stream_name] = simulator
        print(f"Camera added: rtsp://localhost:{self.port}/{stream_name}")

    def start(self):
        """Start RTSP server"""
        print(f"\nMock RTSP Server starting on port {self.port}...")
        print("\nNote: This is a simplified mock RTSP server for demo purposes.")
        print("For real RTSP streaming, use ffmpeg or MediaMTX.\n")
        print("Available streams:")

        for stream_name, simulator in self.cameras.items():
            print(f"  rtsp://localhost:{self.port}/{stream_name}")

        print("\nTo use with VLC or other players:")
        print(f"  vlc rtsp://localhost:{self.port}/<stream_name>")
        print("\nPress Ctrl+C to stop\n")

        self.running = True

        # Start all cameras in separate threads
        threads = []
        for stream_name, simulator in self.cameras.items():
            thread = threading.Thread(
                target=simulator.start,
                kwargs={"display": True}
            )
            thread.daemon = True
            thread.start()
            threads.append(thread)

        try:
            # Wait for threads
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            print("\nStopping server...")
            self.running = False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Mock Camera Simulator for PPE Detection Demo"
    )
    parser.add_argument(
        '--video',
        type=str,
        help='Path to video file (if not provided, uses test pattern)'
    )
    parser.add_argument(
        '--loop',
        action='store_true',
        help='Loop video when it ends'
    )
    parser.add_argument(
        '--fps',
        type=int,
        default=30,
        help='Frames per second (default: 30)'
    )
    parser.add_argument(
        '--name',
        type=str,
        default='Mock Camera',
        help='Camera name'
    )
    parser.add_argument(
        '--rtsp',
        action='store_true',
        help='Start mock RTSP server'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8554,
        help='RTSP server port (default: 8554)'
    )
    parser.add_argument(
        '--stream-name',
        type=str,
        default='cam1',
        help='RTSP stream name (default: cam1)'
    )
    parser.add_argument(
        '--no-display',
        action='store_true',
        help='Do not display video window'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("MOCK CAMERA SIMULATOR")
    print("KKD Tespit Sistemi Demo / PPE Detection System Demo")
    print("=" * 80)
    print()

    if args.rtsp:
        # RTSP server mode
        server = MockRTSPServer(port=args.port)

        # Add camera(s)
        simulator = MockCameraSimulator(
            video_path=args.video,
            loop=args.loop,
            fps=args.fps,
            camera_name=args.name
        )
        server.add_camera(args.stream_name, simulator)

        # Start server
        server.start()

    else:
        # Single camera mode
        simulator = MockCameraSimulator(
            video_path=args.video,
            loop=args.loop,
            fps=args.fps,
            camera_name=args.name
        )

        print("Controls:")
        print("  'q' - Quit")
        print("  's' - Save screenshot")
        print()

        simulator.start(display=not args.no_display)

    print("\nMock camera simulator stopped")


if __name__ == "__main__":
    main()
