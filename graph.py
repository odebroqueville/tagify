import os
import sys
import subprocess
from pyvis.network import Network
from tkinter import Tk, filedialog

def get_tags(file_path):
    """Get tags for a file using the tag command line tool."""
    tag_cmd = ["tag", "--list", file_path]
    print(f"Running command: {' '.join(tag_cmd)}")  # Debugging print statement
    result = subprocess.run(tag_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Failed to get tags for {file_path}: {result.stderr}")
        return []
    tags_str = result.stdout.strip()
    print(f"Command output: {tags_str}")  # Debugging print statement
    tags_lines = tags_str.split("\t")
    if len(tags_lines) > 1:
        tags = tags_lines[1].split(",")
        return [tag.strip() for tag in tags]
    return []

def build_files_tags(folder_path):
    """Build the files_tags dictionary by recursively visiting all files and sub-folders."""
    files_tags = {}
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            print(f"Processing file: {file_name}")  # Debugging print statement
            if file_name.endswith(("_tagged.pdf", "_tagged.txt", "_tagged.mp4", "_tagged.mkv", "_tagged.webm")):
                file_path = os.path.join(root, file_name)
                tags = get_tags(file_path)
                if tags:
                    files_tags[file_name] = tags
                    print(f"Added tags for {file_name}: {tags}")  # Debugging print statement
                else:
                    print(f"No tags found for {file_name}")  # Debugging print statement
            else:
                print(f"Skipped file: {file_name}")  # Debugging print statement
    return files_tags

if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
    else:
        # Prompt the user to select a folder if no folder path is provided
        root = Tk()
        root.withdraw()  # Hide the root window
        folder_path = filedialog.askdirectory(title="Select Folder Containing Files to Tag")
        if not folder_path:
            print("No folder path provided.")
            sys.exit()

    print(f"Selected folder: {folder_path}")

    files_tags = build_files_tags(folder_path)
    print(f"Files and tags: {files_tags}")

    # Initialize a PyVis Network object
    net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")

    # Add nodes and edges
    for file, tags in files_tags.items():
        # Add file node (shape: rectangle)
        net.add_node(file, label=file, color="blue", shape="rectangle")
        for tag in tags:
            # Add tag node (shape: ellipse, if not already added)
            if tag not in net.node_map:
                net.add_node(tag, label=tag, color="green", shape="ellipse")
            # Add edge between file and tag
            net.add_edge(file, tag)

    # Generate the network graph HTML
    net.write_html("tags_graph.html")
    print("Generated tags_graph.html")

    # Add custom JavaScript for interactivity
    with open("tags_graph.html", "r") as file:
        html_content = file.read()

    custom_js = """
    <script type="text/javascript">
    function highlightConnectedNodes(params) {
        if (params.nodes.length > 0) {
            var selectedNode = params.nodes[0];
            var connectedNodes = network.getConnectedNodes(selectedNode);
            var secondLevelNodes = [];
            connectedNodes.forEach(function(node) {
                secondLevelNodes = secondLevelNodes.concat(network.getConnectedNodes(node));
            });

            var allNodes = network.body.nodes;
            for (var nodeId in allNodes) {
                if (allNodes.hasOwnProperty(nodeId)) {
                    var node = allNodes[nodeId];
                    if (nodeId == selectedNode || connectedNodes.includes(nodeId) || secondLevelNodes.includes(nodeId)) {
                        node.setOptions({color: 'red'});
                    } else {
                        node.setOptions({color: 'grey'});
                    }
                }
            }
        }
    }
    network.on('click', highlightConnectedNodes);
    </script>
    """

    # Insert the custom JavaScript before the closing </body> tag
    html_content = html_content.replace("</body>", custom_js + "</body>")

    with open("tags_graph.html", "w") as file:
        file.write(html_content)
    print("Updated tags_graph.html with custom JavaScript")

    # Open the generated HTML file in the default web browser
    try:
        # Use os.system to open the file with the default application
        os.system("open tags_graph.html")
        print("Opened tags_graph.html in web browser")
    except Exception as e:
        print(f"Failed to open tags_graph.html in web browser: {e}")
