"""Simple example of using the Crack Inspection Agent.

This script demonstrates basic usage without requiring actual images.
For production use, replace with real concrete sample images.
"""

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.crack_detection import CrackDetectionTools


def main():
    """Run a simple crack detection workflow."""

    print("=" * 70)
    print("Concrete Crack Detection - Simple Example")
    print("=" * 70)
    print()

    # Create agent with crack detection tools
    agent = Agent(
        name="Crack Inspector",
        model=Claude(id="claude-3-7-sonnet-latest"),
        tools=[CrackDetectionTools()],
        markdown=True,
        show_tool_calls=True,
        instructions=[
            "You are an expert in concrete inspection.",
            "Help analyze crack measurements and generate reports.",
        ],
    )

    # Example 1: Calibration calculation
    print("\n" + "=" * 70)
    print("Example 1: Calculate Calibration Factor")
    print("=" * 70)
    print()

    response = agent.run(
        """I have a concrete image with a ruler in it.
        The ruler shows 1 inch (25.4mm) and measures 127 pixels in the image.
        Calculate the calibration factor."""
    )

    print("\n" + "-" * 70)
    print("Example 2: Measure Crack Width")
    print("-" * 70)
    print()

    response = agent.run(
        """Using the calibration factor from the previous calculation,
        I have a crack that measures 15 pixels wide.
        Calculate the crack width in millimeters and classify its severity."""
    )

    print("\n" + "-" * 70)
    print("Example 3: Generate Inspection Report")
    print("-" * 70)
    print()

    response = agent.run(
        """Generate an inspection report with the following data:
        - Project: Bridge Rehabilitation Project
        - Sample ID: PIER-A-001
        - Crack Width: 2.5 mm
        - Classification: Wide crack
        - Severity: High
        - Location: Pier A, west face, 1.2m from base
        """
    )

    print("\n" + "=" * 70)
    print("Example Complete!")
    print("=" * 70)
    print("\nFor image-based analysis, use agent.py or app.py")
    print()


if __name__ == "__main__":
    main()
