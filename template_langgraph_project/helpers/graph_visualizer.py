from pathlib import Path
from rich.console import Console
from rich.text import Text

console = Console()


def save_graph_visualization(graph, output_dir: str = "output"):
    """
    Saves a Mermaid visualization of a LangGraph to a markdown file.

    Args:
        graph: The compiled LangGraph object.
        output_dir (str): Directory to save the visualization (default: "output").
    """
    try:
        # Get the Mermaid diagram source
        mermaid_source = graph.get_graph().draw_mermaid()

        # Create markdown content with the mermaid diagram
        markdown_content = f"""# LangGraph Visualization

```mermaid
{mermaid_source}
```
"""
        # Save to a markdown file in the output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        file_path = output_path / "graph.md"
        with open(file_path, "w") as f:
            f.write(markdown_content)

        console.print(
            Text(f"\nGraph visualization saved to {file_path}", style="bold green")
        )
        console.print(
            Text(
                "Open in VSCode and press Ctrl+Shift+V (Cmd+Shift+V on Mac) to preview\n",
                style="bold blue",
            )
        )
    except Exception as e:
        console.print(
            Text(f"Could not generate graph visualization: {e}", style="bold red")
        )
