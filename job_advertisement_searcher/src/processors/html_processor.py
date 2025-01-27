import html2text
import pandas as pd

class HTMLProcessor:
    """Handles HTML to markdown conversion."""
    def __init__(self):
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = False
        self.converter.ignore_images = True
        self.converter.ignore_tables = False

    def to_markdown(self, html_content: str) -> str:
        """Convert HTML content to markdown format."""
        if pd.isna(html_content):
            return ""
        return self.converter.handle(str(html_content)) 