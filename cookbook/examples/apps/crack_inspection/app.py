"""Gradio Web App for Concrete Crack Width Measurement.

HuggingFace Space deployment ready.
Provides a user-friendly interface for construction inspectors and laboratories.
"""

import json
import os
from pathlib import Path
from typing import Optional, Tuple
import gradio as gr
from agno.agent import Agent
from agno.media import Image
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.tools.crack_detection import CrackDetectionTools
from pydantic import BaseModel, Field


class CrackMeasurement(BaseModel):
    """Structured output for crack measurements."""

    cracks_detected: bool = Field(..., description="Whether cracks were detected")
    crack_count: int = Field(..., description="Number of cracks identified")
    crack_descriptions: list[str] = Field(..., description="Descriptions for each crack")
    calibration_object_detected: bool = Field(..., description="Whether calibration reference found")
    calibration_object_type: Optional[str] = Field(None, description="Type of calibration object")
    reference_dimension_pixels: Optional[float] = Field(None, description="Reference dimension in pixels")
    crack_widths_pixels: list[float] = Field(default_factory=list, description="Crack widths in pixels")
    crack_widths_mm: list[float] = Field(default_factory=list, description="Crack widths in mm")
    crack_classifications: list[str] = Field(
        default_factory=list, description="Classifications (hair/fine/medium/wide/severe)"
    )
    severity_assessment: str = Field(..., description="Overall severity")
    recommendations: list[str] = Field(default_factory=list, description="Recommended actions")


# Global agent instance
_agent = None


def get_agent(model_choice: str = "Claude 3.5 Sonnet"):
    """Get or create agent instance."""
    global _agent

    # Map model choice to actual model
    if model_choice == "GPT-4 Vision":
        model = OpenAIChat(id="gpt-4o")
    elif model_choice == "Claude 3.5 Sonnet":
        model = Claude(id="claude-3-7-sonnet-latest")
    elif model_choice == "Claude 3 Opus":
        model = Claude(id="claude-3-opus-20240229")
    else:
        model = Claude(id="claude-3-7-sonnet-latest")

    # Create agent if not exists or model changed
    if _agent is None or _agent.model != model:
        _agent = Agent(
            name="Crack Inspector",
            model=model,
            tools=[CrackDetectionTools()],
            markdown=True,
            show_tool_calls=True,
            instructions=[
                "You are an expert in concrete inspection and crack analysis for construction projects.",
                "Analyze concrete sample images to detect and measure cracks with precision.",
                "Always search for calibration references (rulers, coins, markers, measuring tape).",
                "Provide accurate measurements in millimeters using calibration data.",
                "Follow international construction standards for crack classification.",
                "Be thorough, professional, and safety-conscious in your analysis.",
                "",
                "MEASUREMENT METHODOLOGY:",
                "1. Identify all visible cracks and their patterns",
                "2. Locate calibration reference if present",
                "3. Measure crack widths in pixels",
                "4. Convert to millimeters using calibration factor",
                "5. Classify severity and provide recommendations",
            ],
            response_model=CrackMeasurement,
        )

    return _agent


