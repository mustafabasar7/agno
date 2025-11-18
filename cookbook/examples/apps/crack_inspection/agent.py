"""Concrete Crack Width Measurement Agent.

This agent uses computer vision to detect and measure cracks in concrete samples.
Designed for construction laboratories and building inspection reports.

Usage:
    python agent.py <image_path> [--calibration-mm <value>] [--project <name>] [--sample-id <id>]

Example:
    python agent.py concrete_sample.jpg --calibration-mm 25.4 --project "Building A" --sample-id "S-001"
"""

import json
from pathlib import Path
from typing import Optional
from agno.agent import Agent, RunResponse
from agno.media import Image
from agno.models.anthropic import Claude
from agno.models.openai import OpenAIChat
from agno.tools.crack_detection import CrackDetectionTools
from pydantic import BaseModel, Field


class CrackMeasurement(BaseModel):
    """Structured output for crack measurements."""

    cracks_detected: bool = Field(..., description="Whether cracks were detected in the image")
    crack_count: int = Field(..., description="Number of distinct cracks identified")
    crack_descriptions: list[str] = Field(..., description="List of descriptions for each crack")
    calibration_object_detected: bool = Field(
        ..., description="Whether a calibration reference was found"
    )
    calibration_object_type: Optional[str] = Field(
        None, description="Type of calibration object (ruler, coin, etc.)"
    )
    reference_dimension_pixels: Optional[float] = Field(
        None, description="Measured dimension of reference object in pixels"
    )
    crack_widths_pixels: list[float] = Field(
        default_factory=list, description="Estimated crack widths in pixels"
    )
    crack_widths_mm: list[float] = Field(default_factory=list, description="Crack widths in millimeters")
    crack_classifications: list[str] = Field(
        default_factory=list, description="Classification for each crack (hair, fine, medium, wide, severe)"
    )
    severity_assessment: str = Field(..., description="Overall severity assessment")
    recommendations: list[str] = Field(
        default_factory=list, description="Recommended actions based on findings"
    )


