import os


def create_markdown_with_files(prefix="prefix_", markdown_file_name="all_python_files.md"):
    # Path for the Markdown file
    markdown_path = os.path.join("..", markdown_file_name)

    skip_directories = ['venv']  # Directories to skip

    with open(markdown_path, 'w', encoding='utf-8') as markdown_file:
        for root, dirs, files in os.walk(".."):
            # Modify dirs in-place to skip specific directories
            dirs[:] = [d for d in dirs if d not in skip_directories]

            # Filter to only include .py files
            py_files = [f for f in files if f.endswith('.py')]

            for file in py_files:
                file_path = os.path.join(root, file)
                # Write the file name as a heading in the Markdown file
                markdown_file.write(f"## {prefix}{file_path[2:]}\n\n")  # Remove "./" from the start
                # Write the content of the .py file in a code block
                markdown_file.write("```python\n")
                with open(file_path, 'r', encoding='utf-8') as f_read:
                    content = f_read.read()
                    markdown_file.write(content)
                markdown_file.write("\n```\n\n")


if __name__ == "__main__":
    create_markdown_with_files(prefix="hasura_discord_bot_", markdown_file_name="../hasura_discord_bot.md")
