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


def generate_docker_commands(image_name, env_vars):
    """Generates Docker build and run commands with specified environment variables."""
    # Generate Docker build command
    build_command = f"docker build -t {image_name} ."

    # Convert environment variables to Docker run command options
    env_options = " ".join([f"-e {key}='{value}'" for key, value in env_vars.items()])

    # Generate Docker run command
    run_command = f"docker run --rm -d {env_options} -p 8080:8080 {image_name}"

    return build_command, run_command


def main():
    # Docker image name
    image_name = 'hasura-bots-bot:latest'
    # Path to your .env file
    env_file_path = '../.env'

    # Read environment variables from .env file
    env_vars = read_env_file(env_file_path)

    # Generate the Docker build and run commands
    build_command, run_command = generate_docker_commands(image_name, env_vars)

    # Print the commands
    print("Run the following commands to build and run your Docker container:")
    print(build_command)
    print(run_command)


if __name__ == '__main__':
    main()