class CrackInspectionAgent:
    """Agent for detecting and measuring cracks in concrete samples."""

    def __init__(
        self,
        model: str = "claude-3-7-sonnet-latest",
        use_openai: bool = False,
        structured_output: bool = True,
    ):
        """Initialize the crack inspection agent.

        Args:
            model: Model ID to use (default: Claude 3.5 Sonnet)
            use_openai: Use OpenAI GPT-4 Vision instead of Claude
            structured_output: Enable structured output mode
        """
        # Select model
        if use_openai:
            agent_model = OpenAIChat(id="gpt-4o")
        else:
            agent_model = Claude(id=model)

        # Create agent with crack detection tools
        self.agent = Agent(
            name="Crack Inspector",
            model=agent_model,
            tools=[CrackDetectionTools()],
            markdown=True,
            show_tool_calls=True,
            instructions=[
                "You are an expert in concrete inspection and crack analysis.",
                "Analyze images of concrete samples to detect and measure cracks.",
                "Always look for calibration references (rulers, coins, markers) in images.",
                "Provide accurate measurements in millimeters.",
                "Follow construction industry standards for crack classification.",
                "Be thorough and professional in your analysis.",
            ],
            # Enable structured output if requested
            response_model=CrackMeasurement if structured_output else None,
        )

        self.structured_output = structured_output

    def analyze_image(
        self,
        image_path: str,
        calibration_mm: Optional[float] = None,
        project_name: str = "Inspection Project",
        sample_id: str = "SAMPLE-001",
    ) -> dict:
        """Analyze a concrete sample image for cracks.

        Args:
            image_path: Path to the concrete sample image
            calibration_mm: Known dimension in mm for calibration (if reference object present)
            project_name: Name of the construction project
            sample_id: Unique sample identifier

        Returns:
            Dictionary with analysis results and measurements
        """
        # Load image
        img_path = Path(image_path)
        if not img_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Prepare analysis prompt
        prompt_parts = [
            "Analyze this concrete sample image for cracks and defects.",
            "",
            "ANALYSIS STEPS:",
            "1. First, carefully examine the entire image for any cracks, fissures, or surface defects",
            "2. Look for calibration references (ruler, coin, measuring tape, or any object with known dimensions)",
            "3. For each crack detected:",
            "   - Describe its location and pattern",
            "   - Estimate its width in pixels relative to the image",
            "4. If a calibration reference is found:",
            "   - Identify what it is",
            "   - Measure its dimension in pixels",
            "5. Use the tools provided to:",
            "   - Calculate calibration factor if reference is available",
            "   - Measure crack widths in millimeters",
            "   - Generate inspection report",
            "",
            "IMPORTANT: Be precise and methodical. Provide specific pixel measurements.",
        ]

        if calibration_mm:
            prompt_parts.extend(
                [
                    "",
                    f"CALIBRATION INFO: Reference object has known dimension of {calibration_mm} mm",
                ]
            )

        prompt = "\n".join(prompt_parts)

        # Run analysis
        response: RunResponse = self.agent.run(prompt, images=[Image(filepath=img_path)])

        # Extract results
        if self.structured_output and response.content:
            # Structured output mode
            if isinstance(response.content, CrackMeasurement):
                result = response.content.model_dump()
            else:
                result = response.content
        else:
            # Regular mode - parse from response
            result = {
                "response_text": response.content,
                "messages": [msg.model_dump() if hasattr(msg, "model_dump") else str(msg) for msg in response.messages],
            }

        # Add metadata
        result["image_path"] = str(img_path)
        result["project_name"] = project_name
        result["sample_id"] = sample_id

        return result

    def generate_report(self, analysis_results: dict) -> str:
        """Generate a formatted inspection report.

        Args:
            analysis_results: Results from analyze_image()

        Returns:
            Formatted report string
        """
        # Use the agent to generate report
        measurements_json = json.dumps(
            {k: v for k, v in analysis_results.items() if k not in ["response_text", "messages"]}, indent=2
        )

        report_prompt = f"""Generate an inspection report with this data:
Project: {analysis_results.get('project_name', 'N/A')}
Sample ID: {analysis_results.get('sample_id', 'N/A')}
Measurements: {measurements_json}
"""

        response = self.agent.run(report_prompt)
        return response.content if isinstance(response.content, str) else str(response.content)


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Concrete Crack Width Measurement Agent")
    parser.add_argument("image", help="Path to concrete sample image")
    parser.add_argument("--calibration-mm", type=float, help="Known dimension in mm for calibration")
    parser.add_argument("--project", default="Inspection Project", help="Project name")
    parser.add_argument("--sample-id", default="SAMPLE-001", help="Sample identifier")
    parser.add_argument("--use-openai", action="store_true", help="Use GPT-4 Vision instead of Claude")
    parser.add_argument("--model", default="claude-3-7-sonnet-latest", help="Model ID to use")
    parser.add_argument("--no-structured", action="store_true", help="Disable structured output")

    args = parser.parse_args()

    # Create agent
    agent = CrackInspectionAgent(
        model=args.model, use_openai=args.use_openai, structured_output=not args.no_structured
    )

    # Analyze image
    print(f"\n{'='*70}")
    print("CONCRETE CRACK INSPECTION - ANALYSIS IN PROGRESS")
    print(f"{'='*70}\n")

    results = agent.analyze_image(
        image_path=args.image,
        calibration_mm=args.calibration_mm,
        project_name=args.project,
        sample_id=args.sample_id,
    )

    # Display results
    print(f"\n{'='*70}")
    print("ANALYSIS RESULTS")
    print(f"{'='*70}\n")
    print(json.dumps(results, indent=2))

    # Generate report
    print(f"\n{'='*70}")
    print("GENERATING INSPECTION REPORT")
    print(f"{'='*70}\n")

    report = agent.generate_report(results)
    print(report)


if __name__ == "__main__":
    main()