def analyze_concrete_image(
    image,
    calibration_mm: Optional[float],
    calibration_type: str,
    project_name: str,
    sample_id: str,
    model_choice: str,
    progress=gr.Progress(),
) -> Tuple[str, str, str]:
    """Analyze concrete image for cracks.

    Args:
        image: Uploaded image
        calibration_mm: Known dimension in mm
        calibration_type: Type of calibration object
        project_name: Project name
        sample_id: Sample identifier
        model_choice: AI model to use
        progress: Gradio progress tracker

    Returns:
        Tuple of (analysis_json, report_text, summary_html)
    """
    if image is None:
        return "Error: Please upload an image", "", ""

    progress(0.1, desc="Initializing agent...")

    try:
        # Get agent
        agent = get_agent(model_choice)

        progress(0.2, desc="Processing image...")

        # Prepare prompt
        prompt_parts = [
            "Analyze this concrete sample image for cracks and structural defects.",
            "",
            "DETAILED ANALYSIS REQUIRED:",
            "1. Examine the entire image systematically for cracks, fissures, and defects",
            "2. Look for calibration references (ruler, coin, measuring tape, markers)",
            "3. For EACH crack detected:",
            "   - Describe precise location (e.g., 'upper left quadrant, 45-degree angle')",
            "   - Describe pattern (linear, branching, network, map-cracking)",
            "   - Estimate width in pixels by comparing to image features",
            "4. If calibration reference found:",
            "   - Identify the object type",
            "   - Measure its dimension in pixels accurately",
            "5. Use the crack detection tools to:",
            "   - Calculate precise calibration factor",
            "   - Convert pixel measurements to millimeters",
            "   - Classify crack severity",
            "",
            "PRECISION REQUIREMENTS:",
            "- Provide specific numerical pixel measurements",
            "- Use sub-pixel accuracy when possible",
            "- Account for image perspective and distortion",
        ]

        if calibration_mm and calibration_mm > 0:
            prompt_parts.extend(
                [
                    "",
                    f"CALIBRATION REFERENCE: {calibration_type} with known dimension of {calibration_mm} mm",
                    "Use this information to calculate the calibration factor.",
                ]
            )

        prompt = "\n".join(prompt_parts)

        progress(0.4, desc="Running AI analysis...")

        # Run analysis
        response = agent.run(prompt, images=[Image(filepath=image if isinstance(image, str) else image.name)])

        progress(0.7, desc="Processing results...")

        # Extract results
        if isinstance(response.content, CrackMeasurement):
            results = response.content.model_dump()
        else:
            results = {"error": "Unexpected response format", "content": str(response.content)}

        # Add metadata
        results["project_name"] = project_name
        results["sample_id"] = sample_id
        results["model_used"] = model_choice

        progress(0.9, desc="Generating report...")

        # Generate formatted output
        analysis_json = json.dumps(results, indent=2)

        # Create report
        report_lines = [
            "=" * 80,
            "CONCRETE CRACK INSPECTION REPORT",
            "=" * 80,
            "",
            f"Project: {project_name}",
            f"Sample ID: {sample_id}",
            f"AI Model: {model_choice}",
            "",
            "-" * 80,
            "FINDINGS",
            "-" * 80,
            "",
        ]

        if results.get("cracks_detected"):
            report_lines.append(f"Cracks Detected: YES ({results.get('crack_count', 0)} crack(s))")
            report_lines.append("")

            # Crack details
            descriptions = results.get("crack_descriptions", [])
            widths_mm = results.get("crack_widths_mm", [])
            classifications = results.get("crack_classifications", [])

            for i, desc in enumerate(descriptions):
                report_lines.append(f"Crack #{i+1}:")
                report_lines.append(f"  Description: {desc}")
                if i < len(widths_mm):
                    report_lines.append(f"  Width: {widths_mm[i]:.3f} mm")
                if i < len(classifications):
                    report_lines.append(f"  Classification: {classifications[i]}")
                report_lines.append("")
        else:
            report_lines.append("Cracks Detected: NO")
            report_lines.append("")

        # Calibration info
        if results.get("calibration_object_detected"):
            report_lines.append(
                f"Calibration Reference: {results.get('calibration_object_type', 'Detected')}"
            )
            report_lines.append("")

        # Severity
        report_lines.extend(
            [
                "-" * 80,
                "SEVERITY ASSESSMENT",
                "-" * 80,
                "",
                results.get("severity_assessment", "N/A"),
                "",
            ]
        )

        # Recommendations
        if results.get("recommendations"):
            report_lines.extend(["-" * 80, "RECOMMENDATIONS", "-" * 80, ""])
            for i, rec in enumerate(results["recommendations"], 1):
                report_lines.append(f"{i}. {rec}")
            report_lines.append("")

        report_lines.extend(["=" * 80, "END OF REPORT", "=" * 80])

        report_text = "\n".join(report_lines)

        # Create HTML summary
        html_parts = ["<div style='font-family: Arial, sans-serif;'>"]

        if results.get("cracks_detected"):
            severity_color = "red" if "severe" in results.get("severity_assessment", "").lower() else "orange"
            html_parts.append(
                f"<h3 style='color: {severity_color};'>⚠️ Cracks Detected: {results.get('crack_count', 0)}</h3>"
            )

            # Crack summary table
            if widths_mm:
                html_parts.append("<table style='width:100%; border-collapse: collapse; margin: 10px 0;'>")
                html_parts.append(
                    "<tr style='background-color: #f0f0f0;'>"
                    "<th style='border: 1px solid #ddd; padding: 8px;'>Crack</th>"
                    "<th style='border: 1px solid #ddd; padding: 8px;'>Width (mm)</th>"
                    "<th style='border: 1px solid #ddd; padding: 8px;'>Classification</th>"
                    "</tr>"
                )
                for i, (width, classification) in enumerate(zip(widths_mm, classifications), 1):
                    html_parts.append(
                        f"<tr>"
                        f"<td style='border: 1px solid #ddd; padding: 8px;'>#{i}</td>"
                        f"<td style='border: 1px solid #ddd; padding: 8px;'>{width:.3f}</td>"
                        f"<td style='border: 1px solid #ddd; padding: 8px;'>{classification}</td>"
                        f"</tr>"
                    )
                html_parts.append("</table>")
        else:
            html_parts.append("<h3 style='color: green;'>✓ No Cracks Detected</h3>")

        html_parts.append(f"<p><strong>Severity:</strong> {results.get('severity_assessment', 'N/A')}</p>")
        html_parts.append("</div>")

        summary_html = "".join(html_parts)

        progress(1.0, desc="Complete!")

        return analysis_json, report_text, summary_html

    except Exception as e:
        error_msg = f"Error during analysis: {str(e)}"
        return error_msg, error_msg, f"<div style='color: red;'>{error_msg}</div>"


