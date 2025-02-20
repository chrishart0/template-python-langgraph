from pathlib import Path
from rich.console import Console
from rich.text import Text

from template_langgraph_project.helpers.logger_helper import get_logger

logger = get_logger()

console = Console()


def save_graph_visualization(
    graph,
    output_dir: str = "outputs",
    source_file: str = None,
    draw_ascii_mode: bool = True,
):
    """
    Saves a Mermaid visualization of a LangGraph to a markdown file.

    Args:
        graph: The compiled LangGraph object.
        output_dir (str): Directory to save the visualization (default: "output").
        source_file (str): Source file path to use for naming the output (default: None).
        draw_ascii_mode (bool): Whether to draw the graph in ASCII mode (default: True).

    Example:
        ...
        graph = graph_builder.compile(checkpointer=memory)
        save_graph_visualization(graph, source_file="Basic_LangGraph_Project/main.py")
    """
    try:
        # Get the Mermaid diagram source
        graph_source = graph.get_graph()
        mermaid_source = graph_source.draw_mermaid()

        if draw_ascii_mode:
            logger.info("\n" + graph_source.draw_ascii())

        # Create markdown content with the mermaid diagram
        markdown_content = f"""# LangGraph Visualization

```mermaid
{mermaid_source}
```
"""
        # Save to a markdown file in the output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Generate file name based on source file if provided
        if source_file:
            base_name = Path(source_file).stem
            file_path = output_path / f"graph_{base_name}.md"
        else:
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
