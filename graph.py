import os
import sys
import subprocess
from pyvis.network import Network
from tkinter import Tk, filedialog

def get_tags(file_path):
    """Get tags for a file using the tag command line tool."""
    tag_cmd = ["tag", "--list", file_path]
    result = subprocess.run(tag_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Failed to get tags for {file_path}: {result.stderr}")
        return []
    tags_str = result.stdout.replace(file_path,"").strip()
    # Split the tags_str based on the first occurrence of multiple spaces
    tags = [tag.strip() for tag in tags_str.split(",")] if tags_str else []
    if len(tags) > 0:
        print(f"Retrieved Finder tags for {file_path}: {', '.join(tags)}")
    else:
        print(f"No Finder tags found for {file_path}")
    return tags

def build_files_tags(folder_path):
    """Build the files_tags dictionary by recursively visiting all files and sub-folders."""
    files_tags = {}
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            # Check if it's actually a file
            if not os.path.isfile(file_path):
                continue
            
            # Skip hidden files and non-supported files
            if file_name.startswith("._") or not file_name.endswith((".pdf", ".txt", ".mp4", ".mkv", ".webm")):
                continue
            
            tags = get_tags(file_path)
            if len(tags) > 0:
                files_tags[file_name] = tags
                print(f"Added tags for {file_name}: {tags}")  # Debugging print statement
            else:
                print(f"No tags found for {file_name}")  # Debugging print statement
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
        net.add_node(file, label=file, color="blue", shape="box", node_type = "file")
        for tag in tags:
            # Add tag node (shape: ellipse, if not already added)
            if tag not in net.node_map:
                net.add_node(tag, label=tag, color="green", shape="ellipse", node_type = "tag")
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
                        node.setOptions({color: 'orange'});
                    } else {
                        node.setOptions({color: 'grey'});
                    }
                }
            }
        }
    }

    function unhighlightConnectedNodes() {
        var allNodes = network.body.nodes;
        for (var nodeId in allNodes) {
            if (allNodes.hasOwnProperty(nodeId)) {
                var node = allNodes[nodeId];
                if (node.options.node_type === "file") {
                    node.setOptions({color: "blue"});
                } else if (node.options.node_type === "tag") {
                    node.setOptions({color: "green"});
                }
            }
        }
    }
    
    network.on('click', function(params) {
        if (params.nodes.length === 0) {
            unhighlightConnectedNodes();
        } else {
            highlightConnectedNodes(params);
        }
    });
    
    // Store the original colors of all nodes after the graph is created
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
        sys.exit(0) # Exit with status code 0 indicating success
    except Exception as e:
        print(f"Failed to open tags_graph.html in web browser: {e}")
        sys.exit(1)  # Exit with status code 1 indicating an error