# Create Gradio interface
def create_app():
    """Create Gradio app interface."""

    with gr.Blocks(title="Concrete Crack Width Measurement", theme=gr.themes.Soft()) as app:
        gr.Markdown(
            """
        # 🏗️ Concrete Crack Width Measurement System

        **Professional crack detection and measurement for construction inspection**

        Upload a photo of a concrete sample to automatically detect and measure crack widths in millimeters.
        Designed for construction laboratories and building inspection reports.
        """
        )

        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 📸 Image Upload")
                image_input = gr.Image(type="filepath", label="Concrete Sample Image")

                gr.Markdown("### ⚙️ Configuration")

                project_name = gr.Textbox(
                    label="Project Name", value="Construction Project", placeholder="Building A Inspection"
                )

                sample_id = gr.Textbox(label="Sample ID", value="SAMPLE-001", placeholder="S-001")

                with gr.Accordion("🎯 Calibration Settings", open=True):
                    gr.Markdown(
                        """
                    For accurate measurements, include a calibration reference in your image:
                    - Ruler or measuring tape
                    - Standard coin (e.g., 1 cent = 19.05mm)
                    - Calibration marker
                    """
                    )

                    calibration_type = gr.Dropdown(
                        choices=["Ruler", "Coin", "Measuring Tape", "Calibration Marker", "Other"],
                        label="Calibration Object Type",
                        value="Ruler",
                    )

                    calibration_mm = gr.Number(
                        label="Known Dimension (mm)",
                        value=25.4,
                        info="Known dimension of calibration object",
                    )

                model_choice = gr.Dropdown(
                    choices=["Claude 3.5 Sonnet", "Claude 3 Opus", "GPT-4 Vision"],
                    label="AI Model",
                    value="Claude 3.5 Sonnet",
                )

                analyze_btn = gr.Button("🔍 Analyze Concrete Sample", variant="primary", size="lg")

            with gr.Column(scale=1):
                gr.Markdown("### 📊 Analysis Results")

                summary_output = gr.HTML(label="Quick Summary")

                with gr.Tabs():
                    with gr.Tab("📋 Report"):
                        report_output = gr.Textbox(
                            label="Inspection Report", lines=20, max_lines=30, show_copy_button=True
                        )

                    with gr.Tab("🔧 Technical Data (JSON)"):
                        json_output = gr.Textbox(
                            label="Raw Analysis Data", lines=20, max_lines=30, show_copy_button=True
                        )

        # Examples
        gr.Markdown("### 📚 Example Usage")
        gr.Markdown(
            """
        **Typical Workflow:**
        1. Take a photo of the concrete sample with a ruler or coin for scale
        2. Upload the image above
        3. Enter the known dimension of your calibration object
        4. Click "Analyze Concrete Sample"
        5. Review the measurements and download the report

        **Crack Classifications:**
        - **Hair crack:** < 0.1 mm (Minimal concern, monitor)
        - **Fine crack:** 0.1-0.3 mm (Low severity, document)
        - **Medium crack:** 0.3-1.0 mm (Moderate, repair recommended)
        - **Wide crack:** 1.0-3.0 mm (High severity, repair required)
        - **Severe crack:** > 3.0 mm (Critical, immediate attention needed)
        """
        )

        # Connect button
        analyze_btn.click(
            fn=analyze_concrete_image,
            inputs=[image_input, calibration_mm, calibration_type, project_name, sample_id, model_choice],
            outputs=[json_output, report_output, summary_output],
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(share=False, server_name="0.0.0.0", server_port=7860)
