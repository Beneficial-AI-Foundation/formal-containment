import re
from xml.etree import ElementTree as ET


def sanitize_xml_content(xml_string: str) -> str:
    """
    Sanitize XML content by replacing problematic characters.
    Preserves existing valid XML entities.

    Args:
        xml_string: String containing XML content with potential issues

    Returns:
        Sanitized XML string with problematic characters replaced
    """
    # First, temporarily replace valid XML entities
    placeholders = {
        "&amp;": "___AMP___",
        "&lt;": "___LT___",
        "&gt;": "___GT___",
        "&apos;": "___APOS___",
        "&quot;": "___QUOT___",
    }

    for entity, placeholder in placeholders.items():
        xml_string = xml_string.replace(entity, placeholder)

    # Replace problematic characters that might appear in LLM outputs
    replacements = {
        # Basic XML special characters
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        "'": "&apos;",
        '"': "&quot;",
        # Common problematic characters in code or math notation
        "`": "&#96;",  # Backticks often used in markdown
        "\\": "&#92;",  # Backslashes in code snippets
        "{": "&#123;",  # Curly braces in code
        "}": "&#125;",
        # Control characters that are invalid in XML
        "\u0000": "",  # Null byte - simply remove
        "\u0001": "",  # Start of heading
        "\u0002": "",  # Start of text
        "\u0003": "",  # End of text
        "\u0004": "",  # End of transmission
        "\u0005": "",  # Enquiry
        "\u0006": "",  # Acknowledge
        "\u0007": "",  # Bell
        "\u0008": "",  # Backspace
        "\u000b": "",  # Vertical tab
        "\u000c": "",  # Form feed
        "\u000e": "",  # Shift out
        "\u000f": "",  # Shift in
        "\u0010": "",  # Data link escape
        "\u0011": "",  # Device control 1
        "\u0012": "",  # Device control 2
        "\u0013": "",  # Device control 3
        "\u0014": "",  # Device control 4
        "\u0015": "",  # Negative acknowledge
        "\u0016": "",  # Synchronous idle
        "\u0017": "",  # End of transmission block
        "\u0018": "",  # Cancel
        "\u0019": "",  # End of medium
        "\u001a": "",  # Substitute
        "\u001b": "",  # Escape
        "\u001c": "",  # File separator
        "\u001d": "",  # Group separator
        "\u001e": "",  # Record separator
        "\u001f": "",  # Unit separator
        "\u007f": "",  # Delete
    }

    # Apply replacements
    for char, replacement in replacements.items():
        xml_string = xml_string.replace(char, replacement)

    # Restore valid XML entities
    for entity, placeholder in placeholders.items():
        xml_string = xml_string.replace(placeholder, entity)

    return xml_string


def parse_xml(xml_string: str) -> ET.Element:
    """
    Parse XML string from language model output in a robust way.
    Attempts to fix common XML issues before parsing.

    Args:
        xml_string: A string that should contain valid XML

    Returns:
        The parsed XML as an ElementTree Element

    Raises:
        ET.ParseError: If the XML cannot be parsed even after cleanup
    """
    # Ensure we're working with a string
    xml_string = str(xml_string)

    # 0. Try parsing without modifications first (fastest path)
    try:
        return ET.fromstring(xml_string)
    except ET.ParseError:
        # Continue with fixes if direct parsing fails
        pass

    # 1. Check if we have a root element, add one if missing
    root_pattern = re.compile(r"^\s*<[^>?!]+>.*</[^>]+>\s*$", re.DOTALL)
    if not root_pattern.match(xml_string):
        xml_string = f"<root>{xml_string}</root>"

    # 2. Handle problematic characters
    xml_string = sanitize_xml_content(xml_string)

    # 3. Remove XML declaration if present but malformed
    xml_string = re.sub(r"<\?xml[^>]*\?>", "", xml_string)

    # 4. Wrap pre-formatted or code blocks in CDATA
    # Look for common code patterns and wrap in CDATA
    code_pattern = re.compile(
        r"((?:^|\n)[ \t]*(?:def|class|if|for|while|import|from|print)\s+[^\n]+(?:\n[ \t]+[^\n]+)*)",
        re.MULTILINE,
    )
    xml_string = code_pattern.sub(r"<![CDATA[\1]]>", xml_string)

    # 5. Handle invalid tag names (replace with valid names)
    def sanitize_tag_name(match):
        full_tag = match.group(0)
        tag_name = match.group(2)
        # Replace invalid characters in tag names
        sanitized = re.sub(r"[^a-zA-Z0-9_:-]", "_", tag_name)
        return full_tag.replace(tag_name, sanitized)

    xml_string = re.sub(r"<(/?)([^ >]+)([^>]*?)(/?)>", sanitize_tag_name, xml_string)

    # 6. Attempt to find and close unclosed tags
    try:
        return ET.fromstring(xml_string)
    except ET.ParseError:
        open_tags = []
        for match in re.finditer(r"<(/?)([a-zA-Z0-9_:-]+)(?:[^>]*)(/?)>", xml_string):
            is_closing = match.group(1) == "/"
            tag_name = match.group(2)
            is_self_closing = match.group(3) == "/"

            if not is_closing and not is_self_closing:
                open_tags.append(tag_name)
            elif is_closing:
                if open_tags and open_tags[-1] == tag_name:
                    open_tags.pop()

        # Close any remaining open tags
        for tag in reversed(open_tags):
            xml_string += f"</{tag}>"

        # 7. Try one more time with cleaned content
        try:
            return ET.fromstring(xml_string)
        except ET.ParseError as e:
            # 8. Last resort: try to extract just the content between the outermost tags
            match = re.search(
                r"<([a-zA-Z0-9_:-]+)(?:[^>]*)>(.*)</\1>", xml_string, re.DOTALL
            )
            if match:
                tag_name = match.group(1)
                content = match.group(2)
                # Make one final attempt with minimized content
                try:
                    return ET.fromstring(f"<{tag_name}>{content}</{tag_name}>")
                except ET.ParseError:
                    # If still failing, wrap in CDATA as last resort
                    return ET.fromstring(
                        f"<{tag_name}><![CDATA[{content}]]></{tag_name}>"
                    )

            # If all else fails, create a minimal valid XML with the error message
            error_msg = str(e)
            return ET.fromstring(f"<error>Failed to parse XML: {error_msg}</error>")
