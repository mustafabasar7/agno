"""Toolkit for concrete crack detection and width measurement."""

import json
from typing import Optional, Dict, Any, List
from agno.tools.toolkit import Toolkit


class CrackDetectionTools(Toolkit):
    """Tools for detecting and measuring cracks in concrete samples.

    This toolkit provides capabilities for:
    - Analyzing concrete images for crack detection
    - Calibrating measurements using reference objects
    - Measuring crack widths in millimeters
    - Generating construction inspection reports
    """

    def __init__(
        self,
        analyze_cracks: bool = True,
        calibrate: bool = True,
        measure_width: bool = True,
        generate_report: bool = True,
    ):
        """Initialize CrackDetectionTools.

        Args:
            analyze_cracks: Enable crack analysis function
            calibrate: Enable calibration function
            measure_width: Enable width measurement function
            generate_report: Enable report generation function
        """
        super().__init__(name="crack_detection_tools")

        if analyze_cracks:
            self.register(self.analyze_concrete_image)
        if calibrate:
            self.register(self.calculate_calibration_factor)
        if measure_width:
            self.register(self.measure_crack_width)
        if generate_report:
            self.register(self.generate_inspection_report)

    def analyze_concrete_image(
        self,
        image_description: str,
        detected_features: Optional[str] = None,
    ) -> str:
        """Analyze a concrete sample image to detect cracks and surface defects.

        This function processes visual information from concrete samples to identify:
        - Presence and location of cracks
        - Crack patterns (linear, branching, network)
        - Surface defects and deterioration
        - Severity assessment

        Args:
            image_description: Detailed description of what you see in the concrete image
            detected_features: JSON string of detected features (cracks, reference objects, etc.)

        Returns:
            JSON string with analysis results including crack detection and characteristics
        """
        analysis = {
            "cracks_detected": True,
            "analysis": image_description,
            "severity": "to_be_determined",
            "recommendations": []
        }

        if detected_features:
            try:
                features = json.loads(detected_features)
                analysis["detected_features"] = features
            except json.JSONDecodeError:
                analysis["detected_features"] = detected_features

        # Add basic recommendations
        if "crack" in image_description.lower():
            analysis["recommendations"].append(
                "Crack detected - proceed with width measurement"
            )
            analysis["recommendations"].append(
                "Use calibration reference for accurate measurements"
            )

        return json.dumps(analysis, indent=2)

    def calculate_calibration_factor(
        self,
        reference_object: str,
        known_dimension_mm: float,
        measured_pixels: Optional[float] = None,
    ) -> str:
        """Calculate the pixel-to-millimeter calibration factor.

        Uses a reference object with known dimensions to establish the conversion
        factor between pixels and millimeters for accurate crack width measurements.

        Common reference objects:
        - Ruler or measuring tape (known length)
        - Standard coin (e.g., 1 cent = 19.05mm diameter)
        - Calibration card or marker

        Args:
            reference_object: Type of reference object used (e.g., "ruler", "coin", "marker")
            known_dimension_mm: Known dimension of reference object in millimeters
            measured_pixels: Measured dimension in pixels (if available from image analysis)

        Returns:
            JSON string with calibration factor and instructions
        """
        calibration_info = {
            "reference_object": reference_object,
            "known_dimension_mm": known_dimension_mm,
            "calibration_status": "pending",
            "instructions": []
        }

        if measured_pixels and measured_pixels > 0:
            # Calculate pixels per millimeter
            pixels_per_mm = measured_pixels / known_dimension_mm
            calibration_info["pixels_per_mm"] = pixels_per_mm
            calibration_info["mm_per_pixel"] = 1.0 / pixels_per_mm
            calibration_info["calibration_status"] = "complete"
            calibration_info["instructions"].append(
                f"Calibration successful: {pixels_per_mm:.2f} pixels = 1 mm"
            )
        else:
            calibration_info["instructions"].extend([
                f"Measure the {reference_object} dimension in the image (pixels)",
                f"Known dimension: {known_dimension_mm} mm",
                "Formula: calibration_factor = measured_pixels / known_dimension_mm"
            ])

        return json.dumps(calibration_info, indent=2)

    def measure_crack_width(
        self,
        crack_description: str,
        calibration_factor: Optional[float] = None,
        estimated_width_pixels: Optional[float] = None,
    ) -> str:
        """Measure crack width in millimeters using calibration data.

        Converts pixel measurements to millimeters using the calibration factor
        and provides crack classification according to construction standards.

        Crack Classification (typical standards):
        - Hair crack: < 0.1 mm
        - Fine crack: 0.1 - 0.3 mm
        - Medium crack: 0.3 - 1.0 mm
        - Wide crack: 1.0 - 3.0 mm
        - Severe crack: > 3.0 mm

        Args:
            crack_description: Description of the crack (location, pattern, appearance)
            calibration_factor: Millimeters per pixel (from calibration)
            estimated_width_pixels: Crack width measurement in pixels

        Returns:
            JSON string with crack width in mm and classification
        """
        measurement = {
            "crack_description": crack_description,
            "measurement_status": "pending",
            "width_mm": None,
            "classification": None,
            "severity_level": None,
            "action_required": None,
        }

        if calibration_factor and estimated_width_pixels:
            # Calculate crack width in millimeters
            width_mm = estimated_width_pixels * calibration_factor
            measurement["width_mm"] = round(width_mm, 3)
            measurement["measurement_status"] = "complete"

            # Classify crack
            if width_mm < 0.1:
                measurement["classification"] = "Hair crack"
                measurement["severity_level"] = "Minimal"
                measurement["action_required"] = "Monitor"
            elif width_mm < 0.3:
                measurement["classification"] = "Fine crack"
                measurement["severity_level"] = "Low"
                measurement["action_required"] = "Monitor and document"
            elif width_mm < 1.0:
                measurement["classification"] = "Medium crack"
                measurement["severity_level"] = "Moderate"
                measurement["action_required"] = "Repair recommended"
            elif width_mm < 3.0:
                measurement["classification"] = "Wide crack"
                measurement["severity_level"] = "High"
                measurement["action_required"] = "Repair required"
            else:
                measurement["classification"] = "Severe crack"
                measurement["severity_level"] = "Critical"
                measurement["action_required"] = "Immediate repair required - structural assessment needed"
        else:
            measurement["instructions"] = [
                "Calibration factor required (mm per pixel)",
                "Crack width in pixels required",
                "Use calculate_calibration_factor first if not available"
            ]

        return json.dumps(measurement, indent=2)

    def generate_inspection_report(
        self,
        project_name: str,
        sample_id: str,
        measurements: str,
        inspector_notes: Optional[str] = None,
    ) -> str:
        """Generate a formatted construction inspection report.

        Creates a professional report suitable for construction documentation
        and building inspection purposes.

        Args:
            project_name: Name of the construction project
            sample_id: Unique identifier for the concrete sample
            measurements: JSON string with measurement data
            inspector_notes: Additional notes or observations

        Returns:
            Formatted inspection report as a string
        """
        from datetime import datetime

        report_lines = [
            "=" * 70,
            "CONCRETE CRACK INSPECTION REPORT",
            "=" * 70,
            "",
            f"Project: {project_name}",
            f"Sample ID: {sample_id}",
            f"Inspection Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "-" * 70,
            "MEASUREMENTS",
            "-" * 70,
        ]

        try:
            data = json.loads(measurements)
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict):
                        report_lines.append(f"\n{key.upper().replace('_', ' ')}:")
                        for sub_key, sub_value in value.items():
                            report_lines.append(f"  {sub_key}: {sub_value}")
                    else:
                        report_lines.append(f"{key}: {value}")
            else:
                report_lines.append(str(data))
        except json.JSONDecodeError:
            report_lines.append(measurements)

        if inspector_notes:
            report_lines.extend([
                "",
                "-" * 70,
                "INSPECTOR NOTES",
                "-" * 70,
                inspector_notes,
            ])

        report_lines.extend([
            "",
            "-" * 70,
            "END OF REPORT",
            "-" * 70,
        ])

        return "\n".join(report_lines)
