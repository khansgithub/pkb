import json
import unittest

from app import exceptions
from app.markdown import ParseMarkdown


class TestMarkdown(unittest.TestCase):

    def setUp(self) -> None:
        self.test_cases = [
            {
                "name": "Simple nested headings",
                "input": ["# Title", "## Subtitle", "Some text here."],
                "expected": {"Title": [{"Subtitle": ["Some text here."]}]},
            },
            {
                "name": "Skipped heading level",
                "input": [
                    "# Main",
                    "### Skipped level heading",
                    "Content after a skipped heading level.",
                ],
                "expected": {
                    "Main": [
                        {
                            "_": [
                                {
                                    "Skipped level heading": [
                                        "Content after a skipped heading level."
                                    ]
                                }
                            ]
                        }
                    ]
                },
            },
            {
                "name": "Multiple top-level sections",
                "input": [
                    "# First Section",
                    "Content of the first section.",
                    "# Second Section",
                    "Content of the second section.",
                ],
                "expected": {
                    "First Section": ["Content of the first section."],
                    "Second Section": ["Content of the second section."],
                },
            },
            {
                "name": "Deep nested headings",
                "input": [
                    "# Root",
                    "## Branch",
                    "### Leaf",
                    "Details at the deepest heading.",
                ],
                "expected": {
                    "Root": [
                        {"Branch": [{"Leaf": ["Details at the deepest heading."]}]}
                    ]
                },
            },
            {
                "name": "Headings with bullets",
                "input": [
                    "# Introduction",
                    "This is an intro paragraph.",
                    "## Details",
                    "- Bullet point one",
                    "- Bullet point two",
                    "## Conclusion",
                    "Some final thoughts.",
                ],
                "expected": {
                    "Introduction": [
                        "This is an intro paragraph.",
                        {"Details": ["- Bullet point one", "- Bullet point two"]},
                        {"Conclusion": ["Some final thoughts."]},
                    ]
                },
            },
            {
                "name": "Single section",
                "input": ["# Section", "Some text."],
                "expected": {"Section": ["Some text."]},
            },
            {
                "name": "Formatted headings",
                "input": [
                    "# **Bold** Title",
                    "## Subtitle with *italics*",
                    "Paragraph under formatted headings.",
                ],
                "expected": {
                    "**Bold** Title": [
                        {
                            "Subtitle with *italics*": [
                                "Paragraph under formatted headings."
                            ]
                        }
                    ]
                },
            },
            {
                "name": "Missing H1 heading",
                "input": ["## Subsection", "This file starts with an H2 heading."],
                "expected_exception": exceptions.MissingHeadingOne,
            },
            {
                "name": "Code block",
                "input": [
                    "# Code Example",
                    "```python",
                    'print("Hello, world!")',
                    "```",
                ],
                "expected": {"Code Example": [["python", 'print("Hello, world!")']]},
            },
            {
                "name": "Heading with special characters",
                "input": [
                    "# What's New?",
                    "## v1.0: Initial Release",
                    "Details about the release.",
                ],
                "expected": {
                    "What's New?": [
                        {"v1.0: Initial Release": ["Details about the release."]}
                    ]
                },
            },
        ]

    def test_markdown_parsing(self):
        for case in self.test_cases:
            text = "\n".join(case["input"])
            parser = ParseMarkdown(text)
            expected_exception = case.get("expected_exception", None)

            with self.subTest(case=case["name"]):
                if expected_exception:
                    with self.assertRaises(expected_exception):
                        parser.parse_markdown()
                else:
                    result = parser.parse_markdown()
                    # Compare JSON string representations for consistent formatting
                    self.assertEqual(json.dumps(result), json.dumps(case["expected"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
