def read_env_file(file_path):
    """Reads an .env file and returns a dictionary of environment variables."""
    env_vars = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key] = value
    return env_vars


def generate_docker_commands(project_id, image_name, env_vars):
    """Generates Docker build, push, and run commands with specified environment variables."""
    # Tag image for Google Container Registry
    gcr_image_name = f"gcr.io/{project_id}/{image_name}"

    # Generate Docker build command
    build_command = f"docker build -t {gcr_image_name} ."

    # Generate Docker push command
    push_command = f"docker push {gcr_image_name}"

    # Convert environment variables to Docker run command options
    env_options = " ".join([f"-e {key}='{value}'" for key, value in env_vars.items()])

    # Generate Docker run command for local testing (optional)
    run_command = f"docker run --rm {env_options} {gcr_image_name}"

    return build_command, push_command, run_command


def main():
    # Google Cloud Project ID
    project_id = 'hasura-bots'
    # Docker image name
    image_name = 'hasura-bots-bot:latest'
    # Path to your .env file
    env_file_path = '../.env'

    # Read environment variables from .env file
    env_vars = read_env_file(env_file_path)

    # Generate the Docker build, push, and run commands
    build_command, push_command, run_command = generate_docker_commands(project_id, image_name, env_vars)

    # Print the commands
    print("Run the following commands to build, push, and optionally run your Docker container locally:")
    print(build_command)
    print(f"docker buildx build --platform linux/amd64,linux/arm64 -t gcr.io/{project_id}/{image_name} --push .")
    print(push_command)
    print(run_command)


if __name__ == '__main__':
    main()
