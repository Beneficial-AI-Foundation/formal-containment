import re
from xml.etree import ElementTree as ET


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

    # 1. Check if we have a root element, add one if missing
    root_pattern = re.compile(r"^\s*<[^>?!]+>.*</[^>]+>\s*$", re.DOTALL)
    if not root_pattern.match(xml_string):
        xml_string = f"<root>{xml_string}</root>"

    # 2. Try to fix unclosed tags by removing problematic content
    try:
        return ET.fromstring(xml_string)
    except ET.ParseError:
        # 3. Clean up common issues
        # Remove XML declaration if present but malformed
        xml_string = re.sub(r"<\?xml[^>]*\?>", "", xml_string)

        # 4. Try to handle unescaped special characters in content
        xml_string = xml_string.replace("&", "&amp;")
        # But don't double-escape existing entities
        xml_string = re.sub(r"&amp;(amp|lt|gt|apos|quot);", r"&\1;", xml_string)

        # 5. Attempt to find and close unclosed tags
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

        # 6. Last attempt to parse
        try:
            return ET.fromstring(xml_string)
        except ET.ParseError as e:
            # 7. If all else fails, extract content between outermost tags
            # This is a fallback that tries to salvage something
            match = re.search(
                r"<([a-zA-Z0-9_:-]+)(?:[^>]*)>(.*)</\1>", xml_string, re.DOTALL
            )
            if match:
                tag_name = match.group(1)
                content = match.group(2)
                return ET.fromstring(f"<{tag_name}>{content}</{tag_name}>")
            # Re-raise the original error if we couldn't fix it
            raise e
